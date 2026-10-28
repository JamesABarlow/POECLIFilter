from dataclasses import dataclass
from pathlib import Path

import poeclifilter
from poeclifilter import loader

file_name = "display_variables.yaml"

Color = tuple[int, int, int, int]


@dataclass(frozen=True)
class SoundAlert:
    id: int
    volume: int


@dataclass(frozen=True)
class ColorMap:
    background: dict[str, Color]
    border: dict[str, Color]
    text: dict[str, Color]


@dataclass(frozen=True)
class DisplayVariables:
    schema: int
    colors: ColorMap
    font_size: dict[str, int]
    sound_alert: dict[str, SoundAlert]


def get_display_variables(config_dir: Path):
    raw = loader.load(Path(f"{config_dir}/{file_name}").read_text())
    return parse(raw)


def parse(raw):
    # TODO: Apply correct validation
    return DisplayVariables(
        schema=raw["schema"],
        colors=ColorMap(**raw["colors"]),
        font_size=raw["font_size"],
        sound_alert={name: SoundAlert(**v) for name, v in raw["sound_alert"].items()},
    )
