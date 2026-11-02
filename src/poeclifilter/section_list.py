from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Any

from poeclifilter import merger
from poeclifilter.filters import GearGroup, JewelleryGroup
from poeclifilter.models.filter_data import flat_bands, grouped_bands, no_bands
from poeclifilter.models.filter_data.sections import SectionFilterData


# Generic so pyright checks each section's merge accepts what its parse returns
@dataclass(frozen=True)
class Section[FilterDataT: SectionFilterData[Any]]:
    name: str
    file_name: str
    parse: Callable[[Any], FilterDataT]
    merge: Callable[[FilterDataT, Path], None]  # (the section's filter data, item data dir)


# Each entry is its own constant so pyright checks its parse and merge pair up. Inside a list
# annotated list[Section[Any]] it would treat every entry as Section[Any] and skip that check.
CURRENCY = Section("currency", "currency.yaml", flat_bands.parse, merger.merge_currency_section)
GEAR = Section(
    "gear",
    "gear.yaml",
    partial(grouped_bands.parse, group_type=GearGroup),
    merger.merge_gear_section,
)
JEWELLERY = Section(
    "jewellery",
    "jewellery.yaml",
    partial(grouped_bands.parse, group_type=JewelleryGroup),
    merger.merge_jewellery_section,
)
UNIQUES = Section("uniques", "uniques.yaml", flat_bands.parse, merger.merge_unique_section)
MISCELLANEOUS = Section("miscellaneous", "miscellaneous.yaml", no_bands.parse, merger.merge_nothing)
FLASKS = Section("flasks", "flasks.yaml", flat_bands.parse, merger.merge_flasks_section)
CARDS = Section("cards", "cards.yaml", flat_bands.parse, merger.merge_cards_section)

# Order has big importance here as it affects the order that the final filer is built.
SECTIONS: list[Section[Any]] = [MISCELLANEOUS, CURRENCY, UNIQUES, CARDS, FLASKS, GEAR, JEWELLERY]
