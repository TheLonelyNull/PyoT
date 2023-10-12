import asyncio
import logging
import socket
from asyncio import DatagramTransport
from typing import Callable

LOGGER = logging.getLogger(__name__)


class UDPListener:
    def __init__(self, port: int, host: str = "0.0.0.0"):
        self._host = host
        self._port = port
        self._on_connected_callbacks = []
        self._on_received_callbacks = []
        self._task = None
        self._transport = None

    async def start(self):
        self._task = asyncio.create_task(self._start_broadcast_listener())

    async def _start_broadcast_listener(self):
        loop = asyncio.get_running_loop()

        LOGGER.debug("Starting UDP Broadcast listener.")
        self._transport, _ = await loop.create_datagram_endpoint(
            lambda: _BroadcastListenerProtocol(self._on_connect_wrapper, self._on_data_received_wrapper),
            local_addr=(self._host, self._port), reuse_port=True)
        LOGGER.info(f"Started UDP Broadcast listener on {self._host}:{self._port}")

        while True:
            await asyncio.sleep(0)

    async def stop(self):
        if self._transport:
            self._transport.close()
        self._task.cancel()
        LOGGER.info("Stopped UDP Listener.")

    def _on_connect_wrapper(self, transport: DatagramTransport):
        # Close the connection if no more connections are currently accepted
        for callback in self._on_connected_callbacks:
            callback(transport)

    def _on_data_received_wrapper(self, data: bytes, addr: tuple[str, int]):
        LOGGER.debug(f"Got UDP Datagram from {addr[0]}:{addr[1]}")
        for callback in self._on_received_callbacks:
            callback(data, addr)

    def register_connection_callback(self, callback: Callable[[DatagramTransport], None]):
        self._on_connected_callbacks.append(callback)

    def register_on_data_received_callback(self, callback: Callable[[bytes, tuple[str, int]], None]):
        self._on_received_callbacks.append(callback)


class _BroadcastListenerProtocol(asyncio.DatagramProtocol):

    def __init__(self,
                 on_connected: Callable[[DatagramTransport], None] | None,
                 on_received: Callable[[bytes, tuple[str, int]], None] | None):
        self._on_connected = on_connected
        self._on_received = on_received

        self._transport = None

    def connection_made(self, transport: DatagramTransport):
        self._transport = transport
        sock = transport.get_extra_info("socket")
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        LOGGER.debug("Listening for broadcast on socket.")
        if self._on_connected:
            self._on_connected(transport)

    def datagram_received(self, data, addr):
        """Called when some datagram is received."""
        if self._on_received:
            self._on_received(data, addr)
