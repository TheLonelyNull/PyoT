import asyncio
import logging
from asyncio import Protocol, BaseTransport
from typing import Callable

LOGGER = logging.getLogger(__name__)


class TCPClient:
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port
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
