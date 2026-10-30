from dataclasses import dataclass
from pathlib import Path

from poeclifilter import loader, writer
from poeclifilter.filters import AttributeGroup, BandNames
from poeclifilter.models import rule
from poeclifilter.models.rule import Rule

file_name = "armour.yaml"


@dataclass(frozen=True)
class Band:
    base_types: list[str]


@dataclass(frozen=True)
class ArmourFilterData:
    schema: int
    armour_categories: dict[AttributeGroup, dict[BandNames, Band]]
    rules: list[Rule]


def get_filter_data(config_dir: Path):
    raw = loader.load(Path(f"{config_dir}/{file_name}").read_text())

    return parse(raw)


def parse(raw):
    # TODO: finish parsing and validation
    armour_categories = {
        AttributeGroup(name): parse_bands(bands) for name, bands in raw["armour_categories"].items()
    }

    rules = [rule.parse(rule_data) for rule_data in raw["rules"]]

    return ArmourFilterData(schema=raw["schema"], armour_categories=armour_categories, rules=rules)


def parse_bands(raw_bands):
    bands = {BandNames(name): parse_band(band) for name, band in raw_bands.items()}
    return bands


def parse_band(raw_band):
    base_types = raw_band.get("base_types", [])
    return Band(base_types=base_types)


def write_filter_data(armour: ArmourFilterData, filter_dir: Path):
    Path(f"{filter_dir}/{file_name}").write_text(writer.dump(armour))
