import asyncio
import logging
from asyncio import Protocol, BaseTransport
from typing import Callable

from client.network.client_authentication_manager import ClientAuthenticationManager, RejectConnectionCommand, \
    IssueChallengeCommand, AcceptChallengeCommand, AcceptMessageCommand
from client.network.client_encryption_manager import ClientEncryptionManager

LOGGER = logging.getLogger(__name__)

AUTHENTICATION_HANDSHAKE_TIMEOUT = 1


class NoServerConnectedError(Exception):
    """Error to raise if attempt to access server is made before connection."""


class ClientTCPServer:
    def __init__(
            self,
            client_authentication_manager: ClientAuthenticationManager,
            client_encryption_manager: ClientEncryptionManager,
            port: int,
            host: str = "0.0.0.0",
            authentication_timeout: int = 5

    ):
        self._host = host
        self._port = port

        self._client_authentication_manager = client_authentication_manager
        self._client_encryption_manager = client_encryption_manager
        self._on_connected_callbacks = []
        self._on_disconnected_callbacks = []
        self._on_received_callbacks = []
        self._task = None
        self._server = None
        self._transport = None

    async def start(self):
        self._task = asyncio.create_task(self._start_server())

    async def _start_server(self):
        loop = asyncio.get_running_loop()
        LOGGER.debug(f"Starting TCP server on {self._host}:{self._port}")
        self._server = await loop.create_server(
            lambda: _TCPServerProtocol(
                self._on_connect_wrapper,
                self._on_disconnect_wrapper,
                self._on_data_received_wrapper
            ),
            self._host,
            self._port)
        LOGGER.info(f"TCP Server started on {self._host}:{self._port}")
        await self._server.serve_forever()

    async def stop(self):
        self._task.cancel()
        LOGGER.info("TCP Server stopped.")

    def _on_connect_wrapper(self, transport: BaseTransport):
        # Close the connection if no more connections are currently accepted
        if self._transport:
            LOGGER.debug(f"Got TCP connection from {transport.get_extra_info('peername')} but was full.")
            transport.close()
        else:
            LOGGER.debug(f"Got new TCP connection from {transport.get_extra_info('peername')}.")
            self._transport = transport

            # Start an event loop that checks if server is verified after a timeout and prevent hanging DDOs attacks
            # that never responds.
            loop = asyncio.get_running_loop()
            loop.call_later(5, self._handel_server_authentication_timeout)

    def _handel_server_authentication_timeout(self):
        if self._transport and not self._client_authentication_manager.is_server_authenticated():
            LOGGER.debug("Authentication handshake not completed in time. Disconnecting...")
            self._transport.close()

    def _on_disconnect_wrapper(self):
        LOGGER.debug("Peer disconnected.")
        should_callback = self._client_authentication_manager.is_server_authenticated()

        self._transport = None
        self._client_encryption_manager.reset()
        self._client_authentication_manager.reset()

        if should_callback:
            for callback in self._on_disconnected_callbacks:
                callback()

    def _on_data_received_wrapper(self, data: bytes):
        LOGGER.debug(f"Received data: {data}")

        authentication_command = self._client_authentication_manager.authenticate_server_message(data)
        if isinstance(authentication_command, RejectConnectionCommand):
            self._transport.close()
            return

        if isinstance(authentication_command, IssueChallengeCommand):
            self._transport.write(authentication_command.challenge)
            return

        # Only notify connection callbacks on challenge success.
        if isinstance(authentication_command, AcceptChallengeCommand):
            for callback in self._on_connected_callbacks:
                callback(self._transport)

            # Send server the client's public key, so it can encrypt future instructions to the
            # client.
            self._transport.write(authentication_command.client_public_key)
            return

        # Only notify data callbacks once authenticated.
        if isinstance(authentication_command, AcceptMessageCommand):
            decrypted_data = self._client_encryption_manager.decrypt_payload_from_server(data)
            # Decrypt Payload
            for callback in self._on_received_callbacks:
                callback(decrypted_data)

    def register_connection_callback(self, callback: Callable[[BaseTransport], None]):
        self._on_connected_callbacks.append(callback)

    def register_disconnection_callback(self, callback: Callable[[], None]):
        self._on_disconnected_callbacks.append(callback)

    def register_on_data_received_callback(self, callback: Callable[[bytes], None]):
        self._on_received_callbacks.append(callback)

    def write(self, payload: bytes) -> None:
        if not self._transport or not self._client_authentication_manager.is_server_authenticated():
            raise NoServerConnectedError("Data can't be written as no server is connected yet.")
        # TODO encrypt
        self._transport.write(payload)

    def disconnect(self) -> None:
        if not self._transport or not self._client_authentication_manager.is_server_authenticated():
            raise NoServerConnectedError("Can't disconnect from server is no server is connected yet.")
        self._transport.close()


class _TCPServerProtocol(Protocol):
    def __init__(self,
                 on_connected: Callable[[BaseTransport], None] | None,
                 on_disconnected: Callable[[], None] | None,
                 on_received: Callable[[bytes], None] | None):
        self._on_connected = on_connected
        self._on_disconnected = on_disconnected
        self._on_received = on_received

    def connection_made(self, transport: BaseTransport) -> None:
        if self._on_connected:
            self._on_connected(transport)

    def data_received(self, data: bytes) -> None:
        if self._on_received:
            self._on_received(data)

    def connection_lost(self, exc: Exception | None) -> None:
        if self._on_disconnected:
            self._on_disconnected()
