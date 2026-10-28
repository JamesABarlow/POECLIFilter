import os
from importlib.resources import files
from pathlib import Path

import poeclifilter
from poeclifilter.filters import FilterRef, GameVersion


def config_root() -> Path:
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg_config_home) if xdg_config_home else Path.home() / ".config"
    return base / "poeclifilter"


def base_config_dir(game_version: GameVersion) -> Path:
    return Path(files(poeclifilter).joinpath(game_version, "base_filter_config"))


def item_data_dir(game_version: GameVersion) -> Path:
    return Path(files(poeclifilter).joinpath(game_version, "item_data"))


def filters_root(game_version: GameVersion) -> Path:
    return config_root().joinpath("filters", game_version)


def filter_dir(filter: FilterRef) -> Path:
    return filters_root(filter.game_version).joinpath(filter.name)


def list_filter_names(game_version: GameVersion) -> list[str]:
    filters_root_path = filters_root(game_version)
    if not filters_root_path.is_dir():
        return []
    return sorted(p.name for p in filters_root_path.iterdir() if p.is_dir())
