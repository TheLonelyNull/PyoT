from rsa import PublicKey, PrivateKey

from server.utils.encryption_manager import EncryptionManager


class ServerEncryptionManager:
    def __init__(self,
                 server_private_key: PrivateKey,
                 server_public_key: PublicKey,
                 encryption_manager: EncryptionManager
                 ):
        self._server_private_key = server_private_key
        self._server_public_key = server_public_key
        self._encryption_manager = encryption_manager

        self._client_public_key = None

    def get_server_public_key(self) -> PublicKey:
        return self._server_public_key

    def sign_client_challenge(self, challenge: bytes) -> bytes:
        return self._encryption_manager.sign(challenge, self._server_private_key)

    def set_client_public_key(self, key: bytes) -> None:
        self._client_public_key = PublicKey.load_pkcs1(key)

    def encrypt_payload_for_client(self, payload: bytes) -> bytes:
        return self._encryption_manager.encrypt(payload, self._client_public_key)

    def decrypt_payload_from_client(self, payload: bytes) -> bytes:
        return self._encryption_manager.decrypt(payload, self._server_private_key)
