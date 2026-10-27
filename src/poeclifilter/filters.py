from dataclasses import dataclass
from enum import StrEnum


class GameVersion(StrEnum):
    POE1 = "poe1"
    POE2 = "poe2"


@dataclass
class FilterRef:
    game_version: GameVersion
    name: str
