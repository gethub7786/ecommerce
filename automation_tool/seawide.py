import logging
import ftplib
from .base import Supplier

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
