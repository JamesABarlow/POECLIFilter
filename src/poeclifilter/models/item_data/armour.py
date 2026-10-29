from dataclasses import dataclass
from pathlib import Path

from poeclifilter import loader
from poeclifilter.filters import AttributeGroup

file_name = "armour.yaml"


@dataclass(frozen=True)
class ArmourEntry:
    band: str


@dataclass(frozen=True)
class ArmourItemData:
    schema: int
    game_version: str
    armour_types: dict[AttributeGroup, dict[str, ArmourEntry]]


# TODO: does this really need to be seperate from other banded items anymore?
def get_item_data(config_dir: Path):
    raw = loader.load(Path(f"{config_dir}/{file_name}").read_text())
    return parse(raw)


def parse(raw):
    armour = {
        AttributeGroup(group): {
            name: ArmourEntry(band=entry["band"]) for name, entry in items.items()
        }
        for group, items in raw["armour_types"].items()
    }

    return ArmourItemData(
        schema=raw["schema"], game_version=raw["game_version"], armour_types=armour
    )
