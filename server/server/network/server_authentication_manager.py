from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto

from server.network.server_encryption_manager import ServerEncryptionManager


class AuthenticationState(Enum):
    INITIAL = auto()
    PUBLIC_KEY_SHARED = auto()
    CHALLENGE_ANSWERED = auto()
    AUTHENTICATED = auto()


class AuthenticationCommand(ABC):
    """Command issued by the Client Authentication Manager."""


class RejectConnectionCommand(AuthenticationCommand):
    """Command issued when authentication has failed and server connection should be rejected."""


@dataclass
class RespondToChallengeCommand(AuthenticationCommand):
    """Command issued when the server should be challenged to prove its identity."""
    signed_challenge: bytes


@dataclass
class MarkClientAsAuthenticatedCommand(AuthenticationCommand):
    """Command issued when authentication flow is complete."""


class AcceptMessageCommand(AuthenticationCommand):
    """Command issued when authentication is successful and message from this server should be accepted."""


class ServerAuthenticationManager:
    def __init__(self, server_encryption_manager: ServerEncryptionManager):
        self._state = AuthenticationState.INITIAL
        self._server_encryption_manager = server_encryption_manager

    def mark_public_key_as_shared(self):
        if self._state != AuthenticationState.INITIAL:
            raise RuntimeError("Public key shared while in state %", self._state.name)

        self._state = AuthenticationState.PUBLIC_KEY_SHARED

    def authenticate_server_message(self, data: bytes) -> AuthenticationCommand:
        if self._state == AuthenticationState.INITIAL:
            # We first need to send the client the server's public key. So this means the client does not adhere to the
            # handshake protocol. Reject the connection.
            return RejectConnectionCommand()

        elif self._state == AuthenticationState.PUBLIC_KEY_SHARED:
            # Respond to Challenge
            signed_challenge = self._server_encryption_manager.sign_client_challenge(data)
            self._state = AuthenticationState.CHALLENGE_ANSWERED
            return RespondToChallengeCommand(signed_challenge=signed_challenge)

        elif self._state == AuthenticationState.CHALLENGE_ANSWERED:
            # Got client public key after successfully responding to challenge.
            self._state = AuthenticationState.AUTHENTICATED
            self._server_encryption_manager.set_client_public_key(data)
            return MarkClientAsAuthenticatedCommand()

        elif self._state == AuthenticationState.AUTHENTICATED:
            # Once server is authenticated we keep treating it as such for the
            # duration of the session.
            return AcceptMessageCommand()

        # Otherwise always reject.
        return RejectConnectionCommand()

    def is_client_authenticated(self) -> bool:
        return self._state == AuthenticationState.AUTHENTICATED
