import asyncio
import logging

from client.client.config.config_loader import ClientConfigLoader
from client.client.network.client_connection_manager import ClientConnectionManager
from client.client.network.client_tcp_server import ClientTCPServer
from client.client.network.udp_broadcaster import UDPBroadcaster
from shared.encryption.encryption_manager import EncryptionManager


async def main():
    encryption_manager = EncryptionManager()
    config_loader = ClientConfigLoader(encryption_manager)
    config = config_loader.load_config()

    logging.basicConfig(encoding='utf-8', level=config.log_level)

    tcp_server = ClientTCPServer(config.tcp_server_port)
    udp_broadcaster = UDPBroadcaster(config.udp_broadcast_port, f'{{"port": {config.tcp_server_port}}}'.encode("utf-8"))
    connection_manager = ClientConnectionManager(udp_broadcaster, tcp_server)
    await connection_manager.start()
    loop = asyncio.get_event_loop()
    await loop.create_future()


asyncio.run(main())
