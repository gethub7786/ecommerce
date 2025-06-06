import argparse
import csv
import os
import urllib.parse
import urllib.request
from datetime import datetime


def download_inventory(base_url: str, timestamp: int, api_key: str | None = None) -> str:
    """Download inventory CSV as text."""
    params = {'timestamp': str(timestamp)}
    if api_key:
        params['key'] = api_key
    url = base_url
    if '?' in base_url:
        url += '&' + urllib.parse.urlencode(params)
    else:
        url += '?' + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url) as resp:
        return resp.read().decode('utf-8', 'ignore')


def load_mapping(path: str) -> dict:
    """Load SKU mapping CSV."""
    mapping: dict[str, str] = {}
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cwr = row.get('cwr_sku')
            my = row.get('my_sku')
            if cwr and my:
                mapping[cwr.strip()] = my.strip()
    return mapping


def parse_inventory(text: str) -> list[dict]:
    """Parse inventory CSV into a list of dictionaries."""
    reader = csv.DictReader(text.splitlines())
    rows: list[dict] = []
    for row in reader:
        cleaned = {k.strip(): v.strip() for k, v in row.items() if k}
        rows.append(cleaned)
    return rows


def merge_inventory(inventory: list[dict], sku_map: dict) -> list[dict]:
    """Merge inventory rows with SKU mapping."""
    merged: list[dict] = []
    for row in inventory:
        cwr_sku = row.get('PartNumber') or row.get('SKU') or row.get('cwr_sku')
        if not cwr_sku:
            continue
        internal = sku_map.get(cwr_sku)
        if not internal:
            continue
        merged.append({
            'sku': internal,
            'available': row.get('Qty') or row.get('QtyAvailable') or row.get('available', ''),
            'price': row.get('Price') or row.get('price', '')
        })
    return merged


def write_output(rows: list[dict], path: str) -> None:
    """Write merged data to CSV."""
    if not rows:
        return
    fieldnames = ['sku', 'available', 'price']
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description='Process CWR inventory feed.')
    parser.add_argument('--base-url', required=True, help='Base URL for CWR inventory feed')
    parser.add_argument('--api-key', default=os.getenv('CWR_API_KEY'), help='API key for CWR')
    parser.add_argument('--since', type=int, required=True, help='UNIX timestamp for incremental feed')
    parser.add_argument('--mapping', required=True, help='Path to local SKU mapping CSV')
    parser.add_argument('--output', required=True, help='Path to output CSV file')
    args = parser.parse_args()

    inventory_text = download_inventory(args.base_url, args.since, args.api_key)
    inventory_rows = parse_inventory(inventory_text)
    sku_map = load_mapping(args.mapping)
    final_rows = merge_inventory(inventory_rows, sku_map)
    write_output(final_rows, args.output)


if __name__ == '__main__':
    main()
