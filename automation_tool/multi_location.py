import csv
import json
import logging
from pathlib import Path


def normalize_qty(val):
    try:
        return int(float(val))
    except Exception:
        return 0


def convert_to_amazon(input_file: Path, output_file: Path, mapping: dict,
                      sku_field: str = 'SKU', delimiter: str = '\t') -> int:
    """Convert inventory CSV to Amazon multi-location JSON.

    Parameters
    ----------
    input_file : Path
        Source inventory CSV file.
    output_file : Path
        Destination JSON path.
    mapping : dict
        Mapping of column names to Amazon supply source IDs.
    sku_field : str, default 'SKU'
        Column containing the SKU value.
    delimiter : str, default '\t'
        CSV delimiter used in the input file.

    Returns
    -------
    int
        Number of SKUs processed.
    """
    if not input_file.exists():
        logging.error("Input file not found: %s", input_file)
        raise FileNotFoundError(str(input_file))

    with input_file.open(newline='', encoding='utf-8-sig') as inf:
        reader = csv.DictReader(inf, delimiter=delimiter)
        rows = list(reader)

    output_file.parent.mkdir(parents=True, exist_ok=True)

    records = []
    processed = 0
    for row in rows:
        sku = row.get(sku_field) or row.get(sku_field.lower())
        if not sku:
            logging.warning('Skipping row with missing %s', sku_field)
            continue
        availability = []
        for col, source_id in mapping.items():
            qty = normalize_qty(row.get(col, '0'))
            availability.append({
                'fulfillmentChannelCode': source_id,
                'quantity': qty,
            })
        availability.append({'fulfillmentChannelCode': 'DEFAULT', 'quantity': 0})
        records.append({
            'sku': sku,
            'productType': 'PRODUCT',
            'patches': [{
                'op': 'replace',
                'path': '/attributes/fulfillment_availability',
                'value': availability,
            }],
        })
        processed += 1

    with output_file.open('w', encoding='utf-8') as outf:
        json.dump(records, outf, indent=2)

    logging.info('Processed %s SKUs into %s', processed, output_file)
    return processed
