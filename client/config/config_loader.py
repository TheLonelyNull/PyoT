from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from rsa import PublicKey, PrivateKey

from shared.encryption.encryption_manager import EncryptionManager


@dataclass
class ClientConfig:
    client_id: str
    log_level: str
    server_public_key: PublicKey
    private_key: PrivateKey
    public_key: PublicKey
    udp_broadcast_port: int
    tcp_server_port: int


class ClientConfigError(Exception):
    """Error to raise if config loading goes wrong."""


class ClientConfigLoader:
    DEFAULT_UDP_PORT = 53179
    DEFAULT_TCP_PORT = 52179

    def __init__(self, encryption_manager: EncryptionManager, path: Path = Path("./config.cfg")):
        self._encryption_manager = encryption_manager
        self._path = path
        self._config = ConfigParser(allow_no_value=True)

    def load_config(self) -> ClientConfig:
        self._config.read(self._path)

        log_level = self._config.get("APPLICATION", "LogLevel", fallback="INFO")

        if not (client_id := self._config.get("APPLICATION", "ClientId", fallback=None)):
            client_id = str(uuid4())

        if not (server_public_key := self._config.get("SECURITY", "ServerPublicKey", fallback=None)):
            raise ClientConfigError("Server public key not found")
        server_public_key = PublicKey.load_pkcs1(server_public_key.encode("UTF-8"))

        if not (public_key := self._config.get("SECURITY", "PublicKey", fallback=None)) or not (
                private_key := self._config.get("SECURITY", "PrivateKey", fallback=None)):
            public_key, private_key = self._encryption_manager.generate_key_pair()
        else:
            private_key = PrivateKey.load_pkcs1(private_key.encode("UTF-8"))
            public_key = PublicKey.load_pkcs1(public_key.encode("UTF-8"))

        try:
            udp_broadcast_port = self._config.get("NETWORK", "UDPBroadcastPort", fallback=None) or self.DEFAULT_UDP_PORT
            udp_broadcast_port = int(udp_broadcast_port)
            tcp_server_port = self._config.get("NETWORK", "TCPServerPort", fallback=None) or self.DEFAULT_TCP_PORT
            tcp_server_port = int(tcp_server_port)
        except ValueError as e:
            raise ClientConfigError("Ports must be valid integers") from e

        config = ClientConfig(
            client_id=client_id,
            log_level=log_level,
            server_public_key=server_public_key,
            private_key=private_key,
            public_key=public_key,
            udp_broadcast_port=udp_broadcast_port,
            tcp_server_port=tcp_server_port
        )
        self.write_config(config)
        return config

    def write_config(self, config: ClientConfig) -> None:
        self._config.read_dict(
            {
                "SECURITY": {
                    "ServerPublicKey": config.server_public_key.save_pkcs1().decode('UTF-8'),
                    "PublicKey": config.public_key.save_pkcs1().decode('UTF-8'),
                    "PrivateKey": config.private_key.save_pkcs1().decode('UTF-8')
                },
                "NETWORK": {
                    "UDPBroadcastPort": str(config.udp_broadcast_port),
                    "TCPServerPort": str(config.tcp_server_port)
                },
                "APPLICATION": {
                  "ClientId": config.client_id,
                  "LogLevel": config.log_level
                }
            }
        )
        with open(self._path, 'w') as config_file:
            self._config.write(config_file)
