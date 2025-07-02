import logging
import csv
import os
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from .base import Supplier
from .cwr_conversion import convert_cwr_to_amazon
from . import catalog
from inventory_processor import (
    download_inventory,
    save_inventory,
)

FULL_SYNC_URL_TMPL = (
    "https://cwrdistribution.com/feeds/productdownload.php"
    "?id={id}"
    "&version=3"
    "&format=csv"
    "&fields=sku,price,qty,qtynj,qtyfl,upc,mfgn,sdesc"
    "&time=0"
)

STOCK_UPDATE_URL_TMPL = (
    "https://cwrdistribution.com/feeds/productdownload.php"
    "?id={id}"
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

    def configure_credentials(self) -> None:
        """Prompt for the CWR feed ID."""
        feed_id = input('Feed ID: ')
        self.set_credential('feed_id', feed_id)
        print('Feed ID saved.')

    def _full_url(self) -> str:
        feed_id = self.get_credential('feed_id')
        if not feed_id:
            print('Missing feed ID; configure credentials first.')
            raise ValueError('Feed ID not configured')
        return FULL_SYNC_URL_TMPL.format(id=feed_id)

    def _stock_url(self, ts: int) -> str:
        feed_id = self.get_credential('feed_id')
        if not feed_id:
            print('Missing feed ID; configure credentials first.')
            raise ValueError('Feed ID not configured')
        return STOCK_UPDATE_URL_TMPL.format(id=feed_id, ts=ts)

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
        output = self.get_credential('full_output', 'cwr_inventory_full.txt')
        try:
            url = self._full_url()
        except ValueError:
            return
        try:
            rows = download_inventory(url)
            if len(rows) == 0:
                logging.warning('CWR full feed returned headers only')
                return
            normalized = []
            for row in rows:
                row = row.copy()
                row['SKU'] = row.pop('sku', row.get('SKU', ''))
                row['QUANTITY'] = row.pop('qty', row.get('Quantity', ''))
                row['NEWJERSEY STOCK'] = row.pop('qtynj', '')
                row['FLORIDA STOCK'] = row.pop('qtyfl', '')
                row['UPC/EAN'] = row.pop('upc', row.get('UPC/EAN', ''))
                row['Manufacturer'] = row.pop('mfgn', row.get('Manufacturer', ''))
                normalized.append(row)
            save_inventory(normalized, Path(output))
            logging.info('Saved CWR full inventory to %s', output)
            # Reset ohtime so the next stock update fetches everything
            self._set_last_ohtime(0)
        except Exception as exc:
            logging.exception('Failed to fetch CWR full inventory: %s', exc)

    def force_full_sync(self) -> None:
        """Reset timestamp and fetch stock feed from the beginning of time."""
        self._set_last_ohtime(0)
        self.fetch_inventory_stock()

    def fetch_inventory_stock(self) -> None:
        """Fetch inventory quantities using ohtime."""
        output = self.get_credential('stock_output', 'cwr_inventory_stock.txt')

        since = self._get_last_ohtime()
        try:
            url = self._stock_url(since)
        except ValueError:
            return
        try:
            rows = download_inventory(url, inventory_only=True)
            if len(rows) == 0:
                logging.warning('CWR stock feed returned headers only')
                return
            normalized = []
            for row in rows:
                row = row.copy()
                row['SKU'] = row.pop('sku', row.get('SKU', ''))
                row['QUANTITY'] = row.pop('qty', row.get('Quantity', ''))
                row['NEWJERSEY STOCK'] = row.pop('qtynj', '')
                row['FLORIDA STOCK'] = row.pop('qtyfl', '')
                row['UPC/EAN'] = row.pop('upc', row.get('UPC/EAN', ''))
                row['Manufacturer'] = row.pop('mfgn', row.get('Manufacturer', ''))
                normalized.append(row)
            save_inventory(normalized, Path(output))
            logging.info('Saved CWR stock inventory to %s', output)
            self._set_last_ohtime(int(datetime.now().timestamp()))
        except Exception as exc:
            logging.exception('Failed to fetch CWR stock inventory: %s', exc)

    def test_connection(self) -> None:
        try:
            url = self._full_url()
        except ValueError:
            return
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
        try:
            url = self._full_url()
        except ValueError:
            return
        out_dir = self.get_credential('catalog_dir', '.')
        name = self.get_credential('catalog_name', 'cwr_catalog.csv')
        output = os.path.join(out_dir, name)
        os.makedirs(out_dir, exist_ok=True)
        try:
            rows = download_inventory(url)
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

    def configure_location_mapping(self) -> None:
        """Prompt for mapping of inventory columns to Amazon supply IDs."""
        mapping = self.get_credential('location_map', {})
        if mapping:
            print('Current mapping:')
            for col, sid in mapping.items():
                print(f'{col} -> {sid}')
        while True:
            col = input('Column name (blank to finish): ').strip()
            if not col:
                break
            sid = input('Supply Source ID: ').strip()
            mapping[col] = sid
        self.set_credential('location_map', mapping)
        print('Location mapping saved.')

    def upload_multi_location_inventory(self) -> None:
        """Convert stock file to Amazon multi-location format."""
        input_path = Path(self.get_credential('stock_output', 'cwr_inventory_stock.txt'))
        output_path = Path(self.get_credential('ml_output', 'cwr_amazon_multilocation_inventory.json'))
        mapping = self.get_credential('location_map', {})
        try:
            count = convert_cwr_to_amazon(input_path, output_path, mapping)
            print(f'Converted {count} SKUs to {output_path}')
        except Exception as exc:
            logging.exception('CWR multi-location conversion failed: %s', exc)
            print('Conversion failed:', exc)
