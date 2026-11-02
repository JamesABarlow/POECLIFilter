from dataclasses import dataclass
from pathlib import Path

from poeclifilter import loader
from poeclifilter.filters import BandNames

file_name = "currency.yaml"


@dataclass(frozen=True)
class CurrencyEntry:
    band: BandNames
    stacks: list[int] | None = None


@dataclass(frozen=True)
class CurrencyItemData:
    schema: int
    game_version: str
    # Categories only organise the data for editing; currency's filter bands are flat
    categories: dict[str, dict[str, CurrencyEntry]]


def get_item_data(config_dir: Path):
    raw = loader.load(Path(f"{config_dir}/{file_name}").read_text())
    return parse(raw)


def parse(raw):
    categories = {
        category: {
            name: CurrencyEntry(band=BandNames(entry["band"]), stacks=entry.get("stacks"))
            for name, entry in items.items()
        }
        for category, items in raw["categories"].items()
    }

    return CurrencyItemData(
        schema=raw["schema"], game_version=raw["game_version"], categories=categories
    )
