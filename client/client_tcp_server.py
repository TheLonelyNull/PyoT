import asyncio
import logging
from asyncio import Protocol, BaseTransport
from typing import Callable

LOGGER = logging.getLogger(__name__)


class ClientTCPServer:
    def __init__(
            self,
            port: int, host: str = "0.0.0.0"
    ):
        self._host = host
        self._port = port
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

            for callback in self._on_connected_callbacks:
                callback(transport)

    def _on_disconnect_wrapper(self):
        LOGGER.debug("Peer disconnected.")
        self._transport = None

        for callback in self._on_disconnected_callbacks:
            callback()

    def _on_data_received_wrapper(self, data: bytes):
        for callback in self._on_received_callbacks:
            callback(data)

    def register_connection_callback(self, callback: Callable[[BaseTransport], None]):
        self._on_connected_callbacks.append(callback)

    def register_disconnection_callback(self, callback: Callable[[], None]):
        self._on_disconnected_callbacks.append(callback)

    def register_on_data_received_callback(self, callback: Callable[[bytes], None]):
        self._on_received_callbacks.append(callback)


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
