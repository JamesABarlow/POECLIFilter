from dataclasses import dataclass
from pathlib import Path

from poeclifilter import loader
from poeclifilter.models import display
from poeclifilter.models.display import Display

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
class DisplayVariablesFilterData:
    schema: int
    colors: ColorMap
    font_size: dict[str, int]
    sound_alert: dict[str, SoundAlert]
    displays: dict[str, Display | None]


def get_filter_data(config_dir: Path):
    raw = loader.load(Path(f"{config_dir}/{file_name}").read_text())
    return parse(raw)


def parse(raw):
    # TODO: Apply correct validation
    return DisplayVariablesFilterData(
        schema=raw["schema"],
        colors=ColorMap(**raw["colors"]),
        font_size=raw["font_size"],
        sound_alert={name: SoundAlert(**v) for name, v in raw["sound_alert"].items()},
        displays=parse_displays(raw["displays"]),
    )


def parse_displays(raw_displays):
    return {
        display_name: display.parse(raw_display)
        for display_name, raw_display in raw_displays.items()
    }
