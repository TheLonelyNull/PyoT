import asyncio

from rsa import PublicKey

from client.client.network.client_encryption_manager import ClientEncryptionManager
from client.client.network.client_tcp_server import ClientTCPServer
from client.client.network.udp_broadcaster import UDPBroadcaster


class ClientConnectionManager:
    def __init__(self, udp_broadcaster: UDPBroadcaster, client_tcp_server: ClientTCPServer,
                 client_encryption_manager: ClientEncryptionManager):
        self._udp_broadcaster = udp_broadcaster
        self._client_tcp_server = client_tcp_server
        self._client_encryption_manager = client_encryption_manager
        self._client_tcp_server.register_connection_callback(self._on_server_connected_callback)
        self._client_tcp_server.register_disconnection_callback(self._on_server_disconnected_callback)

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

        self._client_tcp_server.register_on_data_received_callback(self._expect_server_public_key_callback)
        # Start an event loop that checks if server is verified after a timeout and prevent hanging DDOs attacks that
        # never responds
        # TODO

    def _expect_server_public_key_callback(self, data: bytes) -> None:
        try:
            public_key = PublicKey.load_pkcs1(data)

            if not self._client_encryption_manager.is_valid_claimed_server_key(public_key):
                # TODO disconnect and blacklist timeout
                return

            # TODO Deregister this callback

            challenge = self._client_encryption_manager.get_server_challenge()
            self._client_tcp_server.register_on_data_received_callback(self._expect_server_challenge_response_callback)
            self._client_tcp_server.write(challenge)

        except ValueError:
            pass
            # TODO disconnect and blacklist timeout

    def _expect_server_challenge_response_callback(self, data: bytes) -> None:
        if not self._client_encryption_manager.verify_server_challenge(data):
            pass
            # TODO disconnect and blacklist timeout

        # Send server the client's public key, so it can start encrypted communications
        self._client_tcp_server.write(self._client_encryption_manager.get_client_public_key().save_pkcs1())

        # Start up event handler
        # TODO deregister this callback.
        # TODO Create event handler.

    def _on_server_disconnected_callback(self):
        # Start broadcasting again if TCP Server was disconnected from.
        loop = asyncio.get_event_loop()
        loop.create_task(self._udp_broadcaster.start())
