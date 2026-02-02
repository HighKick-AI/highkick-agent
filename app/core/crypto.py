from __future__ import annotations

import secrets
import string

import base64
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

import jwt  # PyJWT


@dataclass(frozen=True)
class KeyPair:
    """
    - private_key_pem: PKCS8 PEM (string)
    - public_key_b64: 32-byte raw Ed25519 public key encoded base64url (short & readable)
    """
    private_key_pem: str
    public_key_b64: str



class Crypto:

    @staticmethod
    def generate_random_string(num_chars: int) -> str:
        if num_chars <= 0:
            raise ValueError("num_chars must be > 0")

        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(num_chars))

    @staticmethod
    def b64url_encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


    @staticmethod
    def b64url_decode(data: str) -> bytes:
        pad = "=" * (-len(data) % 4)
        return base64.urlsafe_b64decode((data + pad).encode("ascii"))



    @staticmethod
    def seed_from_secret(secret: Union[str, bytes], *, info: bytes = b"jwt-ed25519-key-derivation-v1") -> bytes:
        """
        Derive a deterministic 32-byte seed from a secret phrase.
        HKDF is used to turn arbitrary-length secret input into a uniform seed.
        """
        if isinstance(secret, str):
            secret_bytes = secret.encode("utf-8")
        else:
            secret_bytes = secret

        # NOTE: Using salt=b"" makes this purely deterministic per secret+info.
        # If you want domain separation for different apps/environments, change 'info'.
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"",
            info=info,
        )
        return hkdf.derive(secret_bytes)


    @staticmethod
    def create_key_pair(secret: Union[str, bytes]) -> KeyPair:
        """
        Deterministically creates an Ed25519 key pair from a secret phrase.
        """
        seed = Crypto.seed_from_secret(secret)
        priv = Ed25519PrivateKey.from_private_bytes(seed)
        pub = priv.public_key()

        private_pem = priv.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("utf-8")

        public_raw = pub.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        public_b64 = Crypto.b64url_encode(public_raw)

        return KeyPair(private_key_pem=private_pem, public_key_b64=public_b64)


    @staticmethod
    def create_token(
        private_key: str,
        *,
        subject: str = "user",
        audience: Optional[str] = None,
        issuer: Optional[str] = None,
        expires_in_seconds: int = 3600,
        extra_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create and sign a JWT using an Ed25519 private key (PEM, PKCS8).

        Returns the compact JWT string.
        """
        now = int(time.time())
        payload: Dict[str, Any] = {
            "sub": subject,
            "iat": now,
            "exp": now + int(expires_in_seconds),
        }
        if audience is not None:
            payload["aud"] = audience
        if issuer is not None:
            payload["iss"] = issuer
        if extra_claims:
            payload.update(extra_claims)

        # PyJWT supports EdDSA when cryptography is installed.
        token = jwt.encode(payload, private_key, algorithm="EdDSA")
        # PyJWT may return bytes in older versions; normalize to str.
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return token

    @staticmethod
    def validate_token(
        token: str,
        public_key: str,
        *,
        audience: Optional[str] = None,
        issuer: Optional[str] = None,
        leeway_seconds: int = 0,
    ) -> Dict[str, Any]:
        """
        Validate a JWT using ONLY the public key.

        `public_key` is the base64url-encoded raw Ed25519 public key
        produced by create_key_pair(...).public_key_b64

        Returns the decoded claims dict if valid; raises jwt exceptions otherwise.
        """
        pub_raw = Crypto.b64url_decode(public_key)
        pub = Ed25519PublicKey.from_public_bytes(pub_raw)

        # Provide the public key object directly to PyJWT.
        options = {
            "require": ["exp", "iat", "sub"],
        }

        decoded = jwt.decode(
            token,
            key=pub,
            algorithms=["EdDSA"],
            audience=audience,
            issuer=issuer,
            leeway=leeway_seconds,
            options=options,
        )
        return decoded



    # if __name__ == "__main__":
    #     kp = create_key_pair("correct horse battery staple")
    #     print("Public key (base64url):", kp.public_key_b64)
    #     print("Private key PEM:\n", kp.private_key_pem)

    #     t = create_token(kp.private_key_pem, subject="alice", expires_in_seconds=600)
    #     print("JWT:", t)

    #     claims = validate_token(t, kp.public_key_b64)
    #     print("Validated claims:", claims)
