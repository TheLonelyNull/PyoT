import asyncio
import logging
import socket
from asyncio import DatagramTransport

LOGGER = logging.getLogger(__name__)


class UDPBroadcaster:
    def __init__(self, port: int, message: bytes):
        self._port = port
        self._task = None
        self._message = message
        self._protocol = None
        self._transport = None

    async def start(self):
        self._task = asyncio.create_task(self._start_broadcast_server())

    async def _start_broadcast_server(self):
        loop = asyncio.get_running_loop()

        LOGGER.debug("Starting UDP Broadcast server.")
        self._protocol = _BroadcastProtocol(self._port, message=self._message)
        self._transport, _ = await loop.create_datagram_endpoint(
            lambda: self._protocol,
            local_addr=('0.0.0.0', self._port), reuse_port=True)
        LOGGER.info(f"UDP Broadcast started on port {self._port}")
        while True:
            await asyncio.sleep(0)

    async def stop(self):
        if self._protocol:
            self._protocol.stop_broadcast()
        if self._transport:
            self._transport.close()
        self._task.cancel()
        LOGGER.info("Stopped UDP Broadcast server.")


class _BroadcastProtocol(asyncio.DatagramProtocol):

    def __init__(self, port: int, message: bytes, delay: int = 5, loop: asyncio.AbstractEventLoop = None):
        self._port = port
        self._loop = asyncio.get_event_loop() if loop is None else loop
        self._message = message
        self._delay = delay
        self._transport = None
        self._should_broadcast = True

    def stop_broadcast(self):
        self._should_broadcast = False

    def connection_made(self, transport: DatagramTransport):
        self._transport = transport
        sock = transport.get_extra_info("socket")
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        LOGGER.debug("Started sending broadcast.")
        self._broadcast()

    def _broadcast(self):
        if self._should_broadcast:
            LOGGER.debug("Broadcasting...")
            self._transport.sendto(self._message, ("<broadcast>", self._port))
            self._loop.call_later(self._delay, self._broadcast)
