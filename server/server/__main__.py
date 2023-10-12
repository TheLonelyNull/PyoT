import asyncio
import logging

from server.server.config.config_loader import ServerConfigLoader
from server.server.network.server_connection_manager import ServerConnectionManager
from server.server.network.udp_listener import UDPListener
from shared.encryption.encryption_manager import EncryptionManager


async def main():
    encryption_manager = EncryptionManager()
    config_loader = ServerConfigLoader(encryption_manager)
    config = config_loader.load_config()

    logging.basicConfig(encoding='utf-8', level=config.log_level)

    udp_listener = UDPListener(config.udp_listening_port)
    connection_manager = ServerConnectionManager(
        udp_listener
    )
    await connection_manager.start()

    loop = asyncio.get_event_loop()
    await loop.create_future()


asyncio.run(main())
