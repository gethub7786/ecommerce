from pathlib import Path
from .multi_location import convert_to_amazon


def convert_cwr_to_amazon(
    input_file: Path,
    output_file: Path,
    mapping: dict,
    delimiter: str = "\t",
) -> int:
    """Wrapper calling :func:`convert_to_amazon` for CWR feeds."""
    return convert_to_amazon(
        input_file,
        output_file,
        mapping,
        sku_field="SKU",
        delimiter=delimiter,
    )

