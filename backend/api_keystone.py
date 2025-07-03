from flask import Flask, request
import uuid
import time
import json
import os
from .keystone_service import KeystoneSupplier
from automation_tool.cwr import CwrSupplier
from automation_tool.seawide import SeawideSupplier
from automation_tool import catalog
from datetime import datetime

app = Flask(__name__)

# store credentials separate from automation_tool data
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

ks = KeystoneSupplier()
cs = CwrSupplier()
sw = SeawideSupplier()

# simple in-memory task list
tasks: list[dict] = []

def _start_task(name: str, supplier: str) -> dict:
    task = {
        'id': str(uuid.uuid4()),
        'name': name,
        'supplier': supplier,
        'status': 'running',
        'progress': 0,
        'nextRun': '',
        'started': int(time.time()),
    }
    tasks.append(task)
    return task

def _finish_task(task: dict, ok: bool = True) -> None:
    task['status'] = 'completed' if ok else 'failed'
    task['progress'] = 100
    task['finished'] = int(time.time())

@app.post('/keystone/credentials')
def set_credentials():
    data = request.json or {}
    account = data.get('account_number', '')
    key = data.get('security_key', '')
    cred_store['account_number'] = account
    cred_store['security_key'] = key
    save_creds(cred_store)
    ks.set_credential('account_number', account)
    ks.set_credential('security_key', key)
    return {'status': 'saved'}

@app.post('/keystone/ftp')
def set_ftp():
    data = request.json or {}
    cred_store['ftp_user'] = data.get('user', '')
    cred_store['ftp_password'] = data.get('password', '')
    cred_store['ftp_remote_dir'] = data.get('remote_dir', '/')
    cred_store['remote_update_file'] = data.get('remote_file', 'Inventory.csv')
    save_creds(cred_store)
    ks.set_credential('ftp_user', cred_store['ftp_user'])
    ks.set_credential('ftp_password', cred_store['ftp_password'])
    ks.set_credential('ftp_remote_dir', cred_store['ftp_remote_dir'])
    ks.set_credential('remote_update_file', cred_store['remote_update_file'])
    return {'status': 'saved'}

@app.post('/keystone/location-map')
def set_location_map():
    mapping = request.json or {}
    ks.set_credential('location_map', mapping)
    return {'status': 'saved'}

@app.get('/keystone/inventory/partial')
def run_partial():
    task = _start_task('Keystone Inventory Sync', 'Keystone')
    success = ks.fetch_inventory_primary()
    _finish_task(task, success)
    return {'status': 'ok' if success else 'error'}

@app.get('/keystone/inventory/ftp-full')
def run_ftp_full():
    task = _start_task('Keystone FTP Inventory', 'Keystone')
    try:
        ks.fetch_inventory_secondary()
        ok = True
    except Exception:
        ok = False
    _finish_task(task, ok)
    return {'status': 'done' if ok else 'error'}

@app.get('/keystone/inventory/full')
def run_full():
    task = _start_task('Keystone Full Inventory', 'Keystone')
    try:
        ks.fetch_inventory_full()
        ok = True
    except Exception:
        ok = False
    _finish_task(task, ok)
    return {'status': 'done' if ok else 'error'}

@app.post('/keystone/schedule/partial')
def sched_partial():
    data = request.json or {}
    interval = data.get('interval')
    # scheduling not implemented; acknowledge value
    return {'status': 'scheduled', 'interval': interval}

@app.post('/keystone/schedule/full')
def sched_full():
    data = request.json or {}
    interval = data.get('interval')
    return {'status': 'scheduled', 'interval': interval}

@app.get('/keystone/catalog/run')
def run_catalog():
    task = _start_task('Keystone Catalog Sync', 'Keystone')
    try:
        ks.fetch_catalog()
        ok = True
    except Exception:
        ok = False
    _finish_task(task, ok)
    return {'status': 'done' if ok else 'error'}

@app.post('/keystone/schedule/catalog')
def sched_catalog():
    data = request.json or {}
    interval = data.get('interval')
    return {'status': 'scheduled', 'interval': interval}

@app.get('/keystone/catalog')
def list_catalog():
    rows = catalog.load_rows(ks.name)
    return {'rows': rows}

@app.delete('/keystone/catalog/<sku>')
def delete_sku(sku):
    catalog.delete_sku(ks.name, sku)
    return {'status': 'deleted'}

@app.post('/keystone/catalog/delete-file')
def delete_file():
    path = request.json.get('path') if request.json else ''
    if path:
        catalog.delete_from_file(ks.name, path)
    return {'status': 'done'}

@app.get('/keystone/upload-mli')
def upload_mli():
    ks.upload_multi_location_inventory()
    return {'status': 'done'}

@app.get('/keystone/test')
def test_conn():
    ks.test_connection()
    return {'status': 'done'}

@app.get('/suppliers/status')
def suppliers_status():
    data = []
    for sup in (ks, cs, sw):
        data.append(sup.status())
    return {'suppliers': data}

@app.get('/tasks')
def list_tasks():
    return {'tasks': tasks}

if __name__ == '__main__':
    app.run(debug=True)
