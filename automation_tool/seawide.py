import logging
import ftplib
import os
import csv
from .base import Supplier
from . import catalog

class SeawideSupplier(Supplier):
    """Seawide supplier implementation."""
    def __init__(self):
        super().__init__('Seawide', 'seawide.json')

    def fetch_inventory(self) -> None:
        host = self.get_credential('host')
        user = self.get_credential('username')
        password = self.get_credential('password')
        port = int(self.get_credential('port', 21))
        remote_file = self.get_credential('remote_file', 'inventory.csv')
        output = self.get_credential('output', 'seawide_inventory.csv')

        if not host or not user or not password:
            logging.warning('Seawide FTP credentials missing')
            return

        try:
            with ftplib.FTP_TLS() as ftp:
                ftp.connect(host, port)
                ftp.login(user, password)
                ftp.prot_p()
                with open(output, 'wb') as f:
                    ftp.retrbinary(f'RETR {remote_file}', f.write)
            logging.info('Downloaded Seawide inventory to %s', output)
        except Exception as exc:
            logging.exception('Failed to fetch Seawide inventory: %s', exc)

    def fetch_inventory_full(self) -> None:
        """Download the full inventory file from FTP."""
        host = self.get_credential('host')
        user = self.get_credential('username')
        password = self.get_credential('password')
        port = int(self.get_credential('port', 21))
        remote_file = self.get_credential('remote_full_file', 'inventory_full.csv')
        output = self.get_credential('full_output', 'seawide_inventory_full.csv')

        if not host or not user or not password:
            logging.warning('Seawide FTP credentials missing')
            return

        try:
            with ftplib.FTP_TLS() as ftp:
                ftp.connect(host, port)
                ftp.login(user, password)
                ftp.prot_p()
                with open(output, 'wb') as f:
                    ftp.retrbinary(f'RETR {remote_file}', f.write)
            logging.info('Downloaded Seawide full inventory to %s', output)
        except Exception as exc:
            logging.exception('Failed to fetch Seawide full inventory: %s', exc)

    def test_connection(self) -> None:
        """Attempt to connect to the FTP server and report the result."""
        host = self.get_credential('host')
        user = self.get_credential('username')
        password = self.get_credential('password')
        port = int(self.get_credential('port', 21))
        if not host or not user or not password:
            logging.warning('Seawide FTP credentials missing')
            print('Missing credentials')
            return
        try:
            with ftplib.FTP_TLS() as ftp:
                ftp.connect(host, port, timeout=10)
                ftp.login(user, password)
                ftp.quit()
            logging.info('Seawide FTP connection successful')
            print('Connection successful')
        except Exception as exc:
            logging.exception('Seawide FTP connection failed: %s', exc)
            print('Connection failed:', exc)

    def fetch_catalog(self) -> None:
        """Download the vendor catalog from FTP."""
        host = self.get_credential('host')
        user = self.get_credential('username')
        password = self.get_credential('password')
        port = int(self.get_credential('port', 21))
        remote = self.get_credential('catalog_remote', 'catalog.csv')
        out_dir = self.get_credential('catalog_dir', '.')
        name = self.get_credential('catalog_name', 'seawide_catalog.csv')
        mapping_file = self.get_credential('mapping_file')
        output = os.path.join(out_dir, name)

        if not host or not user or not password:
            logging.warning('Seawide FTP credentials missing')
            return

        os.makedirs(out_dir, exist_ok=True)
        try:
            with ftplib.FTP_TLS() as ftp:
                ftp.connect(host, port)
                ftp.login(user, password)
                ftp.prot_p()
                with open(output, 'wb') as f:
                    ftp.retrbinary(f'RETR {remote}', f.write)
            logging.info('Downloaded Seawide catalog to %s', output)
            with open(output, newline='') as f:
                rows = list(csv.DictReader(f))
            rows = catalog.apply_mapping(rows, mapping_file)
            catalog.save_rows(self.name, rows)
            print('Catalog saved to', catalog.catalog_path(self.name))
        except Exception as exc:
            logging.exception('Failed to fetch Seawide catalog: %s', exc)
            print('Catalog download failed:', exc)
