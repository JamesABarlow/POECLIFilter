from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path

import poeclifilter
from poeclifilter.game import GameVersion

FILTERS_ROOT = Path("filters")


def base_config_dir(game_version: GameVersion):
    return str(files(poeclifilter).joinpath(game_version, "base_filter_config"))


def item_data_dir(game_version: GameVersion):
    return str(files(poeclifilter).joinpath(game_version, "item_data"))


def filters_root(game_version: GameVersion) -> Path:
    return FILTERS_ROOT.joinpath(game_version)


def filter_dir(name: str, game_version: GameVersion) -> Path:
    return filters_root(game_version) / name


def list_filter_names(game_version: GameVersion) -> list[str]:
    filters_root_path = filters_root(game_version)
    if not filters_root_path.is_dir():
        return []
    return sorted(p.name for p in filters_root_path.iterdir() if p.is_dir())
