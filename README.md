# Ecommerce Inventory Tools

This repository contains utilities for managing inventory data.

## Inventory Processor

`inventory_processor.py` automates downloading the CWR Distribution inventory feed, merging with a local SKU mapping file, cleaning the data, and exporting a CSV for Amazon or internal use.

### Usage

```
python inventory_processor.py \
  --base-url https://example.com/inventory \
  --since 1717900000 \
  --mapping mapping.csv \
  --output final_inventory.csv
```

`--since` should be the UNIX timestamp representing the last update time. `--mapping` must be a CSV file with two columns: `cwr_sku` and `my_sku`.

The script uses only the Python standard library and can run in restricted environments without additional dependencies.
