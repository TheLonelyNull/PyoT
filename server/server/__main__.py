import asyncio
import logging

from uvicorn import Config, Server

from api import api
from migrations.migration_client import MigrationClient
from server.config.config_loader import ServerConfigLoader
from server.network.server_connection_manager import ServerConnectionManager
from server.network.udp_listener import UDPListener
from server.utils.encryption_manager import EncryptionManager


async def main():
    # TODO make db location and name configurable
    migration_client = MigrationClient("sqlite:///pyot-server.db")
    migration_client.run_migrations()

    encryption_manager = EncryptionManager()
    config_loader = ServerConfigLoader(encryption_manager)
    config = config_loader.load_config()

    logging.basicConfig(encoding='utf-8', level=config.log_level)

    udp_listener = UDPListener(config.udp_listening_port)
    # TODO tcp client factory
    connection_manager = ServerConnectionManager(
        udp_listener,
        encryption_manager,
        config
    )
    await connection_manager.start()

    loop = asyncio.get_event_loop()
    # TODO api configurable
    api_server_config = Config(api, loop=loop, host='0.0.0.0', port=8080, workers=1)
    api_server = Server(api_server_config)
    loop.create_task(api_server.serve())

    await loop.create_future()


asyncio.run(main())
