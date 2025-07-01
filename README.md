# Ecommerce Inventory Tools

This repository contains utilities for managing inventory data and simple supplier integrations.

## Automation Tool

`automation_tool` provides a console interface for managing supplier credentials and scheduling inventory updates.  Each supplier module contains logic to retrieve inventory using the stored credentials:

* **Keystone** - contacts the SOAP web service with the provided account and security key.
* **CWR** - downloads the CSV feed and optionally merges a SKU mapping.
* **Seawide** - connects to the FTP server and retrieves the latest inventory file.

Seawide suppliers now include utilities to test the FTP connection and download
a full vendor catalog. Catalogs are stored under `automation_tool/data/catalogs`
and can be managed from the menu (delete SKUs individually or via a delete file).

The tool works without external dependencies and stores configuration locally.

### Running

```bash
python -m automation_tool
``` 
or run the script directly:
```bash
python automation_tool/main.py
```

From the menu select a supplier, add credentials (API keys, FTP details, etc.) and optionally schedule recurring inventory fetches.
When using the Seawide supplier you may also test the FTP connection and
retrieve the full product catalog at a chosen interval. Catalog entries can be
removed later from the "Manage Catalog" option.

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
