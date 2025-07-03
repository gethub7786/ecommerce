"""Simple FastAPI server exposing automation tool functions and serving the React UI."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import subprocess
import logging

from automation_tool import KeystoneSupplier, CwrSupplier, SeawideSupplier

app = FastAPI(title="Automation Tool API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

suppliers = {
    "keystone": KeystoneSupplier(),
    "cwr": CwrSupplier(),
    "seawide": SeawideSupplier(),
}

# Serve the built React app from ../web-ui/dist if it exists
dist_dir = Path(__file__).resolve().parent.parent / "web-ui" / "dist"
if dist_dir.exists():
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="static")

@app.get("/api/suppliers")
def list_suppliers():
    return list(suppliers.keys())

@app.post("/api/suppliers/{name}/credentials")
def set_credentials(name: str, creds: dict):
    supplier = suppliers.get(name)
    if not supplier:
        raise HTTPException(status_code=404, detail="Unknown supplier")
    for key, val in creds.items():
        supplier.set_credential(key, val)
    return {"status": "saved"}

@app.post("/api/suppliers/{name}/inventory/update")
def run_update(name: str):
    supplier = suppliers.get(name)
    if not supplier:
        raise HTTPException(status_code=404, detail="Unknown supplier")
    supplier.fetch_inventory()
    return {"status": "started"}

@app.post("/api/suppliers/{name}/inventory/full")
def run_full(name: str):
    supplier = suppliers.get(name)
    if not supplier or not hasattr(supplier, "fetch_inventory_full"):
        raise HTTPException(status_code=404, detail="Unsupported")
    supplier.fetch_inventory_full()
    return {"status": "started"}

@app.get("/api/logs")
def get_logs():
    log_file = Path("automation.log")
    if log_file.exists():
        return FileResponse(str(log_file))
    raise HTTPException(status_code=404, detail="Log not found")

if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=8000)
