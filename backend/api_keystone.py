from flask import Flask, request
import uuid
import time
import json
import os
from automation_tool.keystone import KeystoneSupplier
from automation_tool import catalog
from datetime import datetime, timedelta
import copy
import threading
from threading import Lock

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
# register supplier in shared list
app.config.setdefault('SUPPLIERS', [])
app.config['SUPPLIERS'].append(ks)

# simple in-memory task list
tasks: list[dict] = []
_tasks_lock = Lock()

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
    with _tasks_lock:
        tasks.append(task)
    return task

def _finish_task(task: dict, ok: bool = True) -> None:
    with _tasks_lock:
        task['status'] = 'completed' if ok else 'failed'
        task['progress'] = 100
        task['finished'] = int(time.time())

def _update_progress(task_id, percent):
    with _tasks_lock:
        for t in tasks:
            if t['id'] == task_id:
                t['progress'] = percent
                print(f"[DEBUG] Progress for {task_id}: {percent}%")
                break

# ---------------------------------------------------------------------------
# Helper: register or update a scheduled task so the UI can display it
# ---------------------------------------------------------------------------


def _register_schedule(name: str, supplier: str, interval: int | None):
    """Add or update a task entry with status 'scheduled'.

    If the task already exists (same name & supplier & status=='scheduled'),
    update its interval / nextRun fields; otherwise append a new record.
    """
    now = int(time.time())
    next_run_ts = now + int(interval or 0) if interval else None
    next_run_str = (
        datetime.fromtimestamp(next_run_ts).strftime('%Y-%m-%d %H:%M')
        if next_run_ts else ''
    )
    # try to update existing scheduled task
    for t in tasks:
        if (
            t.get('name') == name
            and t.get('supplier') == supplier
            and t.get('status') == 'scheduled'
        ):
            t['interval'] = interval
            t['nextRun'] = next_run_str
            return t

    task = {
        'id': str(uuid.uuid4()),
        'name': name,
        'supplier': supplier,
        'status': 'scheduled',
        'progress': 0,
        'nextRun': next_run_str,
        'interval': interval,
        'created': now,
    }
    with _tasks_lock:
        tasks.append(task)
    return task

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

# new endpoint to retrieve stored credentials
@app.get('/keystone/credentials')
def get_credentials():
    return {
        'account_number': ks.get_credential('account_number', ''),
        'security_key': ks.get_credential('security_key', ''),
    }

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

# ---------------------------------------------------------------------------
# New endpoint: fetch saved FTP credentials
# ---------------------------------------------------------------------------

@app.get('/keystone/ftp')
def get_ftp():
    """Return stored FTP credentials so the UI can pre-fill the form."""
    return {
        'user': cred_store.get('ftp_user', ''),
        'password': cred_store.get('ftp_password', ''),
        'remote_dir': cred_store.get('ftp_remote_dir', '/'),
        'remote_file': cred_store.get('remote_update_file', 'Inventory.csv'),
    }

@app.post('/keystone/location-map')
def set_location_map():
    mapping = request.json or {}
    # Persist to local credential store so mapping survives restarts
    cred_store['location_map'] = mapping
    save_creds(cred_store)
    ks.set_credential('location_map', mapping)  # type: ignore[arg-type]
    return {'status': 'saved'}

# ---------------------------------------------------------------------------
# New endpoint: fetch stored location mapping
# ---------------------------------------------------------------------------

@app.get('/keystone/location-map')
def get_location_map():
    """Return the saved column→source mapping so UI can pre-populate the grid."""
    return cred_store.get('location_map', {})

@app.get('/keystone/inventory/partial')
def run_partial():
    task = _start_task('Keystone Inventory Sync', 'Keystone')
    def worker():
        try:
            ks.fetch_inventory_secondary(progress_cb=lambda p: _update_progress(task['id'], p))
            _finish_task(task, True)
        except Exception:
            _finish_task(task, False)
    threading.Thread(target=worker, daemon=True).start()
    return {'status': 'started', 'task_id': task['id']}

@app.get('/keystone/inventory/ftp-full')
def run_ftp_full():
    task = _start_task('Keystone FTP Inventory', 'Keystone')
    def worker():
        try:
            ks.fetch_inventory_secondary(progress_cb=lambda p: _update_progress(task['id'], p))
            _finish_task(task, True)
        except Exception:
            _finish_task(task, False)
    threading.Thread(target=worker, daemon=True).start()
    return {'status': 'started', 'task_id': task['id']}

@app.get('/keystone/inventory/full')
def run_full():
    task = _start_task('Keystone Full Inventory', 'Keystone')
    def worker():
        try:
            ks.fetch_inventory_secondary(progress_cb=lambda p: _update_progress(task['id'], p))
            _finish_task(task, True)
        except Exception:
            _finish_task(task, False)
    threading.Thread(target=worker, daemon=True).start()
    return {'status': 'started', 'task_id': task['id']}

@app.post('/keystone/schedule/partial')
def sched_partial():
    data = request.json or {}
    interval = data.get('interval')
    cred_store['partial_interval'] = interval
    save_creds(cred_store)
    _register_schedule('Keystone Partial Inventory (scheduled)', 'Keystone', interval)
    return {'status': 'scheduled', 'interval': interval}

# fetch saved partial schedule
@app.get('/keystone/schedule/partial')
def get_sched_partial():
    return {'interval': cred_store.get('partial_interval')}

