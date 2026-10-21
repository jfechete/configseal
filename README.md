# ConfigSeal

ConfigSeal encrypts and decrypts INI files, so you can store secrets in a config file and read them safely in your Python code.

## How ConfigSeal Works

ConfigSeal uses a key to encrypt and decrypt a file. Store the key in a safe place, because ConfigSeal cannot recover a lost key.

## CLI Usage

ConfigSeal gives you one command: `configseal-edit`.

### Create a New Encrypted File

Run this command to create a new file:

```bash
configseal-edit secrets.ini.enc
```

The command generates a new key and opens your editor with a template. Edit the template, save the file, and close the editor.

The command then prints the new key. Copy the key now and store it in a safe place, because ConfigSeal does not show the key again.

### Edit an Existing Encrypted File

Run the same command on an existing file:

```bash
configseal-edit secrets.ini.enc
```

The command asks for the key. After you enter the key, the command decrypts the file and opens your editor so you can make changes. Save the file and close the editor when you are done.

The command then encrypts the new content and writes it back to the file.

### Notes on the CLI

- The CLI uses the `EDITOR` environment variable to select your editor, and falls back to `vi` if the variable is not set.
- The CLI adds the `.enc` extension to the file name if the extension is missing.

## API Usage

Import functions from the `configseal` package to read an encrypted file in your code.

```python
from configseal import read_config, read_file
```

### read_config

Use `read_config` to read an encrypted INI file as a `ConfigParser` object.

```python
config = read_config("secrets.ini.enc", key="your-key")
value = config["section"]["key"]
```

### read_file

Use `read_file` to read the raw decrypted text of an encrypted file.

```python
text = read_file("secrets.ini.enc", key="your-key")
```

### Key Resolution

Both functions accept a key in two ways: you can pass the key directly with the `key` parameter, or you can store the key as a systemd credential and set the `creds` parameter to the credential name (the default name is `configseal-key`). When you use a credential, ConfigSeal reads the key from `$CREDENTIALS_DIRECTORY/<creds>`.

If you do not supply a key and `CREDENTIALS_DIRECTORY` is not set, ConfigSeal raises an error.

### Caching

`read_config` and `read_file` cache their results, so ConfigSeal reads a file only once per unique set of arguments during a process run.
