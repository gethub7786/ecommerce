"""Download and merge CWR Distribution inventory feed."""

import csv
import json
import ssl
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path


def download_inventory(base_url: str, since: int) -> list:
    """Download CSV data from CWR."""
    url = f"{base_url}&ohtime={since}"
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(url, context=context) as resp:
        return list(csv.DictReader(
            (line.decode('utf-8') for line in resp),
            fieldnames=["SKU", "Quantity", "UPC/EAN", "Manufacturer", "Price", "MAP", "MRP", "qtynj", "qtyfl"]
        ))


def merge_mapping(rows: list, mapping_path: Path) -> list:
    with open(mapping_path, newline='') as f:
        mapping = {r['sku']: r['modified_sku'] for r in csv.DictReader(f)}
    merged = []
    for r in rows:
        sku = r['SKU']
        if sku in mapping:
            merged.append({
                'SKU': mapping[sku],
                'Quantity': r['Quantity'],
                'qtynj': r.get('qtynj', 0),
                'qtyfl': r.get('qtyfl', 0),
                'handling-time': 0,
            })
    return merged


def save_inventory(rows: list, output: Path):
    with open(output, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['SKU', 'Quantity', 'qtynj', 'qtyfl', 'handling-time'], delimiter='\t')
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def main(base_url: str, since: int, mapping: Path, output: Path):
    rows = download_inventory(base_url, since)
    merged = merge_mapping(rows, mapping)
    save_inventory(merged, output)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Process CWR inventory feed")
    parser.add_argument('--base-url', required=True, help='Feed base URL')
    parser.add_argument('--since', type=int, help='UNIX timestamp', default=int((datetime.now() - timedelta(hours=10)).timestamp()))
    parser.add_argument('--mapping', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    main(args.base_url, args.since, args.mapping, args.output)
