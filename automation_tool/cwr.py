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

FEED_TEMPLATE = (
    "https://cwrdistribution.com/feeds/productdownload.php?"
    "id={id}&version=3&format=csv&fields=sku,price,sdesc,qtynj,qtyfl,mfgn"
)

DEFAULT_LOOKBACK_HOURS = 10

class CwrSupplier(Supplier):
    """CWR Distribution supplier implementation."""
    def __init__(self):
        super().__init__('CWR', 'cwr.json')

    def configure_credentials(self) -> None:
        """Prompt for the feed ID used in the URL."""
        feed_id = input('Feed ID: ')
        self.set_credential('feed_id', feed_id)
        print('Credentials saved.')

    def _get_last_time(self) -> int:
        saved = self.get_credential('last_unix_time')
        if saved is not None:
            return int(saved)
        return int((datetime.now() - timedelta(hours=DEFAULT_LOOKBACK_HOURS)).timestamp())

    def _set_last_time(self, ts: int) -> None:
        self.set_credential('last_unix_time', str(ts))

    def fetch_inventory(self) -> None:
        feed_id = self.get_credential('feed_id')
        if not feed_id:
            logging.warning('CWR feed ID missing')
            print('Missing feed ID')
            return
        base_url = FEED_TEMPLATE.format(id=feed_id)
        mapping_file = self.get_credential('mapping_file')
        output = self.get_credential('output', 'cwr_inventory.txt')

        since = self._get_last_time()
        try:
            rows = download_inventory(base_url, since)
            if mapping_file:
                rows = merge_mapping(rows, Path(mapping_file))
            save_inventory(rows, Path(output))
            logging.info('Saved CWR inventory to %s', output)
            self._set_last_time(int(datetime.now().timestamp()))
        except Exception as exc:
            logging.exception('Failed to fetch CWR inventory: %s', exc)

    def fetch_inventory_full(self) -> None:
        """Force download the entire inventory feed and reset the timestamp."""
        feed_id = self.get_credential('feed_id')
        if not feed_id:
            logging.warning('CWR feed ID missing')
            print('Missing feed ID')
            return
        base_url = FEED_TEMPLATE.format(id=feed_id)
        mapping_file = self.get_credential('mapping_file')
        output = self.get_credential('full_output', 'cwr_inventory_full.txt')
        try:
            rows = download_inventory(base_url, 0)
            if mapping_file:
                rows = merge_mapping(rows, Path(mapping_file))
            save_inventory(rows, Path(output))
            logging.info('Saved CWR full inventory to %s', output)
            self._set_last_time(int(datetime.now().timestamp()))
        except Exception as exc:
            logging.exception('Failed to fetch CWR full inventory: %s', exc)

    def test_connection(self) -> None:
        feed_id = self.get_credential('feed_id')
        if not feed_id:
            print('Missing feed ID')
            return
        base_url = FEED_TEMPLATE.format(id=feed_id)
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
        feed_id = self.get_credential('feed_id')
        if not feed_id:
            logging.warning('CWR feed ID missing')
            print('Missing feed ID')
            return
        base_url = FEED_TEMPLATE.format(id=feed_id)
        mapping_file = self.get_credential('mapping_file')
        out_dir = self.get_credential('catalog_dir', '.')
        name = self.get_credential('catalog_name', 'cwr_catalog.csv')
        output = os.path.join(out_dir, name)
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
