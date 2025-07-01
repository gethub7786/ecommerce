"""Download and merge CWR Distribution inventory feed."""

import csv
import ssl
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path


def build_url(base_url: str, since: int, *, inventory_only: bool = False) -> str:
    """Construct the CWR feed URL from the base URL."""
    if inventory_only:
        fields = "sku,qty,upc,mfgn,qtynj,qtyfl"
        param = "ohtime"
    else:
        fields = "sku,price,qty,upc,qtyfl,qtynj,mfgn"
        param = "time"
    if base_url.endswith("&"):
        prefix = base_url.rstrip("&")
    else:
        prefix = base_url
    return f"{prefix}&{param}={since}&fields={fields}"


def download_inventory(url: str, *, inventory_only: bool = False) -> list:
    """Download CSV data from CWR using the provided URL."""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(url, context=context) as resp:
        if inventory_only:
            fieldnames = [
                "SKU",
                "Quantity",
                "UPC/EAN",
                "Manufacturer",
                "qtynj",
                "qtyfl",
            ]
        else:
            fieldnames = [
                "SKU",
                "Price",
                "Quantity",
                "UPC/EAN",
                "qtyfl",
                "qtynj",
                "Manufacturer",
            ]
        return list(
            csv.DictReader((line.decode("utf-8") for line in resp), fieldnames=fieldnames)
        )


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


def main(base_url: str, since: int, mapping: Path, output: Path, *, inventory_only: bool = False):
    url = build_url(base_url, since, inventory_only=inventory_only)
    rows = download_inventory(url, inventory_only=inventory_only)
    merged = merge_mapping(rows, mapping)
    save_inventory(merged, output)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Process CWR inventory feed")
    parser.add_argument('--base-url', required=True, help='Base CWR feed URL without time/ohtime')
    parser.add_argument('--since', type=int, help='UNIX timestamp', default=int((datetime.now() - timedelta(hours=10)).timestamp()))
    parser.add_argument('--inventory-only', action='store_true', help='Use ohtime to get quantity changes only')
    parser.add_argument('--mapping', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    main(args.base_url, args.since, args.mapping, args.output, inventory_only=args.inventory_only)
