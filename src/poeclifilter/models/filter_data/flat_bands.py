from dataclasses import dataclass

from poeclifilter.filters import Band, BandNames
from poeclifilter.models import rule
from poeclifilter.models.rule import Rule

# TODO: Move out to make this fully generic
file_name = "currency.yaml"


type FlatBands = list[BandNames]


@dataclass(frozen=True)
class FlatBandsFilterData:
    schema: int
    bands: dict[BandNames, Band]
    rules: list[Rule[FlatBands]]

    def resolve_bands(self, target_bands: FlatBands) -> list[str]:
        base_types = []
        for target_band_name in target_bands:
            base_types.extend(self.bands[target_band_name].base_types)

        return base_types


def parse(raw):
    # TODO: finish parsing and validation
    bands = parse_groups(raw["bands"])

    rules = [rule.parse(rule_data, parse_rule_bands) for rule_data in raw["rules"]]

    return FlatBandsFilterData(
        schema=raw["schema"],
        bands=bands,
        rules=rules,
    )


def parse_rule_bands(raw_rule_bands) -> FlatBands:
    return [BandNames(band_name) for band_name in raw_rule_bands]


def parse_groups(raw_groups):
    return {BandNames(name): parse_band(band) for name, band in raw_groups.items()}


def parse_band(raw_band):
    base_types = raw_band.get("base_types", [])
    return Band(base_types=base_types)
