import asyncio
import json
import logging
from asyncio import BaseTransport
from functools import partial
from json import JSONDecodeError

from server.tcp_client import TCPClient
from server.udp_listener import UDPListener

LOGGER = logging.getLogger(__name__)


class ServerConnectionManager:

    def __init__(self, udp_listener: UDPListener):
        self._udp_listener = udp_listener
        self._udp_listener.register_on_data_received_callback(self._udp_broadcast_received_callback)
        self._connections: dict[tuple[str, int], TCPClient] = {}

    async def start(self):
        await self._udp_listener.start()

    async def stop(self):
        await self._udp_listener.stop()
        for client in self._connections.values():
            await client.stop()

    def _udp_broadcast_received_callback(self, data: bytes, addr: tuple[str, int]):
        if addr in self._connections:
            return

        try:
            payload = json.loads(data.decode("utf-8"))
            tcp_port = payload["port"]
            client = TCPClient(host=addr[0], port=tcp_port)
            client.register_disconnection_callback(partial(self._handle_tcp_disconnection, addr))
            loop = asyncio.get_event_loop()
            loop.create_task(client.start())
            self._connections[addr] = client
        except (JSONDecodeError, KeyError) as e:
            pass

    def _handle_tcp_disconnection(self, addr: tuple[str, int]):
        LOGGER.debug(f"Removing {addr} from connections.")
        self._connections.pop(addr)
