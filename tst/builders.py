# Builders for test objects. Each call returns a fresh object, so tests can
# mutate what they get without affecting each other.

from poeclifilter.blocks import Block, ResolvedDisplay
from poeclifilter.filters import BandNames
from poeclifilter.models.display import (
    Display,
    MinimapIcon,
    PlayEffect,
)
from poeclifilter.models.filter_data.armour import ArmourFilterData
from poeclifilter.models.filter_data.armour import Band as ArmourBand
from poeclifilter.models.filter_data.banded_items import (
    Band,
    BandedItemClass,
    BandedItemsFilterData,
)
from poeclifilter.models.filter_data.display_variables import (
    ColorMap,
    DisplayVariablesFilterData,
    SoundAlert,
)
from poeclifilter.models.item_data.armour import ArmourEntry, ArmourItemData
from poeclifilter.models.item_data.banded import (
    BandedItemData,
    BandedItemDataClass,
    ItemEntry,
)


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
    item_class="Stackable Currency",
    base_types=None,
    display=None,
):
    return Block(
        comment=comment,
        hide=hide,
        item_class=item_class,
        base_types=[] if base_types is None else base_types,
        display=make_resolved_display() if display is None else display,
    )


def make_band(**overrides):
    defaults = {
        "hide": False,
        "display": make_display(),
        "base_types": [],
        "stacked_base_types": {},
    }
    return Band(**defaults | overrides)


def make_banded_item_class(bands=None, schema=1):
    return BandedItemClass(schema=schema, bands=bands if bands is not None else {})


def make_banded_items(bands=None, schema=1):
    return BandedItemsFilterData(currency=make_banded_item_class(bands, schema))


def make_single_band(band_name=BandNames.S, **band_overrides):
    return make_banded_items({band_name: make_band(**band_overrides)})


def make_color_map(**overrides):
    defaults = {
        "background": {"white": (237, 233, 222, 230)},
        "border": {"purple": (79, 0, 122, 255)},
        "text": {"purple": (79, 0, 122, 255)},
    }
    return ColorMap(**defaults | overrides)


def make_display_variables(**overrides):
    defaults = {
        "schema": 1,
        "colors": make_color_map(),
        "font_size": {"normal": 36},
        "sound_alert": {"major": SoundAlert(id=6, volume=300)},
    }
    return DisplayVariablesFilterData(**defaults | overrides)


def make_item_entry(band="A", stacks=None):
    return ItemEntry(band=band, stacks=stacks)


def make_banded_item_data_class(categories=None, schema=1, game_version="3.25"):
    return BandedItemDataClass(
        schema=schema,
        game_version=game_version,
        categories=categories if categories is not None else {},
    )


def make_banded_item_data(categories=None, schema=1, game_version="3.25"):
    return BandedItemData(currency=make_banded_item_data_class(categories, schema, game_version))


def make_armour_band(base_types=None):
    return ArmourBand(base_types=[] if base_types is None else base_types)


def make_armour_filter_data(armour_categories=None, schema=1):
    return ArmourFilterData(
        schema=schema,
        armour_categories=armour_categories if armour_categories is not None else {},
    )


def make_armour_entry(band="A"):
    return ArmourEntry(band=band)


def make_armour_item_data(categories=None, schema=1, game_version="3.25"):
    return ArmourItemData(
        schema=schema,
        game_version=game_version,
        categories=categories if categories is not None else {},
    )
