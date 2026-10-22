from dataclasses import dataclass
from enum import StrEnum
from importlib.resources import files

import poeclifilter
from poeclifilter import loader
from poeclifilter.game import IconColor, IconShape
from poeclifilter.models import display


class BandNames(StrEnum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"


# Variable for name here
file_paths = {
    "currency": files(poeclifilter).joinpath("base_filter_config", "currency.yaml")
}

# dataclass for banded items contains currency etc


@dataclass(frozen=True)
class PlayEffect:
    color: IconColor
    temp: bool


@dataclass(frozen=True)
class MinimapIcon:
    size: int
    color: IconColor
    shape: IconShape


@dataclass(frozen=True)
class Display:
    hide: bool
    play_effect: PlayEffect | None = None
    minimap_icon: MinimapIcon | None = None
    text_color: str | None = None
    background_color: str | None = None
    border_color: str | None = None
    font_size: str | None = None
    sound_alert: str | None = None


@dataclass(frozen=True)
class Band:
    display: Display
    items: list[str]
    stacked_items: dict[str, list[int]]


@dataclass(frozen=True)
class BandedItemClass:
    schema: int
    bands: dict[BandNames, Band]


@dataclass(frozen=True)
class BandedItems:
    currency: BandedItemClass


def get_banded_items():
    raw = {}
    for name, file in file_paths.items():
        raw[name] = loader.load(file.read_text())

    return BandedItems(currency=parse(raw["currency"]))


def parse(raw):

    # TODO: finish parsing and validation
    bands = {}
    for band_name in BandNames:
        bands[band_name.value] = parse_band(raw["bands"][band_name.value])

    return BandedItemClass(schema=raw["schema"], bands=bands)


def parse_band(raw_band):
    # TODO: stacked items needs doing
    display = parse_display(raw_band.get("display"))
    items = raw_band.get("items", [])
    return Band(display=display, items=items, stacked_items={})


def parse_display(raw_display):
    return Display(
        hide=raw_display.get("hide"),
        play_effect=parse_play_effect(raw_display.get("play_effect")),
        minimap_icon=parse_minimap_icon(raw_display.get("minimap_icon")),
        text_color=raw_display.get("text_color"),
        background_color=raw_display.get("background_color"),
        border_color=raw_display.get("border_color"),
        font_size=raw_display.get("font_size"),
        sound_alert=raw_display.get("sound_alert"),
    )


def parse_play_effect(raw_play_effect):
    if not raw_play_effect:
        return None

    color = IconColor(raw_play_effect["color"])
    return PlayEffect(**(raw_play_effect | {"color": color}))


def parse_minimap_icon(raw_minimap_icon):
    if not raw_minimap_icon:
        return None

    color = IconColor(raw_minimap_icon["color"])
    shape = IconShape(raw_minimap_icon["shape"])
    return MinimapIcon(**(raw_minimap_icon | {"color": color, "shape": shape}))
