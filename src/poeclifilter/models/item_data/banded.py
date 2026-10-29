from dataclasses import dataclass
from pathlib import Path

from poeclifilter import loader

file_names = {"currency": "currency.yaml"}


@dataclass(frozen=True)
class ItemEntry:
    band: str
    stacks: list[int] | None = None


@dataclass(frozen=True)
class BandedItemDataClass:
    schema: int
    game_version: str
    base_types: dict[str, dict[str, ItemEntry]]


@dataclass(frozen=True)
class BandedItemData:
    currency: BandedItemDataClass


def get_item_data(config_dir: Path):
    raw = {}
    for name, file in file_names.items():
        raw[name] = loader.load(Path(f"{config_dir}/{file}").read_text())

    return BandedItemData(currency=parse(raw["currency"]))


def parse(raw):
    base_types = {
        category: {
            name: ItemEntry(band=entry["band"], stacks=entry.get("stacks"))
            for name, entry in items.items()
        }
        for category, items in raw["base_types"].items()
    }
    return BandedItemDataClass(
        schema=raw["schema"], game_version=raw["game_version"], base_types=base_types
    )
