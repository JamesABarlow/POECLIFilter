import pytest

from poeclifilter.filters import BandNames, GameVersion
from poeclifilter.game import IconColor, IconShape
from poeclifilter.models.filter_data import banded_items
from poeclifilter.models.filter_data.banded_items import Band
from poeclifilter.models.display import MinimapIcon, PlayEffect
from poeclifilter.resources import base_config_dir

MINIMAL_BAND = {"hide": False, "display": {}}

FULL_DISPLAY = {
    "play_effect": {"color": "Purple", "temp": False},
    "minimap_icon": {"size": 1, "color": "Purple", "shape": "Circle"},
    "text_color": "$purple",
    "background_color": "$white",
    "border_color": "$purple",
    "font_size": "$normal",
    "sound_alert": "$major",
}


def raw_config(**bands):
    raw_bands = {band.value: dict(MINIMAL_BAND) for band in BandNames}
    raw_bands.update(bands)
    return {"schema": 1, "bands": raw_bands}


def test_load_success():
    result = banded_items.get_banded_items(base_config_dir(GameVersion.POE1))
    assert result.currency is not None
    assert result.currency.schema is not None
    assert result.currency.bands is not None


def test_load_defines_every_band():
    result = banded_items.get_banded_items(base_config_dir(GameVersion.POE1))
    for band in BandNames:
        assert isinstance(result.currency.bands[band], Band)


def test_parse_keeps_schema():
    result = banded_items.parse(raw_config())
    assert result.schema == 1


def test_parse_returns_every_band():
    result = banded_items.parse(raw_config())
    assert len(result.bands) == len(BandNames)
    for band in BandNames:
        assert isinstance(result.bands[band], Band)


def test_parse_keeps_items():
    raw = raw_config(F={"hide": True, "display": {}, "items": ["Scroll of Wisdom"]})
    result = banded_items.parse(raw)
    assert result.bands[BandNames.F].items == ["Scroll of Wisdom"]


def test_parse_band_without_items_is_empty():
    result = banded_items.parse(raw_config())
    assert result.bands[BandNames.S].items == []


def test_parse_keeps_hide():
    raw = raw_config(F={"hide": True, "display": {}})
    bands = banded_items.parse(raw).bands
    assert bands[BandNames.F].hide is True
    assert bands[BandNames.S].hide is False


def test_parse_display_keeps_variable_references_unresolved():
    raw = raw_config(S={"hide": False, "display": FULL_DISPLAY})
    display = banded_items.parse(raw).bands[BandNames.S].display
    assert display.text_color == "$purple"
    assert display.background_color == "$white"
    assert display.border_color == "$purple"
    assert display.font_size == "$normal"
    assert display.sound_alert == "$major"


def test_parse_display_builds_nested_records():
    raw = raw_config(S={"hide": False, "display": FULL_DISPLAY})
    display = banded_items.parse(raw).bands[BandNames.S].display
    assert display.play_effect == PlayEffect(color=IconColor.PURPLE, temp=False)
    assert display.minimap_icon == MinimapIcon(
        size=1, color=IconColor.PURPLE, shape=IconShape.CIRCLE
    )


def test_parse_display_converts_game_values_to_enum_members():
    raw = raw_config(S={"hide": False, "display": FULL_DISPLAY})
    display = banded_items.parse(raw).bands[BandNames.S].display
    # Equality alone cannot prove this: StrEnum members compare equal to their
    # values, so the assertions above pass on plain strings too.
    assert display.play_effect and isinstance(display.play_effect.color, IconColor)
    assert display.minimap_icon and isinstance(display.minimap_icon.color, IconColor)
    assert display.minimap_icon and isinstance(display.minimap_icon.shape, IconShape)


def test_parse_display_rejects_unknown_color():
    raw = raw_config(
        S={
            "hide": False,
            "display": {
                "play_effect": {"color": "Purpel", "temp": False},
            },
        }
    )
    with pytest.raises(ValueError) as error:
        banded_items.parse(raw)
    assert "Purpel" in str(error.value)


def test_parse_display_rejects_unknown_shape():
    raw = raw_config(
        S={
            "hide": False,
            "display": {
                "minimap_icon": {"size": 1, "color": "Purple", "shape": "Circel"},
            },
        }
    )
    with pytest.raises(ValueError) as error:
        banded_items.parse(raw)
    assert "Circel" in str(error.value)


def test_parse_display_rejects_unknown_nested_field():
    raw = raw_config(
        S={
            "hide": False,
            "display": {
                "play_effect": {"color": "Purple", "temp": False, "beam": True},
            },
        }
    )
    with pytest.raises(TypeError) as error:
        banded_items.parse(raw)
    assert "beam" in str(error.value)


def test_parse_display_omitted_fields_are_none():
    display = banded_items.parse(raw_config()).bands[BandNames.A].display
    assert display.play_effect is None
    assert display.minimap_icon is None
    assert display.text_color is None
    assert display.background_color is None
    assert display.border_color is None
    assert display.font_size is None
    assert display.sound_alert is None


def test_parse_missing_band_raises():
    raw = raw_config()
    del raw["bands"]["D"]
    with pytest.raises(KeyError) as error:
        banded_items.parse(raw)
    assert "D" in str(error.value)
