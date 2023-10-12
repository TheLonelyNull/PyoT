import random
import string

from rsa import PublicKey, VerificationError, PrivateKey

from shared.encryption.encryption_manager import EncryptionManager

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
        self._expected_server_public_key = server_public_key
        self._encryption_manager = encryption_manager

        self._claimed_server_public_key = None
        self._verified_claimed_key = None
        self._challenge = None

    def is_valid_claimed_server_key(self, claimed_server_key: PublicKey) -> bool:
        if self._expected_server_public_key and self._expected_server_public_key != claimed_server_key:
            return False

        self._claimed_server_public_key = claimed_server_key
        return True

    def get_server_challenge(self) -> bytes:
        self._challenge = ''.join(random.choice(string.ascii_letters) for i in range(CHALLENGE_LENGTH)).encode("UTF-8")
        return self._challenge

    def verify_server_challenge(self, signed_challenge: bytes) -> bool:
        if not self._challenge:
            raise RuntimeError("No challenge generated yey.")
        try:
            self._encryption_manager.verify(self._challenge, signed_challenge, self._claimed_server_public_key)
        except VerificationError:
            return False
        self._verified_claimed_key = True
        return True

    def encrypt_payload_for_server(self, payload: bytes) -> bytes:
        if not self._verified_claimed_key:
            raise RuntimeError("Server handshake not completed.")

        return self._encryption_manager.encrypt(payload, self._claimed_server_public_key)

    def decrypt_payload_from_server(self, payload: bytes) -> bytes:
        if not self._verified_claimed_key:
            raise RuntimeError("Server handshake not completed.")

        return self._encryption_manager.decrypt(payload, self._client_private_key)

    def get_client_public_key(self) -> PublicKey:
        return self._client_public_key

    def get_server_public_key(self) -> PublicKey:
        return self._claimed_server_public_key
