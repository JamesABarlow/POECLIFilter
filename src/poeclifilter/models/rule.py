from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, get_args

from poeclifilter.game import ItemClass, Operator, Rarity
from poeclifilter.models import display
from poeclifilter.models.display import Display


@dataclass(frozen=True)
class Range:
    min: int | None = None
    max: int | None = None


@dataclass(frozen=True)
class RarityCondition:
    operator: Operator
    rarity: Rarity


@dataclass(frozen=True)
class Rule[BandsT]:
    id: str
    comment: str
    hide: bool | None
    include: bool = True
    bands: BandsT | None = None
    base_types: list[str] | None = None
    item_classes: list[ItemClass] | None = None
    rarity: RarityCondition | None = None
    item_level: Range | None = None
    sockets: Range | None = None
    linked_sockets: Range | None = None
    stack_size: Range | None = None
    display: Display | str | None = None
    rules: list[Rule[BandsT]] | None = None


def parse[BandsT](raw_rule, parse_bands: Callable[[Any], BandsT]) -> Rule[BandsT]:
    raw_bands = raw_rule.get("bands")
    return Rule(
        id=raw_rule["id"],
        comment=raw_rule["comment"],
        include=raw_rule.get("include", True),
        hide=raw_rule.get("hide"),
        bands=None if raw_bands is None else parse_bands(raw_bands),
        base_types=raw_rule.get("base_types"),
        item_classes=parse_item_classes(raw_rule.get("item_classes")),
        rarity=parse_rarity(raw_rule.get("rarity")),
        item_level=parse_range(raw_rule.get("item_level")),
        sockets=parse_range(raw_rule.get("sockets")),
        linked_sockets=parse_range(raw_rule.get("linked_sockets")),
        stack_size=parse_range(raw_rule.get("stack_size")),
        display=parse_display(raw_rule.get("display")),
        rules=parse_rules(raw_rule.get("rules"), parse_bands),
    )


def parse_rules[BandsT](
    raw_rules, parse_bands: Callable[[Any], BandsT]
) -> list[Rule[BandsT]] | None:
    if raw_rules is None:
        return None

    return [parse(raw_rule, parse_bands) for raw_rule in raw_rules]


def parse_item_classes(raw_item_classes):
    if raw_item_classes is None:
        return None

    return [parse_item_class(raw_item_class) for raw_item_class in raw_item_classes]


def parse_item_class(raw_item_class) -> ItemClass:
    # Read the enums from the ItemClass union itself, so there is no second list to keep in step
    for item_class_enum in get_args(ItemClass.__value__):
        try:
            return item_class_enum(raw_item_class)
        except ValueError:
            pass
    raise ValueError(f"Unknown item class {raw_item_class!r}")


def parse_rarity(raw_rarity):
    if raw_rarity is None:
        return None

    return RarityCondition(
        operator=Operator(raw_rarity["operator"]), rarity=Rarity(raw_rarity["rarity"])
    )


def parse_range(raw_range):
    if raw_range is None:
        return None

    return Range(min=raw_range.get("min"), max=raw_range.get("max"))


def parse_display(raw_display):
    if raw_display is None or isinstance(raw_display, str):
        return raw_display

    return display.parse(raw_display)
