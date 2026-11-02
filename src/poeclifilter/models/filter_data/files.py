from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

from poeclifilter import loader, writer

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


def read_filter_data[T](config_dir: Path, file_name: str, parse: Callable[[Any], T]) -> T:
    return parse(loader.load((config_dir / file_name).read_text()))


def write_filter_data(filter_data: DataclassInstance, filter_dir: Path, file_name: str):
    (filter_dir / file_name).write_text(writer.dump(filter_data))
