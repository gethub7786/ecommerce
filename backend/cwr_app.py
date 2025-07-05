from flask import Flask, request
import os, sys, json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from automation_tool.cwr import CwrSupplier
from automation_tool import catalog
from .common import tasks, start_task, finish_task

app = Flask(__name__)

cs = CwrSupplier()

# ---------------- Helpers -----------------
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)
CRED_FILE = os.path.join(DATA_DIR, 'cwr_creds.json')

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

# -------------- Routes --------------------
@app.post('/cwr/credentials')
def set_credentials():
    data = request.json or {}
    cred_store['feed_id'] = data.get('feed_id', '')
    save_creds(cred_store)
    cs.set_credential('feed_id', cred_store['feed_id'])
    return {'status': 'saved'}

@app.get('/cwr/credentials')
def get_credentials():
    return {'feed_id': cs.get_credential('feed_id', '')}

@app.post('/cwr/ftp')
def set_ftp():
    data = request.json or {}
    cs.set_credential('ftp_user', data.get('user', ''))
    cs.set_credential('ftp_password', data.get('password', ''))
    cs.set_credential('ftp_port', str(data.get('port', '22')))
    return {'status': 'saved'}

@app.post('/cwr/location-map')
def set_location_map():
    mapping = request.json or {}
    cs.set_credential('location_map', mapping)  # type: ignore[arg-type]
    return {'status': 'saved'}

@app.get('/cwr/inventory/partial')
def run_partial():
    task = start_task('CWR Stock Sync', 'CWR')
    try:
        cs.fetch_inventory_stock()
        ok = True
    except Exception:
        ok = False
    finish_task(task, ok)
    return {'status': 'done' if ok else 'error'}

# suppliers status & tasks
@app.get('/suppliers/status')
def suppliers_status():
    return {'suppliers': [cs.status()]}

@app.get('/tasks')
def list_tasks():
    return {'tasks': tasks}

if __name__ == '__main__':
    app.run(port=5001) 