from dataclasses import dataclass
from pathlib import Path

from poeclifilter import loader
from poeclifilter.filters import BandNames

file_name = "flasks.yaml"


@dataclass(frozen=True)
class FlaskEntry:
    band: BandNames


@dataclass(frozen=True)
class FlaskItemData:
    schema: int
    game_version: str
    categories: dict[str, dict[str, FlaskEntry]]


def get_item_data(config_dir: Path):
    raw = loader.load(Path(f"{config_dir}/{file_name}").read_text())
    return parse(raw)


def parse(raw):
    categories = {
        category: {name: FlaskEntry(band=BandNames(entry["band"])) for name, entry in items.items()}
        for category, items in raw["categories"].items()
    }

    return FlaskItemData(
        schema=raw["schema"], game_version=raw["game_version"], categories=categories
    )
