from dataclasses import dataclass
from pathlib import Path

from poeclifilter import loader
from poeclifilter.filters import BandNames

file_name = "uniques.yaml"


@dataclass(frozen=True)
class UniqueEntry:
    band: BandNames
    uniques: list[str]


@dataclass(frozen=True)
class UniqueItemData:
    schema: int
    game_version: str
    categories: dict[str, dict[str, UniqueEntry]]


def get_item_data(config_dir: Path):
    raw = loader.load(Path(f"{config_dir}/{file_name}").read_text())
    return parse(raw)


def parse(raw):
    categories = {
        category: {
            name: UniqueEntry(band=BandNames(entry["band"]), uniques=entry["uniques"])
            for name, entry in items.items()
        }
        for category, items in raw["categories"].items()
    }

    return UniqueItemData(
        schema=raw["schema"], game_version=raw["game_version"], categories=categories
    )
