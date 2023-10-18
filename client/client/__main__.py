import asyncio
import logging

from client.config.config_loader import ClientConfigLoader
from client.network.client_connection_manager import ClientConnectionManager
from client.network.client_encryption_manager import ClientEncryptionManager
from client.network.client_tcp_server import ClientTCPServer
from client.network.udp_broadcaster import UDPBroadcaster
from client.network.client_authentication_manager import ClientAuthenticationManager
from client.utils.encryption_manager import EncryptionManager


async def main():
    encryption_manager = EncryptionManager()
    config_loader = ClientConfigLoader(encryption_manager)
    config = config_loader.load_config()

    logging.basicConfig(encoding='utf-8', level=config.log_level)

    client_encryption_manager = ClientEncryptionManager(config.private_key, config.public_key, config.server_public_key,
                                                        encryption_manager)
    client_authentication_manager = ClientAuthenticationManager(client_encryption_manager)
    tcp_server = ClientTCPServer(client_authentication_manager, client_encryption_manager, config.tcp_server_port)
    udp_broadcaster = UDPBroadcaster(config.udp_broadcast_port, f'{{"port": {config.tcp_server_port}}}'.encode("utf-8"))
    connection_manager = ClientConnectionManager(udp_broadcaster, tcp_server)
    await connection_manager.start()
    loop = asyncio.get_event_loop()
    await loop.create_future()


asyncio.run(main())
