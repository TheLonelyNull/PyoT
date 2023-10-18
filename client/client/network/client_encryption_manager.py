import random
import string

from rsa import PublicKey, VerificationError, PrivateKey

from client.utils.encryption_manager import EncryptionManager

CHALLENGE_LENGTH = 500


class ClientEncryptionManager:
    def __init__(self,
                 client_private_key: PrivateKey,
                 client_public_key: PublicKey,
                 server_public_key: PublicKey | None,
                 encryption_manager: EncryptionManager
                 ):
        self._client_private_key = client_private_key
        self._client_public_key = client_public_key
        self._encryption_manager = encryption_manager

        self._expected_server_public_key = server_public_key
        self._claimed_server_public_key = None
        self._challenge = None

    def is_valid_claimed_server_key(self, claimed_server_key: bytes) -> bool:
        try:
            public_key = PublicKey.load_pkcs1(claimed_server_key)
        except ValueError:
            return False

        if self._expected_server_public_key and self._expected_server_public_key != public_key:
            return False

        self._claimed_server_public_key = public_key
        return True

    def get_server_challenge(self) -> bytes:
        self._challenge = ''.join(random.choice(string.ascii_letters) for _ in range(CHALLENGE_LENGTH)).encode("UTF-8")
        return self._challenge

    def verify_server_challenge(self, signed_challenge: bytes) -> bool:
        try:
            self._encryption_manager.verify(self._challenge, signed_challenge, self._claimed_server_public_key)
        except VerificationError:
            return False
        return True

    def encrypt_payload_for_server(self, payload: bytes) -> bytes:
        return self._encryption_manager.encrypt(payload, self._claimed_server_public_key)

    def decrypt_payload_from_server(self, payload: bytes) -> bytes:
        return self._encryption_manager.decrypt(payload, self._client_private_key)

    def get_client_public_key(self) -> PublicKey:
        return self._client_public_key

    def get_server_public_key(self) -> PublicKey:
        return self._claimed_server_public_key

    def reset(self) -> None:
        self._claimed_server_public_key = None
        self._challenge = None
