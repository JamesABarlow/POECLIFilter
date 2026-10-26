from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path

import poeclifilter

FILTERS_ROOT = Path("filters")


def base_config_dir():
    return str(files(poeclifilter).joinpath("base_filter_config"))


def item_data_dir():
    return str(files(poeclifilter).joinpath("item_data"))


def filters_root() -> Path:
    return FILTERS_ROOT


def filter_dir(name: str) -> Path:
    return FILTERS_ROOT / name


def list_filter_names() -> list[str]:
    if not FILTERS_ROOT.is_dir():
        return []
    return sorted(p.name for p in FILTERS_ROOT.iterdir() if p.is_dir())
