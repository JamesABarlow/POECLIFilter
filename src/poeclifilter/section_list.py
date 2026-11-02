from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Any

from poeclifilter import merger
from poeclifilter.filters import GearGroup
from poeclifilter.models.filter_data import flat_bands, grouped_bands


@dataclass(frozen=True)
class Section:
    name: str
    file_name: str
    parse: Callable[[Any], Any]
    merge: Callable[[Any, Path], None]  # (the section's filter data, item data dir)


# Order has big importance here as it affects the order that the final filer is built.
SECTIONS = [
    Section("currency", "currency.yaml", flat_bands.parse, merger.merge_currency_section),
    Section(
        "gear",
        "gear.yaml",
        partial(grouped_bands.parse, group_type=GearGroup),
        merger.merge_gear_section,
    ),
]
