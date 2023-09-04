import asyncio
import logging

from server.udp_listener import UDPListener
from server.tcp_client import TCPClient

logging.basicConfig(encoding='utf-8', level=logging.DEBUG)


async def main():
    # udp_listener_port = 5555
    # udp_listener = UDPListener(udp_listener_port)
    # await udp_listener.start()
    tcp_client_port = 12345
    client = TCPClient("192.168.2.13", tcp_client_port)
    await client.start()

    loop = asyncio.get_event_loop()
    await loop.create_future()


asyncio.run(main())
