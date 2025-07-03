import logging
import urllib.request
import xml.etree.ElementTree as ET
import csv
import os
import ssl
import time
from pathlib import Path
from .base import Supplier, SFTPWrapper, ImplicitFTP_TLS
from .multi_location import convert_to_amazon
from . import catalog

# Fixed FTP connection details for Keystone
HOST = "ftp.ekeystone.com"
PORT = 990  # implicit FTPS


def _parse_dataset(xml_data: bytes) -> list:
    """Parse Keystone SOAP dataset XML into rows."""
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError:
        return []

    diffgram = root.find('.//{urn:schemas-microsoft-com:xml-diffgram-v1}diffgram')
    if diffgram is None:
        return []
    dataset = diffgram.find('NewDataSet')
    if dataset is None:
        return []
    rows = []
    for table in dataset.findall('Table'):
        row = {child.tag: (child.text or '') for child in table}
        rows.append(row)
    return rows


def _soap_error_message(xml_data: bytes) -> str | None:
    """Return a user friendly SOAP error if present in the response."""
    text = xml_data.decode("utf-8", errors="ignore")
    if "You are not authorized to use this function" in text:
        return (
            "Insufficient permissions. The account number/security key/IP address "
            "combination provided has not been granted access to the Electronic "
            "Order API.\nSOAP exception: \"*** You are not authorized to use "
            "this function ***\""
        )
    if "Illegal use of this web service" in text:
        return (
            "Invalid credentials. The security key provided is invalid.\nSOAP "
            "exception: \"*** Illegal use of this web service !!! ***\""
        )
    return None

