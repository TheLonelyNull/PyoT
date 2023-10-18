import asyncio
import json
import logging
from functools import partial
from json import JSONDecodeError

from server.config.config_loader import ServerConfig
from server.network.server_authentication_manager import ServerAuthenticationManager
from server.network.server_encryption_manager import ServerEncryptionManager
from server.network.tcp_client import TCPClient
from server.network.udp_listener import UDPListener
from server.utils.encryption_manager import EncryptionManager

LOGGER = logging.getLogger(__name__)


class ServerConnectionManager:

    def __init__(self, udp_listener: UDPListener, encryption_manager: EncryptionManager, config: ServerConfig):
        self._udp_listener = udp_listener
        self._encryption_manager = encryption_manager
        self._config = config
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
            server_encryption_manager = ServerEncryptionManager(self._config.private_key, self._config.public_key,
                                                                self._encryption_manager)
            server_authentication_manager = ServerAuthenticationManager(server_encryption_manager)
            client = TCPClient(addr[0], tcp_port, server_authentication_manager, server_encryption_manager)
            client.register_disconnection_callback(partial(self._handle_tcp_disconnection, addr))
            loop = asyncio.get_event_loop()
            loop.create_task(client.start())
            self._connections[addr] = client
        except (JSONDecodeError, KeyError) as e:
            pass

    # TODO, perhaps wait for authentication/abstract connection to complete?
    def _handle_successful_tcp_connection(self):
        pass

    def _handle_tcp_disconnection(self, addr: tuple[str, int]):
        LOGGER.debug(f"Removing {addr} from connections.")
        self._connections.pop(addr)
