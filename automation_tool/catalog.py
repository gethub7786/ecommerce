import csv
import os
from .base import DATA_DIR

CATALOG_DIR = os.path.join(DATA_DIR, 'catalogs')
os.makedirs(CATALOG_DIR, exist_ok=True)


def catalog_path(name: str) -> str:
    return os.path.join(CATALOG_DIR, f"{name}.csv")


def apply_mapping(rows: list, mapping_file: str) -> list:
    """Apply a SKU mapping file if provided."""
    if not mapping_file or not os.path.exists(mapping_file):
        return rows
    with open(mapping_file, newline='') as f:
        mapping = {r['sku']: r['modified_sku'] for r in csv.DictReader(f)}
    new_rows = []
    for r in rows:
        sku = r.get('SKU')
        if sku in mapping:
            r = r.copy()
            r['SKU'] = mapping[sku]
        new_rows.append(r)
    return new_rows


def save_rows(name: str, rows: list) -> None:
    path = catalog_path(name)
    if not rows:
        open(path, 'w').close()
        return
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def load_rows(name: str) -> list:
    path = catalog_path(name)
    if not os.path.exists(path):
        return []
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def delete_sku(name: str, sku: str) -> None:
    rows = [r for r in load_rows(name) if r.get('SKU') != sku]
    save_rows(name, rows)


def delete_from_file(name: str, delete_file: str) -> None:
    rows = load_rows(name)
    deletes = set()
    with open(delete_file, newline='') as f:
        for row in csv.DictReader(f):
            if row.get('DELETE', '').strip().upper() == 'X':
                deletes.add(row.get('SKU'))
    rows = [r for r in rows if r.get('SKU') not in deletes]
    save_rows(name, rows)
