import logging
import urllib.request
import xml.etree.ElementTree as ET
import csv
import os
from .base import Supplier
from . import catalog


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

class KeystoneSupplier(Supplier):
    """Keystone Automotive supplier implementation."""
    def __init__(self):
        super().__init__('Keystone', 'keystone.json')

    def fetch_inventory(self) -> None:
        """Retrieve incremental inventory with warehouse breakdown."""
        account = self.get_credential('account_number')
        key = self.get_credential('security_key')
        output = self.get_credential('output', 'keystone_inventory_update.csv')
        if not account or not key:
            logging.warning('Keystone credentials missing')
            return

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
                'SOAPAction': 'http://eKeystone.com/GetInventoryUpdates',
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
            else:
                logging.warning('No data returned from Keystone update')
        except Exception as exc:
            logging.exception('Failed to fetch Keystone inventory: %s', exc)

    def fetch_inventory_full(self) -> None:
        """Retrieve the full Keystone inventory and store it as CSV."""
        account = self.get_credential('account_number')
        key = self.get_credential('security_key')
        output = self.get_credential('full_output', 'keystone_inventory_full.csv')
        if not account or not key:
            logging.warning('Keystone credentials missing')
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
                'SOAPAction': 'http://eKeystone.com/GetInventoryFull',
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
            else:
                logging.warning('No data returned from Keystone')
        except Exception as exc:
            logging.exception('Failed to fetch Keystone full inventory: %s', exc)

    def _ftp_connect(self):
        host = self.get_credential('ftp_host')
        user = self.get_credential('ftp_user')
        password = self.get_credential('ftp_password')
        port = int(self.get_credential('ftp_port', 21))
        protocol = self.get_credential('ftp_protocol', 'ftps').lower()
        if not host or not user or not password:
            return None
        try:
            import ftplib
            if protocol == 'ftp':
                ftp = ftplib.FTP()
            else:
                ftp = ftplib.FTP_TLS()
            ftp.connect(host, port, timeout=10)
            ftp.login(user, password)
            if isinstance(ftp, ftplib.FTP_TLS):
                ftp.prot_p()
            return ftp
        except Exception as exc:
            logging.exception('Keystone FTP connection failed: %s', exc)
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
                'SOAPAction': 'http://eKeystone.com/GetInventoryQuantityFull',
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
