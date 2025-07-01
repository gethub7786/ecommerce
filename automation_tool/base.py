import json
import os
import logging


class SFTPWrapper:
    """Minimal wrapper exposing FTP-style methods for paramiko clients."""

    def __init__(self, client):
        self._client = client

    def size(self, path: str) -> int:
        return self._client.stat(path).st_size

    def retrbinary(self, cmd: str, callback) -> None:
        path = cmd.split(" ", 1)[1]
        with self._client.file(path, "rb") as f:
            while True:
                data = f.read(32768)
                if not data:
                    break
                callback(data)

    def quit(self) -> None:
        self._client.close()

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

class Supplier:
    """Generic supplier storing credentials and providing a fetch hook."""
    def __init__(self, name: str, config_name: str):
        self.name = name
        self.config_path = os.path.join(DATA_DIR, config_name)
        self.credentials = {}
        self.load()

    def load(self) -> None:
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.credentials = json.load(f)

    def save(self) -> None:
        with open(self.config_path, 'w') as f:
            json.dump(self.credentials, f)

    def set_credential(self, key: str, value: str) -> None:
        self.credentials[key] = value
        self.save()

    def get_credential(self, key: str, default=None):
        return self.credentials.get(key, default)

    def fetch_inventory(self) -> None:
        logging.info("Fetching inventory for %s", self.name)

    def configure_credentials(self) -> None:
        """Prompt for a single credential key/value."""
        key = input("Credential name: ")
        value = input("Value: ")
        self.set_credential(key, value)

    def test_connection(self) -> None:
        """Placeholder connection test."""
        logging.info("Testing connection for %s", self.name)
        print("No connection test implemented")

    def fetch_catalog(self) -> None:
        """Placeholder catalog fetch."""
        logging.info("Fetching catalog for %s", self.name)
