import logging
import csv
import os
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from .base import Supplier, SFTPWrapper
from .cwr_conversion import convert_cwr_to_amazon
from .sku_mapping import load_mapping, apply_mapping
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
FTP_HOST = "edi.cwrdistribution.com"



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

    def configure_sku_mapping(self) -> None:
        """Prompt for a SKU mapping CSV file and store its absolute path."""
        path = input('SKU mapping file path: ').strip()
        if path:
            p = Path(path).expanduser().resolve()
            if not p.exists():
                print('File not found:', p)
                return
            self.set_credential('sku_map_file', str(p))
            print('SKU mapping saved.')

    def configure_ftp(self) -> None:
        """Prompt for SFTP credentials used for catalog downloads."""
        user = input('FTP User: ')
        password = input('FTP Password: ')
        port = input('FTP Port (default 22): ') or '22'
        self.set_credential('ftp_user', user)
        self.set_credential('ftp_password', password)
        self.set_credential('ftp_port', port)
        self.set_credential('ftp_remote_dir', '/out')
        self.set_credential('ftp_remote_file', 'catalog.csv')
        print('FTP credentials saved.')

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
        # On first run return the Unix epoch so we fetch the entire feed
        return 0

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
            map_file = self.get_credential('sku_map_file')
            if map_file:
                p = Path(map_file)
                if not p.is_absolute():
                    p = Path(os.path.dirname(self.config_path)) / p
                mapping = load_mapping(p)
                normalized = apply_mapping(normalized, mapping)
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
            map_file = self.get_credential('sku_map_file')
            if map_file:
                p = Path(map_file)
                if not p.is_absolute():
                    p = Path(os.path.dirname(self.config_path)) / p
                mapping = load_mapping(p)
                normalized = apply_mapping(normalized, mapping)
            save_inventory(normalized, Path(output))
            logging.info('Saved CWR stock inventory to %s', output)
            self._set_last_ohtime(int(datetime.now().timestamp()))
        except Exception as exc:
            logging.exception('Failed to fetch CWR stock inventory: %s', exc)

    def test_connection(self) -> None:
        ftp = self._ftp_connect()
        if ftp:
            ftp.quit()
            print('FTP connection successful')
            logging.info('CWR FTP connection successful')
            return
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
        ftp = self._ftp_connect()
        if not ftp:
            return
        remote_dir = self.get_credential('ftp_remote_dir', '/out')
        remote_file = self.get_credential('ftp_remote_file', 'catalog.csv')
        remote_path = f"{remote_dir.rstrip('/')}/{remote_file}" if remote_dir else remote_file
        out_dir = self.get_credential('catalog_dir', '.')
        name = self.get_credential('catalog_name', 'cwr_catalog.csv')
        output = os.path.join(out_dir, name)
        os.makedirs(out_dir, exist_ok=True)
        try:
            try:
                total = ftp.size(remote_path)
            except Exception:
                total = None
            downloaded = 0
            with open(output, 'wb') as f:
                def write_chunk(data):
                    nonlocal downloaded
                    f.write(data)
                    downloaded += len(data)
                    if total:
                        percent = int(downloaded * 100 / total)
                        print(f"\rDownloading: {percent}%", end='', flush=True)
                    else:
                        kb = downloaded // 1024
                        print(f"\rDownloaded {kb} KB", end='', flush=True)

                ftp.retrbinary(f'RETR {remote_path}', write_chunk)
            if total:
                print('\rDownload complete      ')
            else:
                print(f"\rDownloaded {downloaded // 1024} KB total      ")
            with open(output, newline='') as f:
                rows = list(csv.DictReader(f))
            catalog.save_rows(self.name, rows)
            logging.info('Saved CWR catalog to %s', output)
            print('Catalog saved to', catalog.catalog_path(self.name))
        except Exception as exc:
            logging.exception('Failed to fetch CWR catalog: %s', exc)
            print('Catalog download failed:', exc)
        finally:
            try:
                ftp.quit()
            except Exception:
                pass

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

    def _ftp_connect(self):
        """Connect to the CWR FTP server for catalog downloads."""
        user = self.get_credential('ftp_user')
        password = self.get_credential('ftp_password')
        port = int(self.get_credential('ftp_port', '22'))
        if not user or not password:
            print('Missing FTP credentials')
            return None
        try:
            import paramiko
        except Exception as exc:
            logging.exception('paramiko missing for SFTP: %s', exc)
            print('paramiko library required for SFTP')
            return None
        try:
            transport = paramiko.Transport((FTP_HOST, port))
            transport.connect(username=user, password=password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            return SFTPWrapper(sftp)
        except Exception as exc:
            logging.exception('CWR SFTP connection failed: %s', exc)
            print('CWR SFTP connection failed:', exc)
            return None
