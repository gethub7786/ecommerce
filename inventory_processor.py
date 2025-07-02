"""Download and merge CWR Distribution inventory feed."""

import csv
import ssl
import urllib.request
import logging
from datetime import datetime, timedelta
from pathlib import Path
from automation_tool.sku_mapping import load_mapping, apply_mapping


def build_url(base_url: str, since: int, *, inventory_only: bool = False) -> str:
    """Construct the CWR feed URL from the base URL."""
    if inventory_only:
        fields = "sku,qty,qtynj,qtyfl,upc,mfgn"
        param = "ohtime"
    else:
        fields = "sku,price,qty,qtynj,qtyfl,upc,mfgn,sdesc"
        param = "time"
    if base_url.endswith("&"):
        prefix = base_url.rstrip("&")
    else:
        prefix = base_url
    return f"{prefix}&{param}={since}&fields={fields}"


def download_inventory(url: str, *, inventory_only: bool = False, retries: int = 1) -> list:
    """Download CSV data from CWR using the provided URL.

    If a network error occurs, the request is retried once before raising."""
    attempt = 0
    while True:
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(url, context=context, timeout=30) as resp:
                if inventory_only:
                    fieldnames = [
                        "SKU",
                        "Quantity",
                        "qtynj",
                        "qtyfl",
                        "UPC/EAN",
                        "Manufacturer",
                    ]
                else:
                    fieldnames = [
                        "SKU",
                        "Price",
                        "Quantity",
                        "qtynj",
                        "qtyfl",
                        "UPC/EAN",
                        "Manufacturer",
                        "sdesc",
                    ]
                rows = list(
                    csv.DictReader((line.decode("utf-8") for line in resp), fieldnames=fieldnames)
                )
                if rows and rows[0]["SKU"].lower() == "sku":
                    rows = rows[1:]
                if not rows:
                    logging.warning("CWR feed returned no rows")
                return rows
        except Exception as exc:
            if attempt < retries:
                attempt += 1
                continue
            raise


def merge_mapping(rows: list[dict], mapping_path: Path) -> list[dict]:
    """Apply a SKU mapping file to the downloaded rows."""
    mapping = load_mapping(mapping_path)
    return apply_mapping(rows, mapping)


def save_inventory(rows: list, output: Path):
    fieldnames = ['SKU', 'QUANTITY', 'NEWJERSEY STOCK', 'FLORIDA STOCK', 'UPC/EAN', 'Manufacturer']
    with open(output, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, '') for k in fieldnames})


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
