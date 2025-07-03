# Ecommerce Inventory Tools

This repository contains utilities for managing inventory data and simple supplier integrations.

## Automation Tool

`automation_tool` provides a console interface for managing supplier credentials and scheduling inventory updates.  Each supplier module contains logic to retrieve inventory using the stored credentials.  The supplier implementations live in `automation_tool/keystone.py`, `automation_tool/cwr.py`, and `automation_tool/seawide.py`:

* **Keystone** - uses the SOAP web service as the **primary** inventory tracking method via `GetInventoryUpdates` and automatically falls back to FTP when the SOAP call fails. The `SOAPAction` header is sent as a quoted URI (e.g. `"http://eKeystone.com/GetInventoryUpdates"`) so the endpoint recognizes the action. Configure warehouse columns under **Configure Location Mapping** and use **Upload Multi-Location Inventory** to produce `keystone_amazon_multilocation_inventory.json`.
* **CWR** - requires a feed **ID** entered via *Set HTTPS Credential*. The tool builds the feed URLs using that ID. A full sync with `time=0` runs every 48 hours and inventory-only updates via `ohtime` every 5–60 minutes. Both feeds include the location quantities `qtynj` and `qtyfl`. Use the **Force Full Inventory** option to reset the timestamp to 1970 and immediately pull all items. The **Upload Multi-Location Inventory** action converts `cwr_inventory_stock.txt` into an Amazon‑ready file using a configurable location mapping. A separate **SKU Mapping** file (columns `SKU` and `AMAZON SKU`) can be configured so inventory downloads replace supplier SKUs with your Amazon SKUs. The mapping file path is stored as an absolute path so later runs work regardless of the current directory. If a relative path is supplied it will be resolved relative to the credentials file when loading.
When a mapping is provided, inventory files contain an `AMAZON SKU` column instead of the supplier `SKU`.
CWR can also download its catalog via SFTP. Use **Set Ftp Credential** to provide your SFTP username, password and port (default `22`). The tool connects to `edi.cwrdistribution.com` over SFTP and downloads `catalog.csv` from the `out` folder showing progress.
* **Seawide** - the **primary** inventory method uses the same Keystone SOAP API (`GetInventoryFull` and `GetInventoryUpdates`) at `http://order.ekeystone.com/wselectronicorder/electronicorder.asmx` and falls back to FTP if the SOAP request fails. Location mapping and **Upload Multi-Location Inventory** work the same as Keystone, producing `seawide_amazon_multilocation_inventory.json`.

Keystone and Seawide support optional FTP credentials. In each supplier menu
you'll see a **Set FTP Credentials** tab where you enter only `FTP User` and
`FTP Password`. The host, port (`990`) and protocol (implicit FTPS) are fixed and
 not prompted. Keystone connects to `ftp.ekeystone.com`. Seawide uses the
same `ftp.ekeystone.com` host as well. You can also specify a `Remote Folder`
and `Remote File`
used when downloading inventory from FTP. If omitted, the folder defaults to
`/` and the file to `Inventory.csv`. Passive mode is enabled automatically for
all connections. Use **Test Connection** to verify the FTP access. For SOAP
access provide `account_number` and `security_key` via **Set API Credential**.
Seawide works the same way but uses an `api_key` against the same Keystone SOAP
endpoint.
All credentials are stored locally until you change them.

When selecting **Run Full Inventory via FTP (Secondary)** for Keystone or Seawide, you
will be prompted for the remote file name if none is saved. The tool prints the
percent complete while downloading (or the downloaded size if the server does
not report file length).

All suppliers now include utilities to test their connection and download a
vendor catalog. Catalogs are stored under `automation_tool/data/catalogs` and can
be managed from the menu (delete SKUs individually or via a delete file).

The tool works without external dependencies and stores configuration locally.

All inventory actions are logged to `automation.log`. When a SOAP or FTP request
fails, the error message is printed to the console and recorded in the log so
you can diagnose connection issues.
If a SOAP request succeeds but returns no data, the response is checked for
common fault messages. Errors like `*** You are not authorized to use this
function ***` or `*** Illegal use of this web service !!! ***` will be shown in
the console and saved to the log for easier debugging.

### Running

```bash
python -m automation_tool
```
or run the script directly:
```bash
python automation_tool/main.py
```
If you encounter an ``ImportError`` mentioning ``suppliers`` when launching the
tool, make sure you are using the current package layout and run the command
from the repository root as shown above.

The CWR integration runs a full sync every 48 hours using `time=0` and inventory-only updates every 5, 15, 30, 45 or 60 minutes via `ohtime`.
The **Upload Multi-Location Inventory** option converts `cwr_inventory_stock.txt`
to `cwr_amazon_multilocation_inventory.json` for Amazon Seller Central. Configure
the location mapping first under **Configure Location Mapping**.
### Usage

```bash
python inventory_processor.py \
  --base-url "https://cwrdistribution.com/feeds/productdownload.php?id=YOUR_FEED_ID&version=3&format=csv" \
  --since 1717900000 \
  --mapping mapping.csv \
  --output final_inventory.txt
```

`--since` should be the UNIX timestamp representing the last update time. Add `--inventory-only` to produce an ohtime feed. `--mapping` must be a CSV file with columns `SKU` and `AMAZON SKU`.

Both scripts rely only on the Python standard library and run in restricted environments.


## Web UI
A simple Material UI dashboard is provided in `web-ui`. After installing Node.js
and dependencies run:

```bash
npm install
npm run dev
```

The backend API uses Flask. Launch it with:

```bash
python -m backend
```

The UI talks to this API to manage Keystone credentials and trigger inventory
actions.
