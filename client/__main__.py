import asyncio
import logging

from client.client_connection_manager import ClientConnectionManager
from client.client_tcp_server import ClientTCPServer
from client.udp_broadcaster import UDPBroadcaster

logging.basicConfig(encoding='utf-8', level=logging.DEBUG)


async def main():
    tcp_port = 12345
    udp_broadcast_port = 5555

    tcp_server = ClientTCPServer(tcp_port)
    udp_broadcaster = UDPBroadcaster(udp_broadcast_port, f'{{"port": {tcp_port}}}'.encode("utf-8"))
    connection_manager = ClientConnectionManager(udp_broadcaster, tcp_server)
    await connection_manager.start()
    loop = asyncio.get_event_loop()
    await loop.create_future()


asyncio.run(main())
