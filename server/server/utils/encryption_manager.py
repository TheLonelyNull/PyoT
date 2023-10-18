import rsa
from rsa import PublicKey, PrivateKey

HASH_METHOD = "SHA-256"


class EncryptionManager:
    @staticmethod
    def generate_key_pair() -> tuple[PublicKey, PrivateKey]:
        return rsa.newkeys(512)

    @staticmethod
    def encrypt(message: bytes, public_key: PublicKey):
        return rsa.encrypt(message, public_key)

    @staticmethod
    def decrypt(cypher_text: bytes, private_key: PrivateKey):
        return rsa.decrypt(cypher_text, private_key)

    @staticmethod
    def sign(message: bytes, private_key: PrivateKey):
        return rsa.sign(message, private_key, HASH_METHOD)

    @staticmethod
    def verify(message: bytes, signature: bytes, public_key: PublicKey):
        return rsa.verify(message, signature, public_key)
