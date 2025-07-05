import os, sys, json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, request
from datetime import datetime
from automation_tool.keystone import KeystoneSupplier
from automation_tool import catalog
from .common import tasks, start_task, finish_task

app = Flask(__name__)

ks = KeystoneSupplier()

# ------------------------ Helpers ------------------------
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)
CRED_FILE = os.path.join(DATA_DIR, 'keystone_creds.json')

def load_creds() -> dict:
    if os.path.exists(CRED_FILE):
        try:
            with open(CRED_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_creds(data: dict) -> None:
    with open(CRED_FILE, 'w') as f:
        json.dump(data, f)

cred_store = load_creds()

# ------------------------ Routes -------------------------
@app.post('/keystone/credentials')
def set_credentials():
    data = request.json or {}
    cred_store['account_number'] = data.get('account_number', '')
    cred_store['security_key'] = data.get('security_key', '')
    save_creds(cred_store)
    ks.set_credential('account_number', cred_store['account_number'])
    ks.set_credential('security_key', cred_store['security_key'])
    return {'status': 'saved'}

@app.get('/keystone/credentials')
def get_credentials():
    return {
        'account_number': ks.get_credential('account_number', ''),
        'security_key': ks.get_credential('security_key', ''),
    }

@app.post('/keystone/ftp')
def set_ftp():
    data = request.json or {}
    ks.set_credential('ftp_user', data.get('user', ''))
    ks.set_credential('ftp_password', data.get('password', ''))
    ks.set_credential('ftp_remote_dir', data.get('remote_dir', '/'))
    ks.set_credential('remote_update_file', data.get('remote_file', 'Inventory.csv'))
    return {'status': 'saved'}

@app.post('/keystone/location-map')
def set_location_map():
    mapping = request.json or {}
    ks.set_credential('location_map', mapping)  # type: ignore[arg-type]
    return {'status': 'saved'}

@app.get('/keystone/inventory/partial')
def run_partial():
    task = start_task('Keystone Inventory Sync', 'Keystone')
    ok = ks.fetch_inventory_primary()
    finish_task(task, ok)
    return {'status': 'ok' if ok else 'error'}

@app.get('/keystone/inventory/full')
def run_full():
    task = start_task('Keystone Full Inventory', 'Keystone')
    try:
        ks.fetch_inventory_full()
        ok = True
    except Exception:
        ok = False
    finish_task(task, ok)
    return {'status': 'done' if ok else 'error'}

# ... replicate other routes as needed (FTP download, catalog, etc.) ...

@app.get('/suppliers/status')
def suppliers_status():
    return {'suppliers': [ks.status()]}

@app.get('/tasks')
def list_tasks():
    return {'tasks': tasks}

if __name__ == '__main__':
    app.run(port=5000) 