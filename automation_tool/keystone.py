import logging
from .base import Supplier

class KeystoneSupplier(Supplier):
    """Keystone Automotive supplier implementation."""
    def __init__(self):
        super().__init__('Keystone', 'keystone.json')

    def fetch_inventory(self) -> None:
        logging.info(
            "Would connect to Keystone FTP/API using stored credentials: %s",
            self.credentials,
        )
        # Actual implementation would connect to FTP and download files.
