# Ecommerce Inventory Tools

This repository contains utilities for managing inventory data and simple supplier integrations.

## Automation Tool

`automation_tool` provides a console interface for managing supplier credentials and scheduling inventory updates.  Each supplier module contains logic to retrieve inventory using the stored credentials:

* **Keystone** - uses the SOAP web service as the **primary** inventory tracking method via `GetInventoryUpdates` and automatically falls back to FTP when the SOAP call fails.
* **CWR** - downloads the CSV feed and optionally merges a SKU mapping. A force full inventory option resets the timestamp to 1970.
* **Seawide** - the **primary** inventory method uses the SOAP API (`GetInventoryFull` and `GetInventoryUpdates`) and falls back to FTP if the SOAP request fails.

Keystone and Seawide support optional FTP credentials. In each supplier menu
you'll see a **Set FTP Credentials** tab where you enter only `FTP User` and
`FTP Password`. The host, port (`990`) and protocol (implicit FTPS) are fixed and
not prompted. You can also specify a `Remote Folder` and `Remote File` used when
downloading inventory from FTP. If omitted, the folder defaults to `/` and the
file to `Inventory.csv`. Passive mode is enabled automatically for all
connections. Use **Test Connection** to verify the FTP access. For SOAP
access provide `account_number` and `security_key` via **Set Credential**. Seawide
works the same way but uses an `api_key`.
All credentials are stored locally until you change them.

When selecting **Fetch Inventory Update via FTP** for Keystone or Seawide, you
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

From the menu select a supplier, add credentials (API keys, FTP details, etc.) and optionally schedule recurring inventory fetches.  Keystone, CWR and Seawide offer both update and full inventory downloads which can also be scheduled.
For each supplier you may test the connection and schedule catalog downloads at intervals of **1 minute**, **15 minutes**, **30 minutes**, **45 minutes**, **1 hour** or **1 week**. Catalog entries can later be removed from the "Manage Catalog" option.

## Inventory Processor

`inventory_processor.py` automates downloading the CWR Distribution inventory feed, merging with a local SKU mapping file, cleaning the data, and exporting a TSV file suitable for Amazon or internal use.

### Usage

```bash
python inventory_processor.py \
  --base-url https://example.com/inventory \
  --since 1717900000 \
  --mapping mapping.csv \
  --output final_inventory.txt
```

`--since` should be the UNIX timestamp representing the last update time. `--mapping` must be a CSV file with columns `sku` and `modified_sku`.

Both scripts rely only on the Python standard library and run in restricted environments.
