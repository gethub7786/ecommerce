from backend.api_keystone import app, _start_task, _finish_task, tasks  # type: ignore
from flask import request
from automation_tool.cwr import CwrSupplier
from automation_tool import catalog

cs = CwrSupplier()

# ----------------------------- CWR ROUTES -----------------------------

@app.post('/cwr/credentials')
def cwr_set_credentials():
    data = request.json or {}
    feed_id = data.get('feed_id', '')
    cs.set_credential('feed_id', feed_id)
    return {'status': 'saved'}

# fetch saved Feed ID
@app.get('/cwr/credentials')
def cwr_get_credentials():
    return {'feed_id': cs.get_credential('feed_id', '')}

@app.post('/cwr/ftp')
def cwr_set_ftp():
    data = request.json or {}
    cs.set_credential('ftp_user', data.get('user', ''))
    cs.set_credential('ftp_password', data.get('password', ''))
    cs.set_credential('ftp_port', str(data.get('port', '22')))
    return {'status': 'saved'}

@app.post('/cwr/sku-map')
def cwr_set_sku_map():
    data = request.json or {}
    path = data.get('path', '')
    cs.set_credential('sku_map_file', path)
    return {'status': 'saved'}

@app.post('/cwr/location-map')
def cwr_set_location_map():
    mapping = request.json or {}
    cs.set_credential('location_map', mapping)  # type: ignore[arg-type]
    return {'status': 'saved'}

# Inventory actions
@app.get('/cwr/inventory/partial')
def cwr_partial_inventory():
    task = _start_task('CWR Stock Sync', 'CWR')
    try:
        cs.fetch_inventory_stock()
        ok = True
    except Exception:
        ok = False
    _finish_task(task, ok)
    return {'status': 'done' if ok else 'error'}

@app.get('/cwr/inventory/full')
def cwr_full_inventory():
    task = _start_task('CWR Full Inventory', 'CWR')
    try:
        cs.fetch_inventory_full()
        ok = True
    except Exception:
        ok = False
    _finish_task(task, ok)
    return {'status': 'done' if ok else 'error'}

@app.get('/cwr/inventory/force-full')
def cwr_force_full():
    task = _start_task('CWR Force Full Sync', 'CWR')
    try:
        cs.force_full_sync()
        ok = True
    except Exception:
        ok = False
    _finish_task(task, ok)
    return {'status': 'done' if ok else 'error'}

# Schedule placeholders
@app.post('/cwr/schedule/partial')
@app.post('/cwr/schedule/full')
@app.post('/cwr/schedule/catalog')
def cwr_schedule_stub():
    data = request.json or {}
    interval = data.get('interval')
    return {'status': 'scheduled', 'interval': interval}

# Catalog management
@app.get('/cwr/catalog/run')
def cwr_run_catalog():
    task = _start_task('CWR Catalog Sync', 'CWR')
    try:
        cs.fetch_catalog()
        ok = True
    except Exception:
        ok = False
    _finish_task(task, ok)
    return {'status': 'done' if ok else 'error'}

@app.get('/cwr/catalog')
def cwr_list_catalog():
    rows = catalog.load_rows(cs.name)
    return {'rows': rows}

@app.delete('/cwr/catalog/<sku>')
def cwr_delete_sku(sku):
    catalog.delete_sku(cs.name, sku)
    return {'status': 'deleted'}

@app.post('/cwr/catalog/delete-file')
def cwr_delete_file():
    path = request.json.get('path') if request.json else ''
    if path:
        catalog.delete_from_file(cs.name, path)
    return {'status': 'done'}

# Multi-location upload
@app.get('/cwr/upload-mli')
def cwr_upload_mli():
    cs.upload_multi_location_inventory()
    return {'status': 'done'}

# Test connectivity
@app.get('/cwr/test')
def cwr_test_conn():
    cs.test_connection()
    return {'status': 'done'} 