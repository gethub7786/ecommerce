import csv
import os
from pathlib import Path


def load_mapping(path: str | Path) -> dict:
    """Load SKU mapping from CSV file with columns 'SKU' and 'AMAZON SKU'."""
    if not path or not os.path.exists(path):
        return {}
    mapping = {}
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            src = row.get('SKU') or row.get('sku')
            dst = row.get('AMAZON SKU') or row.get('amazon sku') or row.get('amazon_sku') or row.get('modified_sku')
            if src and dst:
                mapping[str(src)] = str(dst)
    return mapping


def apply_mapping(rows: list[dict], mapping: dict) -> list:
    """Return new rows with SKU replaced by mapping when available."""
    if not mapping:
        return rows
    new_rows = []
    for r in rows:
        r = r.copy()
        sku = r.get('SKU')
        if sku in mapping:
            r['SKU'] = mapping[sku]
        new_rows.append(r)
    return new_rows
