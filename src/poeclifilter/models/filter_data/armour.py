from dataclasses import dataclass
from pathlib import Path

from poeclifilter import loader, writer
from poeclifilter.filters import AttributeGroup

file_name = "armour.yaml"


@dataclass(frozen=True)
class Band:
    base_types: list[str]


@dataclass(frozen=True)
class Armour:
    schema: int
    armour: dict[AttributeGroup, dict[str, Band]]


def get_armour(config_dir: Path):
    raw = loader.load(Path(f"{config_dir}/{file_name}").read_text())

    return parse(raw)


def parse(raw):
    # TODO: finish parsing and validation
    armour_categories = {
        AttributeGroup(name): parse_bands(bands) for name, bands in raw["armour"].items()
    }

    return Armour(schema=raw["schema"], armour=armour_categories)


def parse_bands(raw_bands):
    bands = {name: parse_band(band) for name, band in raw_bands.items()}
    return bands


def parse_band(raw_band):
    base_types = raw_band.get("base_types", [])
    return Band(base_types=base_types)


def write_armour(armour: Armour, filter_dir: Path):
    Path(f"{filter_dir}/{file_name}").write_text(writer.dump(armour))
