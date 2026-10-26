from dataclasses import dataclass

from poeclifilter.game import IconColor, IconShape


@dataclass(frozen=True)
class PlayEffect:
    color: IconColor
    temp: bool | None


@dataclass(frozen=True)
class MinimapIcon:
    size: int
    color: IconColor
    shape: IconShape


# TODO: hide here was a mistake. Not part of the display block
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


def parse(raw_display):
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