@app.post('/keystone/schedule/full')
def sched_full():
    data = request.json or {}
    interval = data.get('interval')
    cred_store['full_interval'] = interval
    save_creds(cred_store)
    _register_schedule('Keystone Full Inventory (scheduled)', 'Keystone', interval)
    return {'status': 'scheduled', 'interval': interval}

@app.get('/keystone/schedule/full')
def get_sched_full():
    return {'interval': cred_store.get('full_interval')}

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
    cred_store['catalog_interval'] = interval
    save_creds(cred_store)
    _register_schedule('Keystone Catalog Sync (scheduled)', 'Keystone', interval)
    return {'status': 'scheduled', 'interval': interval}

@app.get('/keystone/schedule/catalog')
def get_sched_catalog():
    return {'interval': cred_store.get('catalog_interval')}

@app.get('/keystone/catalog')
def list_catalog():
    limit = request.args.get('limit', default=50, type=int)
    start = request.args.get('start', default=0, type=int)
    rows = catalog.load_rows(ks.name)
    rows = rows[start:start+limit] if limit>0 else rows[start:]
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
    suppliers = app.config.get('SUPPLIERS', [ks])
    data = [s.status() for s in suppliers]
    return {'suppliers': data}

@app.get('/tasks')
def list_tasks():
    with _tasks_lock:
        data = copy.deepcopy(tasks)
    print('[DEBUG] /tasks response:', data)
    return {'tasks': data}

# ---------------------------------------------------------------------------
# Catalog aggregation endpoints (across all suppliers)
# ---------------------------------------------------------------------------

@app.get('/catalog/overview')
def catalog_overview():
    """Return summary counts for each supplier catalog."""
    data = []
    suppliers = app.config.get('SUPPLIERS', [ks])
    for sup in suppliers:
        rows = catalog.load_rows(sup.name)
        active = len(rows)
        pending = 0  # placeholder; implement your logic
        error = 0
        last_sync_ts = sup.get_credential('last_sync', 0) or 0
        last_sync = '' if not last_sync_ts else datetime.fromtimestamp(int(last_sync_ts)).strftime('%Y-%m-%d %H:%M')
        data.append({
            'supplier': sup.name,
            'active': active,
            'pending': pending,
            'error': error,
            'last_updated': last_sync,
        })
    return {'overview': data}


@app.get('/catalog/rows')
def catalog_rows():
    """Return combined catalog rows across suppliers with pagination and filtering by brand/supplier."""
    start = int(request.args.get('start', 0))
    limit = int(request.args.get('limit', 50))
    q = request.args.get('q', '').lower()
    brand_filter = request.args.get('brand', '').lower()
    supplier_filter = request.args.get('supplier', '').lower()

    rows_combined: list[dict] = []
    suppliers = app.config.get('SUPPLIERS', [ks])
    for sup in suppliers:
        # If supplier filter is set, skip suppliers that don't match
        if supplier_filter and supplier_filter != sup.name.lower():
            continue
        for row in catalog.load_rows(sup.name):
            item = {
                'sku': row.get('VCPN') or row.get('SKU') or row.get('AMAZON SKU'),
                'name': row.get('LongDescription') or row.get('ProductName') or '',
                'supplier': sup.name,
                'brand': row.get('VendorName') or row.get('Brand') or row.get('Manufacturer') or row.get('MFG') or '',
                'stock': row.get('TotalQty') or row.get('Qty') or 0,
                'status': 'Active',
                **row,
            }
            # Text search filter
            if q and q not in str(item['sku']).lower() and q not in str(item['name']).lower():
                continue
            # Brand filter
            if brand_filter and brand_filter != str(item['brand']).lower():
                continue
            rows_combined.append(item)

    rows_combined.sort(key=lambda r: str(r['sku']))
    # Pagination is applied after filtering
    slice_rows = rows_combined[start:start+limit] if limit>0 else rows_combined[start:]
    return {'rows': slice_rows}

@app.get('/catalog/filters')
def catalog_filters():
    """Return all unique brands and suppliers across all products (for filter dropdowns)."""
    brands_set = set()
    suppliers_set = set()
    all_suppliers = app.config.get('SUPPLIERS', [ks])
    for sup in all_suppliers:
        for row in catalog.load_rows(sup.name):
            # Collect brand from any possible field
            for field in ('VendorName', 'Brand', 'Manufacturer', 'MFG'):
                val = row.get(field)
                if val and str(val).strip() and str(val).strip().lower() != 'all':
                    brands_set.add(str(val).strip())
            # Supplier is always the supplier name
            if sup.name and str(sup.name).strip() and str(sup.name).strip().lower() != 'all':
                suppliers_set.add(str(sup.name).strip())
    brands = sorted(brands_set)
    suppliers = sorted(suppliers_set)
    print('[DEBUG] /catalog/filters brands:', brands)
    print('[DEBUG] /catalog/filters suppliers:', suppliers)
    return {'brands': brands, 'suppliers': suppliers}

# alias routes for frontend expectations
@app.get('/keystone/catalog/rows')
def _alias_rows():
    return catalog_rows()

@app.get('/keystone/catalog/overview')
def _alias_overview():
    return catalog_overview()

# Note: other supplier API modules will import this app and add their routes.

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=False)
