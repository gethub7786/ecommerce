import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from automation_tool.cwr_conversion import convert_cwr_to_amazon


def create_input(tmp_path: Path) -> Path:
    data = (
        "SKU\tQUANTITY\tNEWJERSEY STOCK\tFLORIDA STOCK\n"
        "A1\t5\t3\t2\n"
        "B2\t0\t0\t1\n"
    )
    p = tmp_path / "cwr_inventory_stock.txt"
    p.write_text(data)
    return p


def test_conversion_success(tmp_path):
    input_file = create_input(tmp_path)
    output = tmp_path / "out.csv"
    mapping = {
        'NEWJERSEY STOCK': 'NJID',
        'FLORIDA STOCK': 'FLID',
    }
    count = convert_cwr_to_amazon(input_file, output, mapping)
    assert count == 2
    lines = output.read_text().strip().splitlines()
    assert lines[0] == 'sku,fulfillment-center-id,quantity'
    assert lines[1] == 'A1,NJID,3'
    assert lines[2] == 'A1,FLID,2'
    assert lines[3] == 'A1,DEFAULT,0'


def test_missing_file(tmp_path):
    output = tmp_path / 'out.csv'
    try:
        convert_cwr_to_amazon(tmp_path/'missing.txt', output, {})
    except FileNotFoundError:
        pass
    else:
        assert False, 'expected FileNotFoundError'


def test_skip_missing_sku(tmp_path):
    p = tmp_path / "cwr_inventory_stock.txt"
    p.write_text("SKU\tQUANTITY\tNEWJERSEY STOCK\n\t\t1\n")
    output = tmp_path / 'out.csv'
    mapping = {'NEWJERSEY STOCK': 'ID'}
    count = convert_cwr_to_amazon(p, output, mapping)
    assert count == 0
    data = output.read_text().strip().splitlines()
    assert data == ['sku,fulfillment-center-id,quantity']
