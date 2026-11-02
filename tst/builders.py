# Builders for test objects. Each call returns a fresh object, so tests can
# mutate what they get without affecting each other.


from poeclifilter.blocks import Block, ResolvedDisplay
from poeclifilter.filters import Band, BandNames
from poeclifilter.game import Operator, Rarity
from poeclifilter.models.display import (
    Display,
    MinimapIcon,
    PlayEffect,
)
from poeclifilter.models.filter_data.display_variables import (
    ColorMap,
    DisplayVariablesFilterData,
    SoundAlert,
)
from poeclifilter.models.filter_data.flat_bands import FlatBandsFilterData
from poeclifilter.models.filter_data.grouped_bands import GroupedBandsFilterData
from poeclifilter.models.item_data.armour import ArmourEntry, ArmourItemData
from poeclifilter.models.item_data.currency import CurrencyEntry, CurrencyItemData
from poeclifilter.models.item_data.weapons import WeaponEntry, WeaponItemData
from poeclifilter.models.rule import Range, RarityCondition, Rule


def make_play_effect(**overrides):
    return PlayEffect(**{"color": "Purple", "temp": False} | overrides)


def make_minimap_icon(**overrides):
    return MinimapIcon(**{"size": 1, "color": "Purple", "shape": "Circle"} | overrides)


def make_display(**overrides):
    return Display(**overrides)


def make_resolved_display(**overrides):
    return ResolvedDisplay(**overrides)


def make_block(
    comment="",
    hide=False,
    item_classes=None,
    base_types=None,
    display=None,
    sockets=None,
    rarity=None,
    item_level=None,
):
    return Block(
        comment=comment,
        hide=hide,
        item_classes=item_classes,
        base_types=[] if base_types is None else base_types,
        display=make_resolved_display() if display is None else display,
        sockets=sockets,
        rarity=rarity,
        item_level=item_level,
    )


def make_color_map(**overrides):
    defaults = {
        "background": {"white": (237, 233, 222, 230)},
        "border": {"purple": (79, 0, 122, 255)},
        "text": {"purple": (79, 0, 122, 255)},
    }
    return ColorMap(**defaults | overrides)


def make_display_variables(
    schema=1,
    colors=None,
    font_size=None,
    sound_alert=None,
    displays=None,
):
    return DisplayVariablesFilterData(
        schema=schema,
        colors=make_color_map() if colors is None else colors,
        font_size={"normal": 36} if font_size is None else font_size,
        sound_alert=(
            {"major": SoundAlert(id=6, volume=300)} if sound_alert is None else sound_alert
        ),
        displays=(
            {"loud": make_display(border_color="$purple", font_size="$normal")}
            if displays is None
            else displays
        ),
    )


def make_grouped_bands_filter_data(bands=None, rules=None, schema=1):
    return GroupedBandsFilterData(
        schema=schema,
        bands=bands if bands is not None else {},
        rules=[make_rule()] if rules is None else rules,
    )


def make_band(base_types=None):
    return Band(base_types=[] if base_types is None else base_types)


def make_flat_bands_filter_data(bands=None, rules=None, schema=1):
    return FlatBandsFilterData(
        schema=schema,
        bands=bands if bands is not None else {},
        rules=[make_rule()] if rules is None else rules,
    )


def make_armour_entry(band=BandNames.A):
    return ArmourEntry(band=band)


def make_armour_item_data(categories=None, schema=1, game_version="3.25"):
    return ArmourItemData(
        schema=schema,
        game_version=game_version,
        categories=categories if categories is not None else {},
    )


def make_currency_entry(band=BandNames.A, stacks=None):
    return CurrencyEntry(band=band, stacks=stacks)


def make_currency_item_data(categories=None, schema=1, game_version="3.25"):
    return CurrencyItemData(
        schema=schema,
        game_version=game_version,
        categories=categories if categories is not None else {},
    )


def make_weapon_entry(band=BandNames.A):
    return WeaponEntry(band=band)


def make_weapon_item_data(categories=None, schema=1, game_version="3.25"):
    return WeaponItemData(
        schema=schema,
        game_version=game_version,
        categories=categories if categories is not None else {},
    )


def make_range(min=None, max=None):
    return Range(min=min, max=max)


def make_rarity_condition(operator=Operator.EQUAL, rarity=Rarity.RARE):
    return RarityCondition(operator=operator, rarity=rarity)


def make_rule(
    id="rule",
    comment="",
    include=True,
    hide=None,
    bands=None,
    base_types=None,
    item_classes=None,
    rarity=None,
    item_level=None,
    sockets=None,
    linked_sockets=None,
    display=None,
    rules=None,
):
    return Rule(
        id=id,
        comment=comment,
        include=include,
        hide=hide,
        bands=bands,
        base_types=base_types,
        item_classes=item_classes,
        rarity=rarity,
        item_level=item_level,
        sockets=sockets,
        linked_sockets=linked_sockets,
        display=display,
        rules=rules,
    )
