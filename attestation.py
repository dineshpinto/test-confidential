import os
import json
import logging
import socket
from http.client import HTTPConnection
from typing import override

logger = logging.getLogger(__name__)


class AttestationError(Exception):
    """Custom exception for attestation communication errors."""


class AttestationInterface(HTTPConnection):
    def __init__(
        self,
        host: str = "localhost",
        unix_socket_path: str = "/run/container_launcher/teeserver.sock",
    ) -> None:
        super().__init__(host)
        self.unix_socket_path = unix_socket_path

    @override
    def connect(self) -> None:
        """Create a Unix domain socket and connect to the socket."""
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.unix_socket_path)

    def _post(self, endpoint: str, body: str, headers: dict) -> bytes:
        self.request("POST", endpoint, body=body, headers=headers)
        res = self.getresponse()
        success_status = 200
        if res.status != success_status:
            msg = f"Failed to get attestation response: {res.status} {res.reason}"
            raise AttestationError(msg)
        return res.read()

    def get_token(
        self,
        nonces: list[str] | None,
        audience: str,
        token_type: str,  # noqa: S107
    ) -> str:
        """Fetch an attestation token with custom nonce and audience."""
        headers = {"Content-Type": "application/json"}
        if nonces:
            body = json.dumps(
                {"audience": audience, "token_type": token_type, "nonces": nonces}
            )
        else:
            body = json.dumps(
                {"audience": audience, "token_type": token_type}
            )
        token_bytes = self._post("/v1/token", body=body, headers=headers)
        token = token_bytes.decode()
        logger.info("Token %s", token)
        return token


if __name__ == "__main__":
    nonces = [os.getenv("NONCE", default=None)]
    audience = os.getenv("AUDIENCE", default="https://sts.google.com")
    token_type = os.getenv("TOKEN_TYPE", default="OIDC")

    attestation = AttestationInterface()
    attestation.get_token(
        nonces=nonces, 
        audience=audience, 
        token_type=token_type
    )