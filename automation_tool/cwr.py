import logging
from datetime import datetime, timedelta
from pathlib import Path
from .base import Supplier
from inventory_processor import (
    download_inventory,
    merge_mapping,
    save_inventory,
)

class CwrSupplier(Supplier):
    """CWR Distribution supplier implementation."""
    def __init__(self):
        super().__init__('CWR', 'cwr.json')

    def fetch_inventory(self) -> None:
        base_url = self.get_credential('base_url')
        mapping_file = self.get_credential('mapping_file')
        output = self.get_credential('output', 'cwr_inventory.txt')
        if not base_url:
            logging.warning('CWR base_url credential missing')
            return

        since = int((datetime.now() - timedelta(hours=10)).timestamp())
        try:
            rows = download_inventory(base_url, since)
            if mapping_file:
                rows = merge_mapping(rows, Path(mapping_file))
            save_inventory(rows, Path(output))
            logging.info('Saved CWR inventory to %s', output)
        except Exception as exc:
            logging.exception('Failed to fetch CWR inventory: %s', exc)
