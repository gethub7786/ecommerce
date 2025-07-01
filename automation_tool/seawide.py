import logging
from .base import Supplier

class SeawideSupplier(Supplier):
    """Seawide supplier implementation."""
    def __init__(self):
        super().__init__('Seawide', 'seawide.json')

    def fetch_inventory(self) -> None:
        logging.info(
            "Would connect to Seawide systems using stored credentials: %s",
            self.credentials,
        )
