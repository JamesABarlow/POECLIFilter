from dataclasses import dataclass
from pathlib import Path

from poeclifilter import loader
from poeclifilter.filters import AttributeGroup
from poeclifilter.game import ArmourClass

file_name = "armour.yaml"


@dataclass(frozen=True)
class ArmourEntry:
    band: str


@dataclass(frozen=True)
class ArmourItemData:
    schema: int
    game_version: str
    categories: dict[AttributeGroup, dict[ArmourClass, dict[str, ArmourEntry]]]


# TODO: does this really need to be seperate from other banded items anymore?
def get_item_data(config_dir: Path):
    raw = loader.load(Path(f"{config_dir}/{file_name}").read_text())
    return parse(raw)


def parse(raw):
    categories = {
        AttributeGroup(group): {
            ArmourClass(armour_class): {
                name: ArmourEntry(band=entry["band"]) for name, entry in bases.items()
            }
            for armour_class, bases in armour_classes.items()
        }
        for group, armour_classes in raw["categories"].items()
    }

    return ArmourItemData(
        schema=raw["schema"], game_version=raw["game_version"], categories=categories
    )
