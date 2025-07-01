import logging
import urllib.request
from .base import Supplier

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
