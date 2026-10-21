import configparser
import os
from functools import cache
from pathlib import Path

from .core import decrypt, ensure_extension

__all__ = ["read_file", "read_config"]


@cache
def read_config(
    filename: str, key: str | None=None, creds: str="configseal-key"
) -> configparser.ConfigParser:
    """Decrypt an encrypted ini file and return it as a ConfigParser.

    :param filename: Path to the encrypted file.
    :param key: Hex-encoded Fernet key, supplied manually.
    :param creds: systemd credential ID to load the key from
        (reads ``$CREDENTIALS_DIRECTORY/<creds>``).
    """
    content = read_file(filename, key=key, creds=creds)
    config = configparser.ConfigParser()
    config.read_string(content)
    return config


@cache
def read_file(
    filename: str, key: str | None=None, creds: str="configseal-key"
) -> str:
    """Decrypt and return the raw contents of an encrypted ini file.

    :param filename: Path to the encrypted file.
    :param key: Hex-encoded Fernet key, supplied manually.
    :param creds: systemd credential ID to load the key from
        (reads ``$CREDENTIALS_DIRECTORY/<creds>``).
    """
    key_hex = _resolve_key(key, creds)
    path = ensure_extension(Path(filename))
    return decrypt(path.read_bytes(), key_hex)


def _resolve_key(key: str | None, creds: str="configseal-key") -> str:
    if key:
        return key

    creds_dir = os.environ.get("CREDENTIALS_DIRECTORY")
    if not creds_dir:
        raise ValueError(
            "CREDENTIALS_DIRECTORY is not set; cannot load systemd credential"
        )

    cred_path = Path(creds_dir) / creds
    if not cred_path.exists():
        raise ValueError(f"Credential '{creds}' not found in {creds_dir}")

    return cred_path.read_text(encoding="utf-8").strip()
