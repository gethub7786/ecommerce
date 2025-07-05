import csv
import os
from .base import DATA_DIR

CATALOG_DIR = os.path.join(DATA_DIR, 'catalogs')
os.makedirs(CATALOG_DIR, exist_ok=True)


def catalog_path(name: str) -> str:
    return os.path.join(CATALOG_DIR, f"{name}.csv")


def apply_mapping(rows: list, mapping_file: str) -> list:
    """Apply a SKU mapping file if provided and rename the column."""
    if not mapping_file or not os.path.exists(mapping_file):
        return rows
    with open(mapping_file, newline='') as f:
        mapping = {r['sku']: r['modified_sku'] for r in csv.DictReader(f)}
    new_rows = []
    for r in rows:
        r = r.copy()
        sku = r.pop('SKU', None)
        if sku is not None:
            r['AMAZON SKU'] = mapping.get(sku, sku)
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
        sample = f.read(2048)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=',\t')
        except Exception:
            dialect = csv.get_dialect('excel')  # default comma
        reader = csv.DictReader(f, dialect=dialect)
        return list(reader)


def delete_sku(name: str, sku: str) -> None:
    rows = [
        r
        for r in load_rows(name)
        if r.get('SKU') != sku and r.get('AMAZON SKU') != sku
    ]
    save_rows(name, rows)


def delete_from_file(name: str, delete_file: str) -> None:
    rows = load_rows(name)
    deletes = set()
    with open(delete_file, newline='') as f:
        for row in csv.DictReader(f):
            if row.get('DELETE', '').strip().upper() == 'X':
                deletes.add(row.get('SKU') or row.get('AMAZON SKU'))
    rows = [
        r
        for r in rows
        if r.get('SKU') not in deletes and r.get('AMAZON SKU') not in deletes
    ]
    save_rows(name, rows)
