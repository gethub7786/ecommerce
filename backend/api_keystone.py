from flask import Flask, request, jsonify
from automation_tool.keystone import KeystoneSupplier

app = Flask(__name__)
ks = KeystoneSupplier()

@app.post('/keystone/credentials')
def set_credentials():
    data = request.json or {}
    ks.set_credential('account_number', data.get('account_number', ''))
    ks.set_credential('security_key', data.get('security_key', ''))
    return {'status': 'saved'}

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
    ks.set_credential('location_map', mapping)
    return {'status': 'saved'}

@app.get('/keystone/inventory/partial')
def run_partial():
    success = ks.fetch_inventory_primary()
    return {'status': 'ok' if success else 'error'}

@app.get('/keystone/inventory/ftp-full')
def run_ftp_full():
    ks.fetch_inventory_secondary()
    return {'status': 'done'}

@app.get('/keystone/inventory/full')
def run_full():
    ks.fetch_inventory_full()
    return {'status': 'done'}

@app.post('/keystone/schedule/partial')
def sched_partial():
    # placeholder: scheduling not implemented
    return {'status': 'scheduled'}

@app.post('/keystone/schedule/full')
def sched_full():
    return {'status': 'scheduled'}

@app.get('/keystone/catalog/run')
def run_catalog():
    ks.fetch_catalog()
    return {'status': 'done'}

@app.post('/keystone/schedule/catalog')
def sched_catalog():
    return {'status': 'scheduled'}

@app.get('/keystone/upload-mli')
def upload_mli():
    ks.upload_multi_location_inventory()
    return {'status': 'done'}

@app.get('/keystone/test')
def test_conn():
    ks.test_connection()
    return {'status': 'done'}

if __name__ == '__main__':
    app.run(debug=True)
