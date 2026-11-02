from dataclasses import dataclass
from pathlib import Path

from poeclifilter import loader
from poeclifilter.filters import BandNames, GearGroup

file_name = "weapons.yaml"


@dataclass(frozen=True)
class WeaponEntry:
    band: BandNames


@dataclass(frozen=True)
class WeaponItemData:
    schema: int
    game_version: str
    # No class level, unlike armour: a weapon's group is its class
    categories: dict[GearGroup, dict[str, WeaponEntry]]


def get_item_data(config_dir: Path):
    raw = loader.load(Path(f"{config_dir}/{file_name}").read_text())
    return parse(raw)


def parse(raw):
    categories = {
        GearGroup(group): {
            name: WeaponEntry(band=BandNames(entry["band"])) for name, entry in bases.items()
        }
        for group, bases in raw["categories"].items()
    }

    return WeaponItemData(
        schema=raw["schema"], game_version=raw["game_version"], categories=categories
    )
