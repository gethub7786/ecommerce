import json
import os
import logging

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

class Supplier:
    def __init__(self, name, config_name):
        self.name = name
        self.config_path = os.path.join(DATA_DIR, config_name)
        self.credentials = {}
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.credentials = json.load(f)

    def save(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.credentials, f)

    def set_credential(self, key, value):
        self.credentials[key] = value
        self.save()

    def get_credential(self, key, default=None):
        return self.credentials.get(key, default)

    def fetch_inventory(self):
        """Placeholder for supplier-specific inventory retrieval."""
        logging.info("Fetching inventory for %s", self.name)


class KeystoneSupplier(Supplier):
    def __init__(self):
        super().__init__('Keystone', 'keystone.json')

    def fetch_inventory(self):
        logging.info("Would connect to Keystone FTP/API using stored credentials: %s", self.credentials)
        # Actual implementation would connect to FTP and download files.


class CwrSupplier(Supplier):
    def __init__(self):
        super().__init__('CWR', 'cwr.json')

    def fetch_inventory(self):
        logging.info("Would download CWR CSV feed using stored credentials: %s", self.credentials)


class SeawideSupplier(Supplier):
    def __init__(self):
        super().__init__('Seawide', 'seawide.json')

    def fetch_inventory(self):
        logging.info("Would connect to Seawide systems using stored credentials: %s", self.credentials)
