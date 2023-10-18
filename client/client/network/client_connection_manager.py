import asyncio

from client.network.client_tcp_server import ClientTCPServer
from client.network.udp_broadcaster import UDPBroadcaster


class ClientConnectionManager:
    def __init__(self, udp_broadcaster: UDPBroadcaster, client_tcp_server: ClientTCPServer):
        self._udp_broadcaster = udp_broadcaster
        self._client_tcp_server = client_tcp_server
        # Register Callbacks
        self._client_tcp_server.register_connection_callback(self._on_server_connected_callback)
        self._client_tcp_server.register_disconnection_callback(self._on_server_disconnected_callback)
        self._client_tcp_server.register_on_data_received_callback(self._on_data_received_callback)

    async def start(self):
        await self._client_tcp_server.start()
        await self._udp_broadcaster.start()

    async def stop(self):
        await self._udp_broadcaster.stop()
        await self._client_tcp_server.stop()

    def _on_server_connected_callback(self, transport):
        # Stop UDP Broadcast if server found us
        loop = asyncio.get_event_loop()
        loop.create_task(self._udp_broadcaster.stop())

    def _on_data_received_callback(self, payload: bytes):
        pass

    def _on_server_disconnected_callback(self):
        # Start broadcasting again if TCP Server was disconnected from.
        loop = asyncio.get_event_loop()
        loop.create_task(self._udp_broadcaster.start())
