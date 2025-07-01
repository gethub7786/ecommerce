import logging
import urllib.request
import os
from .base import Supplier
from . import catalog

class KeystoneSupplier(Supplier):
    """Keystone Automotive supplier implementation."""
    def __init__(self):
        super().__init__('Keystone', 'keystone.json')

    def fetch_inventory(self) -> None:
        account = self.get_credential('account_number')
        key = self.get_credential('security_key')
        if not account or not key:
            logging.warning('Keystone credentials missing')
            return

        envelope = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ekey="http://eKeystone.com">
  <soapenv:Header/>
  <soapenv:Body>
    <ekey:GetInventoryQuantityUpdates>
      <ekey:Key>{key}</ekey:Key>
      <ekey:FullAccountNo>{account}</ekey:FullAccountNo>
    </ekey:GetInventoryQuantityUpdates>
  </soapenv:Body>
</soapenv:Envelope>'''

        req = urllib.request.Request(
            'http://order.ekeystone.com/wselectronicorder/electronicorder.asmx',
            data=envelope.encode('utf-8'),
            headers={
                'Content-Type': 'text/xml; charset=utf-8',
                'SOAPAction': 'http://eKeystone.com/GetInventoryQuantityUpdates',
            },
        )
        try:
            with urllib.request.urlopen(req) as resp:
                data = resp.read()
            logging.info('Downloaded %s bytes of Keystone inventory', len(data))
        except Exception as exc:
            logging.exception('Failed to fetch Keystone inventory: %s', exc)

    def test_connection(self) -> None:
        """Simple connection test to the SOAP endpoint."""
        try:
            with urllib.request.urlopen('http://order.ekeystone.com/wselectronicorder/electronicorder.asmx', timeout=10) as resp:
                if resp.status == 200:
                    print('Connection successful')
                    logging.info('Keystone connection successful')
                else:
                    print('Connection failed: status', resp.status)
                    logging.warning('Keystone connection failed status %s', resp.status)
        except Exception as exc:
            logging.exception('Keystone connection failed: %s', exc)
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
