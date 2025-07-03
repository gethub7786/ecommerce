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


def get_supplier(name: str):
    supplier = suppliers.get(name)
    if not supplier:
        raise HTTPException(status_code=404, detail="Unknown supplier")
    return supplier

# Serve the built React app from ../web-ui/dist if it exists
dist_dir = Path(__file__).resolve().parent.parent / "web-ui" / "dist"
if dist_dir.exists():
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="static")

@app.get("/api/suppliers")
def list_suppliers():
    return list(suppliers.keys())

@app.post("/api/{name}/set-credentials")
def set_credentials(name: str, creds: dict):
    supplier = get_supplier(name)
    for key, val in creds.items():
        supplier.set_credential(key, val)
    return {"status": "saved"}


@app.post("/api/{name}/set-ftp")
def set_ftp(name: str, creds: dict):
    supplier = get_supplier(name)
    for key, val in creds.items():
        supplier.set_credential(key, val)
    return {"status": "saved"}


@app.post("/api/{name}/location-map")
def set_location_map(name: str, mapping: dict):
    supplier = get_supplier(name)
    supplier.set_credential("location_map", mapping)
    return {"status": "saved"}


@app.post("/api/{name}/sku-map")
def set_sku_map(name: str, data: dict):
    supplier = get_supplier(name)
    supplier.set_credential("mapping_file", data.get("path"))
    return {"status": "saved"}

@app.post("/api/{name}/inventory/partial")
def run_update(name: str):
    supplier = get_supplier(name)
    supplier.fetch_inventory()
    return {"status": "started"}


@app.post("/api/{name}/inventory/full")
def run_full(name: str):
    supplier = get_supplier(name)
    if not hasattr(supplier, "fetch_inventory_full"):
        raise HTTPException(status_code=404, detail="Unsupported")
    supplier.fetch_inventory_full()
    return {"status": "started"}


@app.post("/api/{name}/inventory/secondary")
def run_secondary(name: str):
    supplier = get_supplier(name)
    if not hasattr(supplier, "fetch_inventory_secondary"):
        raise HTTPException(status_code=404, detail="Unsupported")
    supplier.fetch_inventory_secondary()
    return {"status": "started"}


@app.post("/api/{name}/inventory/stock")
def run_stock(name: str):
    supplier = get_supplier(name)
    if not hasattr(supplier, "fetch_inventory_stock"):
        raise HTTPException(status_code=404, detail="Unsupported")
    supplier.fetch_inventory_stock()
    return {"status": "started"}


@app.post("/api/{name}/inventory/force-full")
def run_force_full(name: str):
    supplier = get_supplier(name)
    if not hasattr(supplier, "force_full_sync"):
        raise HTTPException(status_code=404, detail="Unsupported")
    supplier.force_full_sync()
    return {"status": "started"}

@app.post("/api/{name}/catalog")
def run_catalog(name: str):
    supplier = get_supplier(name)
    if not hasattr(supplier, "fetch_catalog"):
        raise HTTPException(status_code=404, detail="Unsupported")
    supplier.fetch_catalog()
    return {"status": "started"}


@app.post("/api/{name}/multi-location")
def run_multi(name: str):
    supplier = get_supplier(name)
    if not hasattr(supplier, "upload_multi_location_inventory"):
        raise HTTPException(status_code=404, detail="Unsupported")
    supplier.upload_multi_location_inventory()
    return {"status": "started"}


@app.get("/api/{name}/test")
def run_test(name: str):
    supplier = get_supplier(name)
    supplier.test_connection()
    return {"status": "done"}

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
