from dataclasses import dataclass
from pathlib import Path

from poeclifilter import loader, writer
from poeclifilter.filters import BandNames
from poeclifilter.models import display
from poeclifilter.models.display import Display

# Variable for name here
file_names = {"currency": "currency.yaml"}

# dataclass for banded items contains currency etc


@dataclass(frozen=True)
class Band:
    hide: bool
    display: Display
    base_types: list[str]
    stacked_base_types: dict[str, list[int]]


@dataclass(frozen=True)
class BandedItemClass:
    schema: int
    bands: dict[BandNames, Band]


@dataclass(frozen=True)
class BandedItemsFilterData:
    currency: BandedItemClass


def get_filter_data(config_dir: Path):
    raw = {}
    for name, file in file_names.items():
        raw[name] = loader.load(Path(f"{config_dir}/{file}").read_text())

    return BandedItemsFilterData(currency=parse(raw["currency"]))


def parse(raw):

    # TODO: finish parsing and validation
    bands = {}
    for band_name in BandNames:
        bands[band_name] = parse_band(raw["bands"][band_name.value])

    return BandedItemClass(schema=raw["schema"], bands=bands)


def parse_band(raw_band):
    # TODO: stacked items needs doing
    band_display = display.parse(raw_band.get("display"))
    base_types = raw_band.get("base_types", [])
    return Band(
        hide=raw_band["hide"], display=band_display, base_types=base_types, stacked_base_types={}
    )


def write_filter_data(banded_items: BandedItemsFilterData, filter_dir: Path):
    for name, file in file_names.items():
        section = getattr(banded_items, name)
        Path(f"{filter_dir}/{file}").write_text(writer.dump(section))
