"""Automation tool package exports.

This package exposes the supplier classes used by ``main.py``.  Older
revisions placed these classes in a ``suppliers`` module so we keep a
compatibility shim to avoid ``ImportError`` when an outdated ``__init__`` is
imported.
"""

try:  # preferred relative imports
    from .keystone import KeystoneSupplier
    from .cwr import CwrSupplier
    from .seawide import SeawideSupplier
except ImportError:  # fallback for running from a single folder without package
    from keystone import KeystoneSupplier
    from cwr import CwrSupplier
    from seawide import SeawideSupplier

from .scheduler import RepeatedTimer

__all__ = [
    "KeystoneSupplier",
    "CwrSupplier",
    "SeawideSupplier",
    "RepeatedTimer",
]
