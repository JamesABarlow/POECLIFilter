from dataclasses import dataclass
from pathlib import Path

from poeclifilter import loader
from poeclifilter.filters import BandNames, JewelleryGroup

file_name = "jewellery.yaml"


@dataclass(frozen=True)
class JewelleryEntry:
    band: BandNames


@dataclass(frozen=True)
class JewelleryItemData:
    schema: int
    game_version: str
    # No class level, like weapons: a jewellery group is its class, except talismans (Amulets)
    categories: dict[JewelleryGroup, dict[str, JewelleryEntry]]


def get_item_data(config_dir: Path):
    raw = loader.load(Path(f"{config_dir}/{file_name}").read_text())
    return parse(raw)


def parse(raw):
    categories = {
        JewelleryGroup(group): {
            name: JewelleryEntry(band=BandNames(entry["band"])) for name, entry in bases.items()
        }
        for group, bases in raw["categories"].items()
    }

    return JewelleryItemData(
        schema=raw["schema"], game_version=raw["game_version"], categories=categories
    )
