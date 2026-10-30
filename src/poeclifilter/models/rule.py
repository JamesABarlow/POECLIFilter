from dataclasses import dataclass

from poeclifilter.filters import AttributeGroup, BandNames
from poeclifilter.game import ArmourClass, Rarity
from poeclifilter.models import display
from poeclifilter.models.display import Display


@dataclass(frozen=True)
class Range:
    min: int | None = None
    max: int | None = None


@dataclass(frozen=True)
class Rule:
    id: str
    comment: str
    hide: bool
    include: bool = True
    bands: dict[AttributeGroup, BandNames] | None = None
    base_types: list[str] | None = None
    armour_classes: list[ArmourClass] | None = None
    rarity: Rarity | None = None
    item_level: Range | None = None
    linked_sockets: Range | None = None
    display: Display | str | None = None
    rules: list[Rule] | None = None


def parse(raw_rule):
    return Rule(
        id=raw_rule["id"],
        comment=raw_rule["comment"],
        include=raw_rule.get("include", True),
        hide=raw_rule.get("hide"),
        bands=parse_bands(raw_rule.get("bands")),
        base_types=raw_rule.get("base_types"),
        armour_classes=parse_armour_classes(raw_rule.get("armour_classes")),
        rarity=parse_rarity(raw_rule.get("rarity")),
        item_level=parse_range(raw_rule.get("item_level")),
        linked_sockets=parse_range(raw_rule.get("linked_sockets")),
        display=parse_display(raw_rule.get("display")),
        rules=parse_rules(raw_rule.get("rules")),
    )


def parse_rules(raw_rules):
    if raw_rules is None:
        return None

    return [parse(raw_rule) for raw_rule in raw_rules]


def parse_bands(raw_bands):
    if raw_bands is None:
        return None

    return {AttributeGroup(group): BandNames(band) for group, band in raw_bands.items()}


def parse_armour_classes(raw_armour_classes):
    if raw_armour_classes is None:
        return None

    return [ArmourClass(armour_class) for armour_class in raw_armour_classes]


def parse_rarity(raw_rarity):
    if raw_rarity is None:
        return None

    return Rarity(raw_rarity)


def parse_range(raw_range):
    if raw_range is None:
        return None

    return Range(min=raw_range.get("min"), max=raw_range.get("max"))


def parse_display(raw_display):
    if raw_display is None or isinstance(raw_display, str):
        return raw_display

    return display.parse(raw_display)
