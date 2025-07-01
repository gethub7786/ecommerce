import logging
import ftplib
import os
import csv
import urllib.request
import xml.etree.ElementTree as ET
from .base import Supplier
from . import catalog
from .keystone import _parse_dataset

class SeawideSupplier(Supplier):
    """Seawide supplier implementation."""
    def __init__(self):
        super().__init__('Seawide', 'seawide.json')

    def fetch_inventory(self) -> None:
        """Retrieve incremental inventory via SOAP or FTP."""
        account = self.get_credential('account_number')
        key = self.get_credential('api_key')
        if account and key:
            self._fetch_inventory_soap(account, key)
        else:
            self.fetch_inventory_update()

    def fetch_inventory_update(self) -> None:
        account = self.get_credential('account_number')
        key = self.get_credential('api_key')
        if account and key:
            self._fetch_inventory_update_soap(account, key)
            return

        host = self.get_credential('host')
        user = self.get_credential('username')
        password = self.get_credential('password')
        port = int(self.get_credential('port', 21))
        protocol = self.get_credential('protocol', 'ftps').lower()
        remote_file = self.get_credential('remote_update_file', 'inventory_update.csv')
        output = self.get_credential('output', 'seawide_inventory_update.csv')

        if not host or not user or not password:
            logging.warning('Seawide FTP credentials missing')
            return

        try:
            with (ftplib.FTP() if protocol == 'ftp' else ftplib.FTP_TLS()) as ftp:
                ftp.connect(host, port)
                ftp.login(user, password)
                if protocol != 'ftp':
                    ftp.prot_p()
                with open(output, 'wb') as f:
                    ftp.retrbinary(f'RETR {remote_file}', f.write)
            logging.info('Downloaded Seawide inventory update to %s', output)
        except Exception as exc:
            logging.exception('Failed to fetch Seawide inventory: %s', exc)

    def fetch_inventory_full(self) -> None:
        """Download the full inventory file via SOAP or FTP."""
        account = self.get_credential('account_number')
        key = self.get_credential('api_key')
        if account and key:
            self._fetch_inventory_full_soap(account, key)
            return

        host = self.get_credential('host')
        user = self.get_credential('username')
        password = self.get_credential('password')
        port = int(self.get_credential('port', 21))
        protocol = self.get_credential('protocol', 'ftps').lower()
        remote_file = self.get_credential('remote_full_file', 'inventory_full.csv')
        output = self.get_credential('full_output', 'seawide_inventory_full.csv')

        if not host or not user or not password:
            logging.warning('Seawide FTP credentials missing')
            return

        try:
            with (ftplib.FTP() if protocol == 'ftp' else ftplib.FTP_TLS()) as ftp:
                ftp.connect(host, port)
                ftp.login(user, password)
                if protocol != 'ftp':
                    ftp.prot_p()
                with open(output, 'wb') as f:
                    ftp.retrbinary(f'RETR {remote_file}', f.write)
            logging.info('Downloaded Seawide full inventory to %s', output)
        except Exception as exc:
            logging.exception('Failed to fetch Seawide full inventory: %s', exc)

    def _fetch_inventory_update_soap(self, account: str, key: str) -> None:
        """Retrieve inventory updates via SOAP."""
        output = self.get_credential('output', 'seawide_inventory_update.csv')
        envelope = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:sea="http://seawide.com">
  <soapenv:Header/>
  <soapenv:Body>
    <sea:GetInventoryUpdates>
      <sea:Key>{key}</sea:Key>
      <sea:FullAccountNo>{account}</sea:FullAccountNo>
    </sea:GetInventoryUpdates>
  </soapenv:Body>
</soapenv:Envelope>'''
        req = urllib.request.Request(
            'https://api.seawide.com/inventory.asmx',
            data=envelope.encode('utf-8'),
            headers={'Content-Type': 'text/xml; charset=utf-8',
                    'SOAPAction': 'http://seawide.com/GetInventoryUpdates'},
        )
        try:
            with urllib.request.urlopen(req) as resp:
                xml_data = resp.read()
            rows = _parse_dataset(xml_data)
            if rows:
                with open(output, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)
                logging.info('Saved Seawide inventory update to %s', output)
            else:
                logging.warning('No data returned from Seawide update')
        except Exception as exc:
            logging.exception('Failed to fetch Seawide SOAP update: %s', exc)

    def _fetch_inventory_full_soap(self, account: str, key: str) -> None:
        """Retrieve full inventory via SOAP."""
        output = self.get_credential('full_output', 'seawide_inventory_full.csv')
        envelope = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:sea="http://seawide.com">
  <soapenv:Header/>
  <soapenv:Body>
    <sea:GetInventoryFull>
      <sea:Key>{key}</sea:Key>
      <sea:FullAccountNo>{account}</sea:FullAccountNo>
    </sea:GetInventoryFull>
  </soapenv:Body>
</soapenv:Envelope>'''
        req = urllib.request.Request(
            'https://api.seawide.com/inventory.asmx',
            data=envelope.encode('utf-8'),
            headers={'Content-Type': 'text/xml; charset=utf-8',
                    'SOAPAction': 'http://seawide.com/GetInventoryFull'},
        )
        try:
            with urllib.request.urlopen(req) as resp:
                xml_data = resp.read()
            rows = _parse_dataset(xml_data)
            if rows:
                with open(output, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)
                logging.info('Saved Seawide full inventory to %s', output)
            else:
                logging.warning('No data returned from Seawide full inventory')
        except Exception as exc:
            logging.exception('Failed to fetch Seawide SOAP full inventory: %s', exc)

    def test_connection(self) -> None:
        """Attempt to connect to SOAP or FTP and report the result."""
        account = self.get_credential('account_number')
        key = self.get_credential('api_key')
        if account and key:
            envelope = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:sea="http://seawide.com">
  <soapenv:Header/>
  <soapenv:Body>
    <sea:GetInventoryUpdates>
      <sea:Key>{key}</sea:Key>
      <sea:FullAccountNo>{account}</sea:FullAccountNo>
    </sea:GetInventoryUpdates>
  </soapenv:Body>
</soapenv:Envelope>'''
            req = urllib.request.Request(
                'https://api.seawide.com/inventory.asmx',
                data=envelope.encode('utf-8'),
                headers={'Content-Type': 'text/xml; charset=utf-8',
                        'SOAPAction': 'http://seawide.com/GetInventoryUpdates'},
            )
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    if resp.status == 200:
                        print('Connection successful')
                        logging.info('Seawide SOAP connection successful')
                        return
                    print('Connection failed: status', resp.status)
                    logging.warning('Seawide SOAP connection failed %s', resp.status)
                    return
            except Exception as exc:
                logging.exception('Seawide SOAP connection failed: %s', exc)
                print('Connection failed:', exc)
                return

        host = self.get_credential('host')
        user = self.get_credential('username')
        password = self.get_credential('password')
        port = int(self.get_credential('port', 21))
        protocol = self.get_credential('protocol', 'ftps').lower()
        if not host or not user or not password:
            logging.warning('Seawide FTP credentials missing')
            print('Missing credentials')
            return
        try:
            with (ftplib.FTP() if protocol == 'ftp' else ftplib.FTP_TLS()) as ftp:
                ftp.connect(host, port, timeout=10)
                ftp.login(user, password)
                if protocol != 'ftp':
                    ftp.prot_p()
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
            with (ftplib.FTP() if protocol == 'ftp' else ftplib.FTP_TLS()) as ftp:
                ftp.connect(host, port)
                ftp.login(user, password)
                if protocol != 'ftp':
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
