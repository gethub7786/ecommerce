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

FULL_SYNC_URL = (
    "https://cwrdistribution.com/feeds/productdownload.php"
    "?id=MPB_NDI0OTY5NDI0OTY5MjM2MQ=="
    "&version=3"
    "&format=csv"
    "&fields=sku,price,qty,qtynj,qtyfl,upc,mfgn,sdesc"
    "&time=0"
)

STOCK_UPDATE_URL = (
    "https://cwrdistribution.com/feeds/productdownload.php"
    "?id=MPB_NDI0OTY5NDI0OTY5MjM2MQ=="
    "&version=3"
    "&format=csv"
    "&fields=sku,qty,qtynj,qtyfl,upc,mfgn"
    "&ohtime={ts}"
)


DEFAULT_LOOKBACK_HOURS = 10

class CwrSupplier(Supplier):
    """CWR Distribution supplier implementation."""
    def __init__(self):
        super().__init__('CWR', 'cwr.json')

    def _get_last_ohtime(self) -> int:
        saved = self.get_credential('last_ohtime')
        if saved is not None:
            return int(saved)
        return int((datetime.now() - timedelta(hours=DEFAULT_LOOKBACK_HOURS)).timestamp())

    def _set_last_ohtime(self, ts: int) -> None:
        self.set_credential('last_ohtime', str(ts))

    def fetch_inventory(self) -> None:
        # Use the inventory-only feed as the primary update
        self.fetch_inventory_stock()

    def fetch_inventory_full(self) -> None:
        """Force download the entire inventory feed and reset the timestamp."""
        mapping_file = self.get_credential('mapping_file')
        output = self.get_credential('full_output', 'cwr_inventory_full.txt')
        url = FULL_SYNC_URL
        try:
            rows = download_inventory(url)
            if len(rows) == 0:
                logging.warning('CWR full feed returned headers only')
                return
            if mapping_file:
                rows = merge_mapping(rows, Path(mapping_file))
            save_inventory(rows, Path(output))
            logging.info('Saved CWR full inventory to %s', output)
            self._set_last_ohtime(int(datetime.now().timestamp()))
        except Exception as exc:
            logging.exception('Failed to fetch CWR full inventory: %s', exc)

    def fetch_inventory_stock(self) -> None:
        """Fetch inventory quantities using ohtime."""
        mapping_file = self.get_credential('mapping_file')
        output = self.get_credential('stock_output', 'cwr_inventory_stock.txt')

        since = self._get_last_ohtime()
        url = STOCK_UPDATE_URL.format(ts=since)
        try:
            rows = download_inventory(url, inventory_only=True)
            if len(rows) == 0:
                logging.warning('CWR stock feed returned headers only')
                return
            if mapping_file:
                rows = merge_mapping(rows, Path(mapping_file))
            save_inventory(rows, Path(output))
            logging.info('Saved CWR stock inventory to %s', output)
            self._set_last_ohtime(int(datetime.now().timestamp()))
        except Exception as exc:
            logging.exception('Failed to fetch CWR stock inventory: %s', exc)

    def test_connection(self) -> None:
        url = FULL_SYNC_URL
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
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
        url = FULL_SYNC_URL
        mapping_file = self.get_credential('mapping_file')
        out_dir = self.get_credential('catalog_dir', '.')
        name = self.get_credential('catalog_name', 'cwr_catalog.csv')
        output = os.path.join(out_dir, name)
        os.makedirs(out_dir, exist_ok=True)
        try:
            rows = download_inventory(url)
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
