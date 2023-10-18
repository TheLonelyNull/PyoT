import asyncio
import logging
from asyncio import Protocol, BaseTransport
from typing import Callable

from server.network.server_authentication_manager import ServerAuthenticationManager, RejectConnectionCommand, \
    AcceptMessageCommand, MarkClientAsAuthenticatedCommand, RespondToChallengeCommand
from server.network.server_encryption_manager import ServerEncryptionManager

LOGGER = logging.getLogger(__name__)


class TCPClient:
    def __init__(self, host: str, port: int, server_authentication_manager: ServerAuthenticationManager,
                 server_encryption_manager: ServerEncryptionManager):
        self._host = host
        self._port = port
        self._server_authentication_manager = server_authentication_manager
        self._server_encryption_manager = server_encryption_manager

        self._on_connected_callbacks = []
        self._on_disconnected_callbacks = []
        self._on_received_callbacks = []
        self._transport = None

    async def start(self):
        loop = asyncio.get_running_loop()
        self._transport, _ = await loop.create_connection(lambda: _TCPClientProtocol(
            self._on_connect_wrapper,
            self._on_disconnect_wrapper,
            self._on_data_received_wrapper
        ), self._host, self._port)

    async def stop(self):
        self._transport: BaseTransport
        if self._transport:
            self._transport.close()

    def _on_connect_wrapper(self, transport: BaseTransport):
        # Send client the server's public key, to start the authentication handshake.
        self._transport = transport
        self._transport.write(self._server_encryption_manager.get_server_public_key().save_pkcs1())
        self._server_authentication_manager.mark_public_key_as_shared()

    def _on_disconnect_wrapper(self):
        LOGGER.debug("Peer disconnected.")
        self._transport = None

        if self._server_authentication_manager.is_client_authenticated():
            for callback in self._on_disconnected_callbacks:
                callback()

    def _on_data_received_wrapper(self, data: bytes):
        LOGGER.debug(f"Received data: {data}")

        authentication_command = self._server_authentication_manager.authenticate_server_message(data)
        if isinstance(authentication_command, RejectConnectionCommand):
            self._transport.close()
            return

        if isinstance(authentication_command, RespondToChallengeCommand):
            self._transport.write(authentication_command.signed_challenge)
            return

        # Only notify connection callbacks on challenge success.
        if isinstance(authentication_command, MarkClientAsAuthenticatedCommand):
            LOGGER.debug(f"Client Authenticated")
            for callback in self._on_connected_callbacks:
                callback(self._transport)
            return

        # Only notify data callbacks once authenticated.
        if isinstance(authentication_command, AcceptMessageCommand):
            decrypted_data = self._server_encryption_manager.decrypt_payload_from_client(data)
            # Decrypt Payload
            for callback in self._on_received_callbacks:
                callback(decrypted_data)

    def register_connection_callback(self, callback: Callable[[BaseTransport], None]):
        self._on_connected_callbacks.append(callback)

    def register_disconnection_callback(self, callback: Callable[[], None]):
        self._on_disconnected_callbacks.append(callback)

    def register_on_data_received_callback(self, callback: Callable[[bytes], None]):
        self._on_received_callbacks.append(callback)

    def write(self, message: bytes):
        self._transport.write(message)


class _TCPClientProtocol(Protocol):
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
