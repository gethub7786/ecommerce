import csv
import os
from pathlib import Path


def load_mapping(path: str | Path) -> dict:
    """Load SKU mapping from CSV file with columns 'SKU' and 'AMAZON SKU'.

    The path may be relative or absolute and `~` will be expanded. If the file
    cannot be found, an empty mapping is returned."""
    if not path:
        return {}
    p = Path(path).expanduser()
    if not p.is_absolute():
        p = (Path.cwd() / p).resolve()
    if not p.exists():
        return {}
    path = str(p)
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
    """Return new rows with Amazon SKU column if mapping is provided."""
    if not mapping:
        return rows
    new_rows = []
    for r in rows:
        r = r.copy()
        sku = r.pop('SKU', None)
        if sku is None:
            new_rows.append(r)
            continue
        amz = mapping.get(sku, sku)
        r['AMAZON SKU'] = amz
        new_rows.append(r)
    return new_rows
