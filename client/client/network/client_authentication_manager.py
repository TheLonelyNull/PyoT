from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto

from client.network.client_encryption_manager import ClientEncryptionManager


class AuthenticationState(Enum):
    UNCONNECTED = auto()
    CHALLENGE_ISSUED = auto()
    AUTHENTICATED = auto()


class AuthenticationCommand(ABC):
    """Command issued by the Client Authentication Manager."""


class RejectConnectionCommand(AuthenticationCommand):
    """Command issued when authentication has failed and server connection should be rejected."""


@dataclass
class IssueChallengeCommand(AuthenticationCommand):
    """Command issued when the server should be challenged to prove its identity."""
    challenge: bytes


@dataclass
class AcceptChallengeCommand(AuthenticationCommand):
    """Command issued when challenge is successful and client public key should be shared."""
    client_public_key: bytes


class AcceptMessageCommand(AuthenticationCommand):
    """Command issued when authentication is successful and message from this server should be accepted."""


class ClientAuthenticationManager:
    def __init__(self, client_encryption_manager: ClientEncryptionManager):
        self._state = AuthenticationState.UNCONNECTED
        self._client_encryption_manager = client_encryption_manager
        # TODO blacklist manager

    def authenticate_server_message(self, data: bytes) -> AuthenticationCommand:
        if self._state == AuthenticationState.UNCONNECTED:
            # Challenge server
            if self._client_encryption_manager.is_valid_claimed_server_key(data):
                self._state = AuthenticationState.CHALLENGE_ISSUED
                return IssueChallengeCommand(
                    challenge=self._client_encryption_manager.get_server_challenge()
                )

        elif self._state == AuthenticationState.CHALLENGE_ISSUED:
            # Validate challenge response
            if self._client_encryption_manager.verify_server_challenge(data):
                self._state = AuthenticationState.AUTHENTICATED
                return AcceptChallengeCommand(
                    self._client_encryption_manager.get_client_public_key().save_pkcs1()
                )

        elif self._state == AuthenticationState.AUTHENTICATED:
            # Once server is authenticated we keep treating it as such for the
            # duration of the session.
            return AcceptMessageCommand()

        # Otherwise always reject.
        return RejectConnectionCommand()

    def is_server_authenticated(self) -> bool:
        return self._state == AuthenticationState.AUTHENTICATED

    def reset(self):
        self._state = AuthenticationState.UNCONNECTED
