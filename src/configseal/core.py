from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

ENCRYPTED_EXTENSION = ".enc"


def encrypt(text: str, key_hex: str) -> bytes:
    return _fernet_from_hex(key_hex).encrypt(text.encode("utf-8"))


def decrypt(blob: bytes, key_hex: str) -> str:
    try:
        return _fernet_from_hex(key_hex).decrypt(blob).decode("utf-8")
    except InvalidToken as e:
        raise ValueError("Incorrect key or corrupted file") from e


def generate_key_hex() -> str:
    """Generate a new random Fernet key, hex-encoded for easy storage."""
    return Fernet.generate_key().hex()


def ensure_extension(path: Path) -> Path:
    """Append the encrypted-file extension if not already present."""
    if path.name.endswith(ENCRYPTED_EXTENSION):
        return path
    return path.with_name(path.name + ENCRYPTED_EXTENSION)


def _fernet_from_hex(key_hex: str) -> Fernet:
    try:
        key = bytes.fromhex(key_hex.strip())
    except ValueError as e:
        raise ValueError("Invalid key format, expected hex string") from e

    try:
        return Fernet(key)
    except ValueError as e:
        raise ValueError("Invalid Fernet key") from e
