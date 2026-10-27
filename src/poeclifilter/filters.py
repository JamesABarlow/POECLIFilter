import re
from dataclasses import dataclass
from enum import StrEnum

FILTER_NAME_PATTERN = re.compile(r"[A-Za-z]+")


class GameVersion(StrEnum):
    POE1 = "poe1"
    POE2 = "poe2"


@dataclass
class FilterRef:
    game_version: GameVersion
    name: str


def is_valid_filter_name(name: str) -> bool:
    return bool(FILTER_NAME_PATTERN.fullmatch(name))
