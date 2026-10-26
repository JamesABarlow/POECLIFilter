from dataclasses import dataclass
from enum import StrEnum
from importlib.resources import files

import poeclifilter
from poeclifilter import loader
from poeclifilter.models import display
from poeclifilter.models.display import Display


class BandNames(StrEnum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"


# Variable for name here
file_paths = {
    "currency": files(poeclifilter).joinpath("base_filter_config", "currency.yaml")
}

# dataclass for banded items contains currency etc


@dataclass(frozen=True)
class Band:
    display: Display
    items: list[str]
    stacked_items: dict[str, list[int]]


@dataclass(frozen=True)
class BandedItemClass:
    schema: int
    bands: dict[BandNames, Band]


@dataclass(frozen=True)
class BandedItems:
    currency: BandedItemClass


def get_banded_items():
    raw = {}
    for name, file in file_paths.items():
        raw[name] = loader.load(file.read_text())

    return BandedItems(currency=parse(raw["currency"]))


def parse(raw):

    # TODO: finish parsing and validation
    bands = {}
    for band_name in BandNames:
        bands[band_name.value] = parse_band(raw["bands"][band_name.value])

    return BandedItemClass(schema=raw["schema"], bands=bands)


def parse_band(raw_band):
    # TODO: stacked items needs doing
    band_display = display.parse(raw_band.get("display"))
    items = raw_band.get("items", [])
    return Band(display=band_display, items=items, stacked_items={})
