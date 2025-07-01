import logging
import csv
import os
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from .base import Supplier
from . import catalog
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

    def test_connection(self) -> None:
        base_url = self.get_credential('base_url')
        if not base_url:
            print('Missing base_url credential')
            return
        try:
            with urllib.request.urlopen(base_url, timeout=10) as resp:
                if resp.status == 200:
                    print('Connection successful')
                    logging.info('CWR connection successful')
                else:
                    print('Connection failed: status', resp.status)
                    logging.warning('CWR connection failed status %s', resp.status)
        except Exception as exc:
            logging.exception('CWR connection failed: %s', exc)
            print('Connection failed:', exc)

    def fetch_catalog(self) -> None:
        base_url = self.get_credential('base_url')
        mapping_file = self.get_credential('mapping_file')
        out_dir = self.get_credential('catalog_dir', '.')
        name = self.get_credential('catalog_name', 'cwr_catalog.csv')
        output = os.path.join(out_dir, name)
        if not base_url:
            logging.warning('CWR base_url credential missing')
            return
        os.makedirs(out_dir, exist_ok=True)
        try:
            rows = download_inventory(base_url, 0)
            if mapping_file:
                rows = merge_mapping(rows, Path(mapping_file))
            catalog.save_rows(self.name, rows)
            with open(output, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
            logging.info('Saved CWR catalog to %s', output)
            print('Catalog saved to', catalog.catalog_path(self.name))
        except Exception as exc:
            logging.exception('Failed to fetch CWR catalog: %s', exc)
            print('Catalog download failed:', exc)
