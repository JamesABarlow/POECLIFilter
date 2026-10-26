# Convert the filter settings to ordered block list that can be used to write the filter

from dataclasses import dataclass

from poeclifilter.models import banded_items
from poeclifilter.models.banded_items import (
    BandedItemClass,
    BandedItems,
    BandNames,
    get_banded_items,
)
from poeclifilter.models.display import Display, ResolvedDisplay
from poeclifilter.models.display_variables import (
    Color,
    DisplayVariables,
    SoundAlert,
    get_display_variables,
)
from poeclifilter.resources import base_config_dir


@dataclass(frozen=True)
class Block:
    comment: str
    hide: bool
    item_class: str | None
    base_type: list[str] | None
    display: ResolvedDisplay


def build_blocks():
    # These should be input as args, simplifies the testing
    display_variables = get_display_variables(base_config_dir())
    banded_items = get_banded_items(base_config_dir())

    blocks = []

    # Ordering matters here, will be the same ordering in the final model.
    blocks.extend(build_banded_items_blocks(banded_items, display_variables))

    # Add misc filter blocks including the final catch all here
    # TODO: This needs to be built better but here for now
    blocks.extend(
        [
            Block(
                comment="",
                hide=False,
                item_class=None,
                base_type=None,
                display=ResolvedDisplay(background_color="237 233 222 230"),
            )
        ]
    )

    return blocks


def build_banded_items_blocks(
    banded_items: BandedItems, display_variables: DisplayVariables
):
    blocks = []

    blocks.extend(build_bands(banded_items.currency, display_variables))

    return blocks


def build_bands(banded_class: BandedItemClass, display_variables: DisplayVariables):
    blocks = []
    for band_name in BandNames:
        band = banded_class.bands.get(band_name)

        if not band or not band.items:
            continue

        blocks.append(
            Block(
                comment="",
                hide=band.display.hide,
                item_class="Stackable Currency",
                base_type=band.items,
                display=build_display(band.display, display_variables),
            )
        )

    return blocks


# Handle color substitions
def build_display(display: Display, display_variables: DisplayVariables):

    resolved_text_color = resolve_color(
        display.text_color, display_variables.colors.text
    )
    resolved_border_color = resolve_color(
        display.border_color, display_variables.colors.border
    )
    resolved_background_color = resolve_color(
        display.background_color, display_variables.colors.background
    )

    resolved_font_size = resolve_font_size(
        display.font_size, display_variables.font_size
    )
    resolved_sound_alert = resolve_sound_alert(
        display.sound_alert, display_variables.sound_alert
    )
    resolved_play_effect = None
    resolved_minimap_icon = None
    if display.play_effect:
        temp = f" Temp" if display.play_effect.temp else ""
        resolved_play_effect = f"{display.play_effect.color}{temp}"
    if display.minimap_icon:
        resolved_minimap_icon = f"{display.minimap_icon.size} {display.minimap_icon.color} {display.minimap_icon.shape}"

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
