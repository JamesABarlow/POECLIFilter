import pytest

from poeclifilter import resources
from poeclifilter.filters import AttributeGroup, GameVersion
from poeclifilter.models import armour_item_data


def raw_config(**armour_types):
    raw_armour_types = armour_types or {"str": {"Astral Plate": {"band": "A"}}}
    return {"schema": 1, "game_version": "3.25", "armour_types": raw_armour_types}


def test_load_success():
    result = armour_item_data.get_armour_item_data(resources.item_data_dir(GameVersion.POE1))
    assert result.schema is not None
    assert result.game_version is not None
    assert result.armour_types is not None


def test_parse_keeps_schema():
    result = armour_item_data.parse(raw_config())
    assert result.schema == 1


def test_parse_keeps_game_version():
    result = armour_item_data.parse(raw_config())
    assert result.game_version == "3.25"


def test_parse_keeps_attribute_groups():
    raw = raw_config(
        str={"Astral Plate": {"band": "A"}},
        str_int={"Sacred Chainmail": {"band": "B"}},
    )
    result = armour_item_data.parse(raw)
    assert set(result.armour_types) == {AttributeGroup.STR, AttributeGroup.STR_INT}


def test_parse_keeps_item_band():
    raw = raw_config(str={"Astral Plate": {"band": "A"}})
    result = armour_item_data.parse(raw)
    assert result.armour_types[AttributeGroup.STR]["Astral Plate"].band == "A"


def test_parse_converts_group_to_enum():
    result = armour_item_data.parse(raw_config())
    assert all(type(group) is AttributeGroup for group in result.armour_types)


def test_parse_rejects_unknown_group():
    raw = raw_config(str_itn={"Sacred Chainmail": {"band": "A"}})
    with pytest.raises(ValueError):
        armour_item_data.parse(raw)
