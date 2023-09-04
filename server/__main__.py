import asyncio
import logging

from server.server_connection_manager import ServerConnectionManager
from server.udp_listener import UDPListener
from server.tcp_client import TCPClient

logging.basicConfig(encoding='utf-8', level=logging.DEBUG)


async def main():
    udp_listener_port = 5555
    udp_listener = UDPListener(udp_listener_port)
    connection_manager = ServerConnectionManager(
        udp_listener
    )
    await connection_manager.start()

    loop = asyncio.get_event_loop()
    await loop.create_future()


asyncio.run(main())
