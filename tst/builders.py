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


def make_play_effect(**overrides):
    return PlayEffect(**{"color": "Purple", "temp": False} | overrides)


def make_minimap_icon(**overrides):
    return MinimapIcon(**{"size": 1, "color": "Purple", "shape": "Circle"} | overrides)


def make_display(hide=False, **overrides):
    return Display(hide=hide, **overrides)


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
    defaults = {"display": make_display(), "items": [], "stacked_items": {}}
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
