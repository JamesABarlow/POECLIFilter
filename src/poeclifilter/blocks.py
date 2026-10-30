# Convert the filter settings to ordered block list that can be used to write the filter

from collections.abc import Sequence
from dataclasses import dataclass

from poeclifilter.filters import AttributeGroup, BandNames, FilterRef
from poeclifilter.models.display import Display
from poeclifilter.models.filter_data import armour as armour_filter_data_model
from poeclifilter.models.filter_data import banded_items, display_variables
from poeclifilter.models.filter_data.armour import ArmourFilterData, Band
from poeclifilter.models.filter_data.banded_items import (
    BandedItemClass,
    BandedItemsFilterData,
)
from poeclifilter.models.filter_data.display_variables import (
    Color,
    DisplayVariablesFilterData,
    SoundAlert,
)
from poeclifilter.resources import filter_dir


# TODO: Not sure if I like this design, can I get something better here
@dataclass(frozen=True)
class ResolvedDisplay:
    play_effect: str | None = None
    minimap_icon: str | None = None
    text_color: str | None = None
    background_color: str | None = None
    border_color: str | None = None
    font_size: str | None = None
    sound_alert: str | None = None


@dataclass(frozen=True)
class Block:
    comment: str
    hide: bool
    item_classes: Sequence[str] | None
    base_types: list[str] | None
    display: ResolvedDisplay | None


def build_blocks(filter_ref: FilterRef):
    # TODO: These should be input as args, simplifies the testing
    display_variables_filter_data = display_variables.get_filter_data(filter_dir(filter_ref))
    banded_items_filter_data = banded_items.get_filter_data(filter_dir(filter_ref))
    armour_filter_data = armour_filter_data_model.get_filter_data(filter_dir(filter_ref))

    blocks = []

    # Ordering matters here, will be the same ordering in the final model.
    blocks.extend(
        build_banded_items_blocks(banded_items_filter_data, display_variables_filter_data)
    )
    blocks.extend(build_armour_blocks(armour_filter_data, display_variables_filter_data))

    # Add misc filter blocks including the final catch all here
    # TODO: This needs to be built better but here for now
    blocks.extend(
        [
            Block(
                comment="",
                hide=False,
                item_classes=None,
                base_types=None,
                display=ResolvedDisplay(background_color="237 233 222 230"),
            )
        ]
    )

    return blocks


def build_banded_items_blocks(
    banded_items: BandedItemsFilterData, display_variables: DisplayVariablesFilterData
):
    blocks = []

    blocks.extend(build_bands(banded_items.currency, display_variables))

    return blocks


def build_bands(banded_class: BandedItemClass, display_variables: DisplayVariablesFilterData):
    blocks = []
    for band_name in BandNames:
        band = banded_class.bands.get(band_name)

        if not band or not band.base_types:
            continue

        blocks.append(
            Block(
                comment="",
                hide=band.hide,
                item_classes=["Stackable Currency"],
                base_types=band.base_types,
                display=build_display(band.display, display_variables),
            )
        )

    return blocks


def build_armour_blocks(
    armour_filter_data: ArmourFilterData, display_variables: DisplayVariablesFilterData
):
    blocks = []
    for rule in armour_filter_data.rules:
        if isinstance(rule.display, str):
            display = None
        else:
            display = build_display(rule.display, display_variables)

        if rule.base_types:
            base_types = rule.base_types
        elif rule.bands:
            base_types = get_bands(rule.bands, armour_filter_data.armour_categories)
        else:
            base_types = None

        blocks.append(
            Block(
                comment=rule.comment,
                hide=rule.hide,
                display=display,
                base_types=base_types,
                item_classes=rule.armour_classes,
            )
        )
    return blocks


def get_bands(
    band: dict[AttributeGroup, list[BandNames]],
    armour_bands: dict[AttributeGroup, dict[BandNames, Band]],
):
    base_types = []
    for attribute_group, band_names in band.items():
        for band_name in band_names:
            target_band = armour_bands[attribute_group][band_name]
            base_types.extend(target_band.base_types)

    return base_types


# Handle color substitions
def build_display(display: Display | None, display_variables: DisplayVariablesFilterData):
    if display is None:
        return None

    resolved_text_color = resolve_color(display.text_color, display_variables.colors.text)
    resolved_border_color = resolve_color(display.border_color, display_variables.colors.border)
    resolved_background_color = resolve_color(
        display.background_color, display_variables.colors.background
    )

    resolved_font_size = resolve_font_size(display.font_size, display_variables.font_size)
    resolved_sound_alert = resolve_sound_alert(display.sound_alert, display_variables.sound_alert)
    resolved_play_effect = None
    resolved_minimap_icon = None
    if display.play_effect:
        temp = " Temp" if display.play_effect.temp else ""
        resolved_play_effect = f"{display.play_effect.color}{temp}"
    if display.minimap_icon:
        resolved_minimap_icon = (
            f"{display.minimap_icon.size} {display.minimap_icon.color} {display.minimap_icon.shape}"
        )

    return ResolvedDisplay(
        play_effect=resolved_play_effect,
        minimap_icon=resolved_minimap_icon,
        text_color=resolved_text_color,
        background_color=resolved_background_color,
        border_color=resolved_border_color,
        font_size=resolved_font_size,
        sound_alert=resolved_sound_alert,
    )


def resolve_color(color_str: str | None, color_map: dict[str, Color]):
    if color_str and color_str.startswith("$"):
        color = color_str.removeprefix("$")
        # TODO: add warning if not found
        color_tuple = color_map.get(color)
        if color_tuple:
            return " ".join(str(c) for c in color_tuple)
        else:
            return None


def resolve_font_size(font_str: str | None, font_size_map: dict[str, int]):
    if font_str and font_str.startswith("$"):
        size = font_str.removeprefix("$")
        # TODO: add warning if not found
        return str(font_size_map.get(size))


def resolve_sound_alert(sound_str: str | None, sound_alert_map: dict[str, SoundAlert]):
    if sound_str and sound_str.startswith("$"):
        alert = sound_str.removeprefix("$")
        sound_alert = sound_alert_map.get(alert)
        # TODO: add warning if not found
        if sound_alert:
            return f"{sound_alert.id} {sound_alert.volume}"
        else:
            return None
