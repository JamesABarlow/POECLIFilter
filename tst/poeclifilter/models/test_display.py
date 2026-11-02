import pytest

from poeclifilter.game import IconColor, IconShape
from poeclifilter.models import display
from poeclifilter.models.display import Display, MinimapIcon, PlayEffect

FULL_DISPLAY = {
    "play_effect": {"color": "Purple", "temp": False},
    "minimap_icon": {"size": 1, "color": "Purple", "shape": "Circle"},
    "text_color": "$purple",
    "background_color": "$white",
    "border_color": "$purple",
    "font_size": "$normal",
    "sound_alert": "$major",
}


def test_parse_missing_display_is_none():
    assert display.parse(None) is None


def test_parse_empty_display_leaves_every_field_unset():
    assert display.parse({}) == Display()


def test_parse_keeps_variable_references_unresolved():
    result = display.parse(FULL_DISPLAY)
    assert result is not None
    assert result.text_color == "$purple"
    assert result.background_color == "$white"
    assert result.border_color == "$purple"
    assert result.font_size == "$normal"
    assert result.sound_alert == "$major"


def test_parse_builds_nested_records():
    result = display.parse(FULL_DISPLAY)
    assert result is not None
    assert result.play_effect == PlayEffect(color=IconColor.PURPLE, temp=False)
    assert result.minimap_icon == MinimapIcon(
        size=1, color=IconColor.PURPLE, shape=IconShape.CIRCLE
    )


def test_parse_play_effect_without_temp_is_none():
    result = display.parse({"play_effect": {"color": "Purple"}})
    assert result is not None
    assert result.play_effect == PlayEffect(color=IconColor.PURPLE, temp=None)


def test_parse_converts_game_values_to_enum_members():
    result = display.parse(FULL_DISPLAY)
    assert result is not None
    # Equality alone cannot prove this: StrEnum members compare equal to their
    # values, so the assertions above pass on plain strings too.
    assert result.play_effect and isinstance(result.play_effect.color, IconColor)
    assert result.minimap_icon and isinstance(result.minimap_icon.color, IconColor)
    assert result.minimap_icon and isinstance(result.minimap_icon.shape, IconShape)


def test_parse_rejects_unknown_color():
    with pytest.raises(ValueError) as error:
        display.parse({"play_effect": {"color": "Purpel", "temp": False}})
    assert "Purpel" in str(error.value)


def test_parse_rejects_unknown_shape():
    with pytest.raises(ValueError) as error:
        display.parse({"minimap_icon": {"size": 1, "color": "Purple", "shape": "Circel"}})
    assert "Circel" in str(error.value)


def test_parse_rejects_unknown_nested_field():
    with pytest.raises(TypeError) as error:
        display.parse({"play_effect": {"color": "Purple", "temp": False, "beam": True}})
    assert "beam" in str(error.value)
