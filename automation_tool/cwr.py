import logging
from .base import Supplier

class CwrSupplier(Supplier):
    """CWR Distribution supplier implementation."""
    def __init__(self):
        super().__init__('CWR', 'cwr.json')

    def fetch_inventory(self) -> None:
        logging.info(
            "Would download CWR CSV feed using stored credentials: %s",
            self.credentials,
        )
