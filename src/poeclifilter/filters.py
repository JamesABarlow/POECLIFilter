import re
from dataclasses import dataclass
from enum import StrEnum

FILTER_NAME_PATTERN = re.compile(r"[A-Za-z]+")


class GameVersion(StrEnum):
    POE1 = "poe1"
    POE2 = "poe2"


class BandNames(StrEnum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"


class AttributeGroup(StrEnum):
    STR = "str"
    DEX = "dex"
    INT = "int"
    STR_INT = "str_int"
    INT_DEX = "int_dex"
    DEX_STR = "dex_str"


@dataclass
class FilterRef:
    game_version: GameVersion
    name: str


def is_valid_filter_name(name: str) -> bool:
    return bool(FILTER_NAME_PATTERN.fullmatch(name))
