from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path

from rsa import PublicKey, PrivateKey

from server.utils.encryption_manager import EncryptionManager


@dataclass
class ServerConfig:
    log_level: str
    private_key: PrivateKey
    public_key: PublicKey
    udp_listening_port: int


class ServerConfigError(Exception):
    """Error to raise if config loading goes wrong."""


class ServerConfigLoader:
    DEFAULT_UDP_PORT = 53179

    def __init__(self, encryption_manager: EncryptionManager, path: Path = Path("config.cfg")):
        self._encryption_manager = encryption_manager
        self._path = path
        self._config = ConfigParser(allow_no_value=True)

    def load_config(self) -> ServerConfig:
        self._config.read(self._path)

        log_level = self._config.get("APPLICATION", "LogLevel", fallback="INFO")

        if not (public_key := self._config.get("SECURITY", "PublicKey", fallback=None)) or not (
                private_key := self._config.get("SECURITY", "PrivateKey", fallback=None)):
            public_key, private_key = self._encryption_manager.generate_key_pair()
        else:
            private_key = PrivateKey.load_pkcs1(private_key.encode("UTF-8"))
            public_key = PublicKey.load_pkcs1(public_key.encode("UTF-8"))

        try:
            udp_listening_port = self._config.get("NETWORK", "UDPListeningPort", fallback=None) or self.DEFAULT_UDP_PORT
            udp_listening_port = int(udp_listening_port)
        except ValueError as e:
            raise ServerConfigError("Ports must be valid integers") from e

        config = ServerConfig(
            log_level=log_level,
            private_key=private_key,
            public_key=public_key,
            udp_listening_port=udp_listening_port,
        )
        self.write_config(config)
        return config

    def write_config(self, config: ServerConfig) -> None:
        self._config.read_dict(
            {
                "SECURITY": {
                    "PublicKey": config.public_key.save_pkcs1().decode('UTF-8'),
                    "PrivateKey": config.private_key.save_pkcs1().decode('UTF-8')
                },
                "NETWORK": {
                    "UDPListeningPort": str(config.udp_listening_port),
                },
                "APPLICATION": {
                    "LogLevel": config.log_level
                }
            }
        )

        with open(self._path, 'w') as config_file:
            self._config.write(config_file)