class KeystoneSupplier(Supplier):
    """Keystone Automotive supplier implementation."""
    def __init__(self):
        super().__init__('Keystone', 'keystone.json')

    def configure_credentials(self) -> None:
        """Prompt for SOAP credentials."""
        account = input('Account Number: ')
        key = input('Security Key: ')
        self.set_credential('account_number', account)
        self.set_credential('security_key', key)
        print('Credentials saved.')

    def configure_ftp(self) -> None:
        """Prompt for FTP authentication details."""
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

    # Primary method: SOAP API inventory tracking
    def fetch_inventory_primary(self) -> bool:
        """Retrieve incremental inventory with warehouse breakdown."""
        account = self.get_credential('account_number')
        key = self.get_credential('security_key')
        output = self.get_credential('output', 'keystone_inventory_update.csv')
        if not account or not key:
            msg = 'Keystone credentials missing'
            logging.warning(msg)
            print(msg)
            return False

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
            'http://order.ekeystone.com/wselectronicorder/electronicorder.asmx',
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
                logging.info('Saved Keystone inventory update to %s', output)
                self.set_credential('last_sync', int(time.time()))
                self.set_credential('item_count', len(rows))
                return True
            err = _soap_error_message(xml_data)
            if err:
                logging.warning('Keystone SOAP error: %s', err)
                print('Error Description', err)
            else:
                msg = 'No data returned from Keystone update'
                logging.warning(msg)
                print(msg)
        except Exception as exc:
            logging.exception('Failed to fetch Keystone inventory: %s', exc)
            print('Error fetching Keystone inventory via SOAP:', exc)
        return False

    # Backwards compatible alias
    def fetch_inventory(self) -> None:
        if not self.fetch_inventory_primary():
            logging.info('Falling back to Keystone FTP inventory update')
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
            msg = 'Keystone FTP credentials missing or connection failed'
            print(msg)
            logging.warning(msg)
            self.configure_ftp()
            ftp = self._ftp_connect()
            if not ftp:
                logging.warning('Keystone FTP connection still failed')
                return

        output = self.get_credential('output', 'keystone_inventory_ftp.csv')
        try:
            total = ftp.size(remote_path)
        except Exception:
            total = None

        downloaded = 0
        try:
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
            logging.info('Downloaded Keystone inventory update via FTP to %s', output)

            # parse downloaded CSV into the catalog store
            try:
                with open(output, newline='') as f:
                    rows = list(csv.DictReader(f))
                if rows:
                    catalog.save_rows(self.name, rows)
                    self.set_credential('last_sync', int(time.time()))
                    self.set_credential('item_count', len(rows))
                    logging.info('Updated %s catalog from FTP download', self.name)
            except Exception as exc:
                logging.warning('Failed to parse downloaded inventory: %s', exc)

        except Exception as exc:
            logging.exception('Failed to fetch Keystone FTP inventory: %s', exc)
            print('Error downloading Keystone inventory via FTP:', exc)
        finally:
            try:
                ftp.quit()
            except Exception:
                pass

    def fetch_inventory_full(self) -> None:
        """Retrieve the full Keystone inventory and store it as CSV."""
        account = self.get_credential('account_number')
        key = self.get_credential('security_key')
        output = self.get_credential('full_output', 'keystone_inventory_full.csv')
        if not account or not key:
            msg = 'Keystone credentials missing'
            logging.warning(msg)
            print(msg)
            return

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
            'http://order.ekeystone.com/wselectronicorder/electronicorder.asmx',
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
                logging.info('Saved Keystone full inventory to %s', output)
                self.set_credential('last_sync', int(time.time()))
                self.set_credential('item_count', len(rows))
            else:
                err = _soap_error_message(xml_data)
                if err:
                    logging.warning('Keystone SOAP error: %s', err)
                    print('Error Description', err)
                else:
                    msg = 'No data returned from Keystone'
                    logging.warning(msg)
                    print(msg)
        except Exception as exc:
            logging.exception('Failed to fetch Keystone full inventory: %s', exc)
            print('Error fetching Keystone full inventory:', exc)

    def _ftp_connect(self):
        """Connect to Keystone's implicit FTPS server."""
        user = self.get_credential('ftp_user')
        password = self.get_credential('ftp_password')
        if not user or not password:
            print('Missing FTP credentials')
            return None
        host = HOST
        port = PORT
        try:
            import ftplib
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
            # Keystone uses implicit FTPS so the control socket is already
            # wrapped with TLS. The server does not support a separate
            # PROT negotiation, so skip ftp.prot_p() and simply enable
            # passive mode for the data connection.
            ftp.set_pasv(True)
            return ftp
        except Exception as exc:
            logging.exception('Keystone FTP connection failed: %s', exc)
            print('Keystone FTP connection failed:', exc)
            return None

    def test_connection(self) -> None:
        """Test SOAP and optionally FTP connectivity."""
        ftp = self._ftp_connect()
        if ftp:
            ftp.quit()
            print('FTP connection successful')
            logging.info('Keystone FTP connection successful')
            return

        try:
            with urllib.request.urlopen(
                'http://order.ekeystone.com/wselectronicorder/electronicorder.asmx',
                timeout=10,
            ) as resp:
                if resp.status == 200:
                    print('Connection successful')
                    logging.info('Keystone SOAP connection successful')
                else:
                    print('Connection failed: status', resp.status)
                    logging.warning(
                        'Keystone SOAP connection failed status %s', resp.status
                    )
        except Exception as exc:
            logging.exception('Keystone SOAP connection failed: %s', exc)
            print('Connection failed:', exc)

    def fetch_catalog(self) -> None:
        """Download the full catalog via SOAP and store it."""
        account = self.get_credential('account_number')
        key = self.get_credential('security_key')
        out_dir = self.get_credential('catalog_dir', '.')
        name = self.get_credential('catalog_name', 'keystone_catalog.xml')
        output = os.path.join(out_dir, name)
        if not account or not key:
            logging.warning('Keystone credentials missing')
            return
        os.makedirs(out_dir, exist_ok=True)
        envelope = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ekey="http://eKeystone.com">
  <soapenv:Header/>
  <soapenv:Body>
    <ekey:GetInventoryQuantityFull>
      <ekey:Key>{key}</ekey:Key>
      <ekey:FullAccountNo>{account}</ekey:FullAccountNo>
    </ekey:GetInventoryQuantityFull>
  </soapenv:Body>
</soapenv:Envelope>'''
        req = urllib.request.Request(
            'http://order.ekeystone.com/wselectronicorder/electronicorder.asmx',
            data=envelope.encode('utf-8'),
            headers={
                'Content-Type': 'text/xml; charset=utf-8',
                'SOAPAction': '"http://eKeystone.com/GetInventoryQuantityFull"',
            },
        )
        try:
            with urllib.request.urlopen(req) as resp:
                data = resp.read()
            with open(output, 'wb') as f:
                f.write(data)
            logging.info('Downloaded Keystone catalog to %s', output)
            # placeholder parse: store minimal row
            catalog.save_rows(self.name, [{'SKU': 'sample', 'DATA': 'see file'}])
            print('Catalog saved to', catalog.catalog_path(self.name))
        except Exception as exc:
            logging.exception('Failed to fetch Keystone catalog: %s', exc)
            print('Catalog download failed:', exc)

    def upload_multi_location_inventory(self) -> None:
        """Convert update file to Amazon multi-location JSON."""
        input_path = Path(self.get_credential('output', 'keystone_inventory_update.csv'))
        output_path = Path(self.get_credential('ml_output', 'keystone_amazon_multilocation_inventory.json'))
        mapping = self.get_credential('location_map', {})
        try:
            count = convert_to_amazon(input_path, output_path, mapping, sku_field='VCPN', delimiter=',')
            print(f'Converted {count} SKUs to {output_path}')
        except Exception as exc:
            logging.exception('Keystone multi-location conversion failed: %s', exc)
            print('Conversion failed:', exc)
