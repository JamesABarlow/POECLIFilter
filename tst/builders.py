# Builders for test objects. Each call returns a fresh object, so tests can
# mutate what they get without affecting each other.

from poeclifilter.blocks import Block
from poeclifilter.models.banded_items import (
    Band,
    BandedItemClass,
    BandedItems,
    BandNames,
)
from poeclifilter.models.display import (
    Display,
    MinimapIcon,
    PlayEffect,
    ResolvedDisplay,
)
from poeclifilter.models.display_variables import (
    ColorMap,
    DisplayVariables,
    SoundAlert,
)
from poeclifilter.models.banded_item_data import (
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
    base_type=None,
    display=None,
):
    return Block(
        comment=comment,
        hide=hide,
        item_class=item_class,
        base_type=[] if base_type is None else base_type,
        display=make_resolved_display() if display is None else display,
    )


def make_band(**overrides):
    defaults = {"hide": False, "display": make_display(), "items": [], "stacked_items": {}}
    return Band(**defaults | overrides)


def make_banded_item_class(bands=None, schema=1):
    return BandedItemClass(schema=schema, bands=bands if bands is not None else {})


def make_banded_items(bands=None, schema=1):
    return BandedItems(currency=make_banded_item_class(bands, schema))


def make_single_band(band_name=BandNames.S, **band_overrides):
    """A BandedItems holding exactly one band — the common shape for a block test."""
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
    return DisplayVariables(**defaults | overrides)


def make_item_entry(band="A", stacks=None):
    return ItemEntry(band=band, stacks=stacks)


def make_banded_item_data_class(basetypes=None, schema=1, game_version="3.25"):
    return BandedItemDataClass(
        schema=schema,
        game_version=game_version,
        basetypes=basetypes if basetypes is not None else {},
    )


def make_banded_item_data(basetypes=None, schema=1, game_version="3.25"):
    return BandedItemData(
        currency=make_banded_item_data_class(basetypes, schema, game_version)
    )
