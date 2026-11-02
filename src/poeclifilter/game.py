from enum import StrEnum


class IconColor(StrEnum):
    RED = "Red"
    GREEN = "Green"
    BLUE = "Blue"
    BROWN = "Brown"
    WHITE = "White"
    YELLOW = "Yellow"
    CYAN = "Cyan"
    GREY = "Grey"
    ORANGE = "Orange"
    PINK = "Pink"
    PURPLE = "Purple"


class IconShape(StrEnum):
    CIRCLE = "Circle"
    DIAMOND = "Diamond"
    HEXAGON = "Hexagon"
    SQUARE = "Square"
    STAR = "Star"
    TRIANGLE = "Triangle"
    CROSS = "Cross"
    MOON = "Moon"
    RAINDROP = "Raindrop"
    KITE = "Kite"
    PENTAGON = "Pentagon"
    UPSIDE_DOWN_HOUSE = "UpsideDownHouse"


class ArmourClass(StrEnum):
    HELMETS = "Helmets"
    BODY_ARMOURS = "Body Armours"
    GLOVES = "Gloves"
    BOOTS = "Boots"
    SHIELDS = "Shields"


class WeaponClass(StrEnum):
    BOWS = "Bows"
    CLAWS = "Claws"
    DAGGERS = "Daggers"
    ONE_HAND_SWORDS = "One Hand Swords"
    ONE_HAND_AXES = "One Hand Axes"
    ONE_HAND_MACES = "One Hand Maces"
    QUIVERS = "Quivers"
    RUNE_DAGGERS = "Rune Daggers"
    SCEPTRES = "Sceptres"
    STAVES = "Staves"
    THRUSTING_ONE_HAND_SWORDS = "Thrusting One Hand Swords"
    TWO_HAND_AXES = "Two Hand Axes"
    TWO_HAND_MACES = "Two Hand Maces"
    TWO_HAND_SWORDS = "Two Hand Swords"
    WANDS = "Wands"
    WARSTAVES = "Warstaves"


class Rarity(StrEnum):
    NORMAL = "Normal"
    MAGIC = "Magic"
    RARE = "Rare"
    UNIQUE = "Unique"


class Operator(StrEnum):
    LESS_THAN = "<"
    LESS_EQUAL = "<="
    EQUAL = "=="
    GREATER_EQUAL = ">="
    GREATER_THAN = ">"


COLOR_CHANNEL = (0, 255)
FONT_SIZE = (1, 45)
ICON_SIZE = (0, 2)
ALERT_SOUND_ID = (1, 16)
ALERT_SOUND_VOLUME = (0, 300)
