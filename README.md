# Ecommerce Inventory Tools

This repository contains utilities for managing inventory data and simple supplier integrations.

## Automation Tool

`automation_tool` provides a console interface for managing supplier credentials and scheduling inventory updates.  Each supplier module contains logic to retrieve inventory using the stored credentials:

* **Keystone** - uses the SOAP web service as the **primary** inventory tracking method via `GetInventoryUpdates` and automatically falls back to FTP when the SOAP call fails.
* **CWR** - downloads the CSV feed and optionally merges a SKU mapping. A force full inventory option resets the timestamp to 1970.
* **Seawide** - the **primary** inventory method uses the SOAP API (`GetInventoryFull` and `GetInventoryUpdates`) and falls back to FTP if the SOAP request fails.

Keystone and Seawide support optional FTP credentials. Provide `ftp_host`,
`ftp_user`, `ftp_password`, `ftp_port` and `ftp_protocol` through the menu
and use **Test Connection** to verify access. The protocol can be `ftp` or
`ftps` (implicit or explicit TLS).
For Seawide SOAP access, also supply `account_number` and `api_key`.

All suppliers now include utilities to test their connection and download a
vendor catalog. Catalogs are stored under `automation_tool/data/catalogs` and can
be managed from the menu (delete SKUs individually or via a delete file).

The tool works without external dependencies and stores configuration locally.

### Running

```bash
python -m automation_tool
``` 
or run the script directly:
```bash
python automation_tool/main.py
```

From the menu select a supplier, add credentials (API keys, FTP details, etc.) and optionally schedule recurring inventory fetches.  Keystone, CWR and Seawide offer both update and full inventory downloads which can also be scheduled.
For each supplier you may test the connection and schedule catalog downloads at intervals of **5 minutes**, **1 hour**, **1 day** or **1 week**. Catalog entries can later be removed from the "Manage Catalog" option.

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
