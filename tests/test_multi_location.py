import json
import os
import json
from pathlib import Path

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from automation_tool.multi_location import convert_to_amazon


def create_input(tmp_path: Path, sku_field: str) -> Path:
    data = (
        f"{sku_field},A,B\n"
        f"X1,1,2\n"
        f"X2,0,3\n"
    )
    p = tmp_path / 'inv.csv'
    p.write_text(data)
    return p


def test_generic_conversion(tmp_path: Path):
    inp = create_input(tmp_path, 'SKU')
    out = tmp_path / 'out.json'
    mapping = {'A': 'ID1', 'B': 'ID2'}
    count = convert_to_amazon(inp, out, mapping, sku_field='SKU', delimiter=',')
    assert count == 2
    data = json.loads(out.read_text())
    assert data[0]['sku'] == 'X1'
    avail = data[0]['patches'][0]['value']
    assert avail[0]['fulfillmentChannelCode'] == 'ID1'
    assert avail[0]['quantity'] == 1
    assert avail[1]['fulfillmentChannelCode'] == 'ID2'
    assert avail[1]['quantity'] == 2
    assert avail[2]['fulfillmentChannelCode'] == 'DEFAULT'

