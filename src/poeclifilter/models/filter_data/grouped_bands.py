from dataclasses import dataclass
from enum import StrEnum

from poeclifilter.filters import Band, BandNames
from poeclifilter.models import rule
from poeclifilter.models.rule import Rule

type GroupedBands[GroupT] = dict[GroupT, list[BandNames]]


@dataclass(frozen=True)
class GroupedBandsFilterData[GroupT: StrEnum]:
    schema: int
    bands: dict[GroupT, dict[BandNames, Band]]
    rules: list[Rule[GroupedBands[GroupT]]]

    def resolve_bands(self, target_bands: GroupedBands[GroupT]) -> list[str]:
        base_types = []
        for group, target_band_names in target_bands.items():
            for target_band_name in target_band_names:
                target_band = self.bands[group][target_band_name]
                base_types.extend(target_band.base_types)

        return base_types


def parse[GroupT: StrEnum](raw, group_type: type[GroupT]) -> GroupedBandsFilterData[GroupT]:
    # TODO: finish parsing and validation
    bands = parse_groups(raw["bands"], group_type)

    def parse_target_bands(raw_rule_bands):
        return parse_rule_bands(raw_rule_bands, group_type)

    rules = [rule.parse(rule_data, parse_target_bands) for rule_data in raw["rules"]]

    return GroupedBandsFilterData(
        schema=raw["schema"],
        bands=bands,
        rules=rules,
    )


def parse_rule_bands[GroupT: StrEnum](
    raw_rule_bands, group_type: type[GroupT]
) -> GroupedBands[GroupT]:
    return {
        group_type(group): [BandNames(band_name) for band_name in band_names]
        for group, band_names in raw_rule_bands.items()
    }


def parse_groups[GroupT: StrEnum](raw_groups, group_type: type[GroupT]):
    return {group_type(name): parse_bands(bands) for name, bands in raw_groups.items()}


def parse_bands(raw_bands):
    bands = {BandNames(name): parse_band(band) for name, band in raw_bands.items()}
    return bands


def parse_band(raw_band):
    base_types = raw_band.get("base_types", [])
    return Band(base_types=base_types)
