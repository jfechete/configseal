import argparse
import getpass
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from .core import decrypt, encrypt, ensure_extension, generate_key_hex

DEFAULT_TEMPLATE = "[section]\nkey = value\n"


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    path = ensure_extension(Path(args.file))
    edit_file(path)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="configseal-edit",
        description="Create or edit an encrypted ini file",
    )
    parser.add_argument("file", help="Path to the encrypted ini file")
    return parser


def edit_file(path: Path) -> None:
    if not path.exists():
        print(f"{path} does not exist, creating new encrypted file.")
        key_hex = generate_key_hex()
        plaintext = _run_editor(DEFAULT_TEMPLATE)
        path.write_bytes(encrypt(plaintext, key_hex))
        print(f"Saved {path}")
        print("Save this key, it will not be shown again:")
        print(key_hex)
    else:
        key_hex = getpass.getpass("Key: ")
        plaintext = decrypt(path.read_bytes(), key_hex)
        new_plaintext = _run_editor(plaintext)

        if new_plaintext == plaintext:
            print("No changes made.")
            return

        path.write_bytes(encrypt(new_plaintext, key_hex))
        print(f"Saved {path}")


def _run_editor(initial_content: str) -> str:
    editor = os.environ.get("EDITOR", "vi")
    fd, tmp_name = tempfile.mkstemp(suffix=".ini")
    tmp_path = Path(tmp_name)

    try:
        os.chmod(tmp_path, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as tf:
            tf.write(initial_content)

        subprocess.run([editor, str(tmp_path)], check=True)
        return tmp_path.read_text(encoding="utf-8")
    finally:
        _shred(tmp_path)


def _shred(path: Path) -> None:
    shred_bin = shutil.which("shred")
    if shred_bin:
        subprocess.run([shred_bin, "-u", "-z", str(path)], check=False)
    else:
        print("Warning: 'shred' not found, deleting file without secure wipe.")
        path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
