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


# The base types in one band of a section's band data
@dataclass(frozen=True)
class Band:
    base_types: list[str]


class GearGroup(StrEnum):
    STR = "str"
    DEX = "dex"
    INT = "int"
    STR_INT = "str_int"
    INT_DEX = "int_dex"
    DEX_STR = "dex_str"
    BOWS = "bows"
    CLAWS = "claws"
    DAGGERS = "daggers"
    ONE_HAND_SWORDS = "one_hand_swords"
    ONE_HAND_AXES = "one_hand_axes"
    ONE_HAND_MACES = "one_hand_maces"
    QUIVERS = "quivers"
    RUNE_DAGGERS = "rune_daggers"
    SCEPTRES = "sceptres"
    STAVES = "staves"
    THRUSTING_ONE_HAND_SWORDS = "thrusting_one_hand_swords"
    TWO_HAND_AXES = "two_hand_axes"
    TWO_HAND_MACES = "two_hand_maces"
    TWO_HAND_SWORDS = "two_hand_swords"
    WANDS = "wands"
    WARSTAVES = "warstaves"


# Talismans share the game's Amulets class but are banded separately
class JewelleryGroup(StrEnum):
    RINGS = "rings"
    AMULETS = "amulets"
    TALISMANS = "talismans"
    BELTS = "belts"


@dataclass
class FilterRef:
    game_version: GameVersion
    name: str


def is_valid_filter_name(name: str) -> bool:
    return bool(FILTER_NAME_PATTERN.fullmatch(name))
