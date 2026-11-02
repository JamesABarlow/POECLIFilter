from dataclasses import dataclass

from poeclifilter.filters import BandNames, GearGroup
from poeclifilter.models import rule
from poeclifilter.models.rule import Rule

file_name = "gear.yaml"


@dataclass(frozen=True)
class Band:
    base_types: list[str]


type GearBands = dict[GearGroup, list[BandNames]]


@dataclass(frozen=True)
class GearFilterData:
    schema: int
    bands: dict[GearGroup, dict[BandNames, Band]]
    rules: list[Rule[GearBands]]

    def resolve_bands(self, target_bands: GearBands) -> list[str]:
        base_types = []
        for gear_group, target_band_names in target_bands.items():
            for target_band_name in target_band_names:
                target_band = self.bands[gear_group][target_band_name]
                base_types.extend(target_band.base_types)

        return base_types


def parse(raw):
    # TODO: finish parsing and validation
    bands = parse_groups(raw["bands"])

    rules = [rule.parse(rule_data, parse_rule_bands) for rule_data in raw["rules"]]

    return GearFilterData(
        schema=raw["schema"],
        bands=bands,
        rules=rules,
    )


def parse_rule_bands(raw_rule_bands) -> GearBands:
    return {
        GearGroup(group): [BandNames(band_name) for band_name in band_names]
        for group, band_names in raw_rule_bands.items()
    }


def parse_groups(raw_groups):
    return {GearGroup(name): parse_bands(bands) for name, bands in raw_groups.items()}


def parse_bands(raw_bands):
    bands = {BandNames(name): parse_band(band) for name, band in raw_bands.items()}
    return bands


def parse_band(raw_band):
    base_types = raw_band.get("base_types", [])
    return Band(base_types=base_types)
