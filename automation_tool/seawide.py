import logging
import ftplib
import ssl
import os
import csv
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from .base import Supplier, SFTPWrapper, ImplicitFTP_TLS
from .multi_location import convert_to_amazon
from . import catalog
from .keystone import _parse_dataset, _soap_error_message

SOAP_URL = "http://order.ekeystone.com/wselectronicorder/electronicorder.asmx"

# Fixed FTP connection details for Seawide
HOST = "ftp.ekeystone.com"  # Seawide shares the same host
PORT = 990  # implicit FTPS

class SeawideSupplier(Supplier):
    """Seawide supplier implementation."""
    def __init__(self):
        super().__init__('Seawide', 'seawide.json')

    def configure_credentials(self) -> None:
        """Prompt for SOAP API credentials."""
        account = input('Account Number: ')
        key = input('API Key: ')
        self.set_credential('account_number', account)
        self.set_credential('api_key', key)
        print('Credentials saved.')

    def configure_ftp(self) -> None:
        """Prompt for FTP access details."""
        user = input('FTP User: ')
        password = input('FTP Password: ')
        remote_dir = input('Remote Folder (default /): ') or '/'
        remote_file = input('Remote File (default Inventory.csv): ') or 'Inventory.csv'
        self.set_credential('ftp_user', user)
        self.set_credential('ftp_password', password)
        self.set_credential('ftp_remote_dir', remote_dir)
        self.set_credential('remote_update_file', remote_file)
        print('FTP credentials saved.')

    def configure_location_mapping(self) -> None:
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

    # Primary method: SOAP API inventory tracking
    def fetch_inventory_primary(self) -> bool:
        account = self.get_credential('account_number')
        key = self.get_credential('api_key')
        if not account or not key:
            msg = 'Seawide API credentials missing'
            logging.warning(msg)
            print(msg)
            return False
        return self._fetch_inventory_update_soap(account, key)

    # Backwards compatible alias
    def fetch_inventory(self) -> None:
        if not self.fetch_inventory_primary():
            logging.info('Falling back to Seawide FTP inventory update')
            self.fetch_inventory_secondary()

    # Secondary method: FTP download
    def fetch_inventory_secondary(self) -> None:
        """Retrieve the inventory update file via FTP with progress output."""
        remote_file = self.get_credential('remote_update_file', 'Inventory.csv')
        if not remote_file:
            remote_file = 'Inventory.csv'
            self.set_credential('remote_update_file', remote_file)
        remote_dir = self.get_credential('ftp_remote_dir', '/')
        remote_path = f"{remote_dir.rstrip('/')}/{remote_file}" if remote_dir else remote_file

        ftp = self._ftp_connect()
        if not ftp:
            msg = 'Seawide FTP credentials missing or connection failed'
            print(msg)
            logging.warning(msg)
            self.configure_ftp()
            ftp = self._ftp_connect()
            if not ftp:
                logging.warning('Seawide FTP connection still failed')
                return

        output = self.get_credential('output', 'seawide_inventory_update.csv')
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
            logging.info('Downloaded Seawide inventory update to %s', output)

            # parse file to update catalog
            try:
                with open(output, newline='') as f:
                    rows = list(csv.DictReader(f))
                if rows:
                    catalog.save_rows(self.name, rows)
                    logging.info('Updated %s catalog from FTP download', self.name)
            except Exception as exc:
                logging.warning('Failed to parse downloaded inventory: %s', exc)

        except Exception as exc:
            logging.exception('Failed to fetch Seawide inventory: %s', exc)
            print('Error downloading Seawide inventory via FTP:', exc)
        finally:
            try:
                ftp.quit()
            except Exception:
                pass

    def upload_multi_location_inventory(self) -> None:
        """Convert update file to Amazon multi-location JSON."""
        input_path = Path(self.get_credential('output', 'seawide_inventory_update.csv'))
        output_path = Path(self.get_credential('ml_output', 'seawide_amazon_multilocation_inventory.json'))
        mapping = self.get_credential('location_map', {})
        try:
            count = convert_to_amazon(input_path, output_path, mapping, sku_field='VCPN', delimiter=',')
            print(f'Converted {count} SKUs to {output_path}')
        except Exception as exc:
            logging.exception('Seawide multi-location conversion failed: %s', exc)
            print('Conversion failed:', exc)

    def fetch_inventory_full(self) -> None:
        """Download the full inventory file via SOAP or FTP."""
        account = self.get_credential('account_number')
        key = self.get_credential('api_key')
        if account and key:
            self._fetch_inventory_full_soap(account, key)
            return

        remote_file = self.get_credential('remote_full_file')
        if not remote_file:
            remote_file = input('Remote full inventory file: ')
            self.set_credential('remote_full_file', remote_file)
        remote_dir = self.get_credential('ftp_remote_dir', '')
        remote_path = f"{remote_dir.rstrip('/')}/{remote_file}" if remote_dir else remote_file

        ftp = self._ftp_connect()
        if not ftp:
            msg = 'Seawide FTP credentials missing or connection failed'
            print(msg)
            logging.warning(msg)
            self.configure_ftp()
            ftp = self._ftp_connect()
            if not ftp:
                logging.warning('Seawide FTP connection still failed')
                return

        output = self.get_credential('full_output', 'seawide_inventory_full.csv')
        try:
            with open(output, 'wb') as f:
                ftp.retrbinary(f'RETR {remote_path}', f.write)
            logging.info('Downloaded Seawide full inventory to %s', output)
        except Exception as exc:
            logging.exception('Failed to fetch Seawide full inventory: %s', exc)
            print('Error downloading Seawide full inventory via FTP:', exc)
        finally:
            try:
                ftp.quit()
            except Exception:
                pass

    def _ftp_connect(self):
        """Connect to Seawide's implicit FTPS server."""
        user = self.get_credential('ftp_user')
        password = self.get_credential('ftp_password')
        if not user or not password:
            print('Missing FTP credentials')
            return None
        host = HOST
        port = PORT
        try:
            ftp = ImplicitFTP_TLS()
            ftp.ssl_version = ssl.PROTOCOL_TLSv1_2
            ftp.connect(host, port, timeout=30)
            try:
                ftp.login(user, password)
            except ftplib.error_perm as exc:
                if '530' in str(exc):
                    print('Login failed (530). Credentials incorrect.')
                    return None
                raise
            # Seawide also uses implicit FTPS so the socket is wrapped in TLS
            # as soon as we connect. The server does not expect a PROT
            # command, so just enable passive mode for data transfers.
            ftp.set_pasv(True)
            return ftp
        except Exception as exc:
            logging.exception('Seawide FTP connection failed: %s', exc)
            print('Seawide FTP connection failed:', exc)
            return None

    def _fetch_inventory_update_soap(self, account: str, key: str) -> bool:
        """Retrieve inventory updates via SOAP."""
        output = self.get_credential('output', 'seawide_inventory_update.csv')
        envelope = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ekey="http://eKeystone.com">
  <soapenv:Header/>
  <soapenv:Body>
    <ekey:GetInventoryUpdates>
      <ekey:Key>{key}</ekey:Key>
      <ekey:FullAccountNo>{account}</ekey:FullAccountNo>
    </ekey:GetInventoryUpdates>
  </soapenv:Body>
