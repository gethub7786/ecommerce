from backend.api_keystone import app, _start_task, _finish_task, tasks  # type: ignore
from flask import request
from automation_tool.seawide import SeawideSupplier
from automation_tool import catalog

sw = SeawideSupplier()

# --------------------------- SEAWIDE ROUTES ---------------------------

@app.post('/seawide/credentials')
def seawide_set_credentials():
    data = request.json or {}
    account = data.get('account_number', '')
    key = data.get('api_key', '')
    sw.set_credential('account_number', account)
    sw.set_credential('api_key', key)
    return {'status': 'saved'}

# fetch saved credentials
@app.get('/seawide/credentials')
def seawide_get_credentials():
    return {
        'account_number': sw.get_credential('account_number', ''),
        'api_key': sw.get_credential('api_key', ''),
    }

@app.post('/seawide/ftp')
def seawide_set_ftp():
    data = request.json or {}
    sw.set_credential('ftp_user', data.get('user', ''))
    sw.set_credential('ftp_password', data.get('password', ''))
    sw.set_credential('ftp_remote_dir', data.get('remote_dir', '/'))
    sw.set_credential('remote_update_file', data.get('remote_file', 'Inventory.csv'))
    return {'status': 'saved'}

@app.post('/seawide/location-map')
def seawide_set_location_map():
    mapping = request.json or {}
    sw.set_credential('location_map', mapping)  # type: ignore[arg-type]
    return {'status': 'saved'}

# Inventory actions
@app.get('/seawide/inventory/partial')
def seawide_partial_inventory():
    task = _start_task('Seawide Inventory Sync', 'Seawide')
    try:
        sw.fetch_inventory_primary()
        ok = True
    except Exception:
        ok = False
    _finish_task(task, ok)
    return {'status': 'done' if ok else 'error'}

@app.get('/seawide/inventory/ftp-full')
def seawide_ftp_full():
    task = _start_task('Seawide FTP Inventory', 'Seawide')
    try:
        sw.fetch_inventory_secondary()
        ok = True
    except Exception:
        ok = False
    _finish_task(task, ok)
    return {'status': 'done' if ok else 'error'}

@app.get('/seawide/inventory/full')
def seawide_full_inventory():
    task = _start_task('Seawide Full Inventory', 'Seawide')
    try:
        sw.fetch_inventory_full()
        ok = True
    except Exception:
        ok = False
    _finish_task(task, ok)
    return {'status': 'done' if ok else 'error'}

# Schedule placeholders
@app.post('/seawide/schedule/partial')
@app.post('/seawide/schedule/full')
@app.post('/seawide/schedule/catalog')
def seawide_schedule_stub():
    data = request.json or {}
    interval = data.get('interval')
    return {'status': 'scheduled', 'interval': interval}

# Catalog management
@app.get('/seawide/catalog/run')
def seawide_run_catalog():
    task = _start_task('Seawide Catalog Sync', 'Seawide')
    try:
        sw.fetch_catalog()
        ok = True
    except Exception:
        ok = False
    _finish_task(task, ok)
    return {'status': 'done' if ok else 'error'}

@app.get('/seawide/catalog')
def seawide_list_catalog():
    rows = catalog.load_rows(sw.name)
    return {'rows': rows}

@app.delete('/seawide/catalog/<sku>')
def seawide_delete_sku(sku):
    catalog.delete_sku(sw.name, sku)
    return {'status': 'deleted'}

@app.post('/seawide/catalog/delete-file')
def seawide_delete_file():
    path = request.json.get('path') if request.json else ''
    if path:
        catalog.delete_from_file(sw.name, path)
    return {'status': 'done'}

@app.get('/seawide/upload-mli')
def seawide_upload_mli():
    sw.upload_multi_location_inventory()
    return {'status': 'done'}

@app.get('/seawide/test')
def seawide_test_conn():
    sw.test_connection()
    return {'status': 'done'} 