</soapenv:Envelope>'''
        req = urllib.request.Request(
            SOAP_URL,
            data=envelope.encode('utf-8'),
            headers={
                'Content-Type': 'text/xml; charset=utf-8',
                'SOAPAction': '"http://eKeystone.com/GetInventoryUpdates"',
            },
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
                return True
            err = _soap_error_message(xml_data)
            if err:
                logging.warning('Seawide SOAP error: %s', err)
                print('Error Description', err)
            else:
                msg = 'No data returned from Seawide update'
                logging.warning(msg)
                print(msg)
        except Exception as exc:
            logging.exception('Failed to fetch Seawide SOAP update: %s', exc)
            print('Error fetching Seawide inventory via SOAP:', exc)
        return False

    def _fetch_inventory_full_soap(self, account: str, key: str) -> None:
        """Retrieve full inventory via SOAP."""
        output = self.get_credential('full_output', 'seawide_inventory_full.csv')
        envelope = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ekey="http://eKeystone.com">
  <soapenv:Header/>
  <soapenv:Body>
    <ekey:GetInventoryFull>
      <ekey:Key>{key}</ekey:Key>
      <ekey:FullAccountNo>{account}</ekey:FullAccountNo>
    </ekey:GetInventoryFull>
  </soapenv:Body>
</soapenv:Envelope>'''
        req = urllib.request.Request(
            SOAP_URL,
            data=envelope.encode('utf-8'),
            headers={
                'Content-Type': 'text/xml; charset=utf-8',
                'SOAPAction': '"http://eKeystone.com/GetInventoryFull"',
            },
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
                err = _soap_error_message(xml_data)
                if err:
                    logging.warning('Seawide SOAP error: %s', err)
                    print('Error Description', err)
                else:
                    msg = 'No data returned from Seawide full inventory'
                    logging.warning(msg)
                    print(msg)
        except Exception as exc:
            logging.exception('Failed to fetch Seawide SOAP full inventory: %s', exc)
            print('Error fetching Seawide full inventory via SOAP:', exc)

    def test_connection(self) -> None:
        """Attempt to connect to FTP first, then SOAP."""
        ftp = self._ftp_connect()
        if ftp:
            ftp.quit()
            print('FTP connection successful')
            logging.info('Seawide FTP connection successful')
            return

        account = self.get_credential('account_number')
        key = self.get_credential('api_key')
        if account and key:
            envelope = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ekey="http://eKeystone.com">
  <soapenv:Header/>
  <soapenv:Body>
    <ekey:GetInventoryUpdates>
      <ekey:Key>{key}</ekey:Key>
      <ekey:FullAccountNo>{account}</ekey:FullAccountNo>
    </ekey:GetInventoryUpdates>
  </soapenv:Body>
</soapenv:Envelope>'''
            req = urllib.request.Request(
                SOAP_URL,
                data=envelope.encode('utf-8'),
                headers={
                    'Content-Type': 'text/xml; charset=utf-8',
                    'SOAPAction': '"http://eKeystone.com/GetInventoryUpdates"',
                },
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
        else:
            print('Missing credentials')

    def fetch_catalog(self) -> None:
        """Download the vendor catalog from FTP."""
        remote = self.get_credential('catalog_remote', 'catalog.csv')
        out_dir = self.get_credential('catalog_dir', '.')
        name = self.get_credential('catalog_name', 'seawide_catalog.csv')
        mapping_file = self.get_credential('mapping_file')
        output = os.path.join(out_dir, name)

        ftp = self._ftp_connect()
        if not ftp:
            logging.warning('Seawide FTP credentials missing')
            print('Missing credentials')
            return

        os.makedirs(out_dir, exist_ok=True)
        try:
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
        finally:
            try:
                ftp.quit()
            except Exception:
                pass
