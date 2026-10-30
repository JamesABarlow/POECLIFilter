import pytest

from poeclifilter import resources
from poeclifilter.filters import AttributeGroup, GameVersion
from poeclifilter.game import ArmourClass
from poeclifilter.models.item_data import armour


def raw_config(**categories):
    raw_categories = categories or {"str": {"Body Armours": {"Astral Plate": {"band": "A"}}}}
    return {"schema": 1, "game_version": "3.25", "categories": raw_categories}


def test_load_success():
    result = armour.get_item_data(resources.item_data_dir(GameVersion.POE1))
    assert result.schema is not None
    assert result.game_version is not None
    assert result.categories is not None


def test_parse_keeps_schema():
    result = armour.parse(raw_config())
    assert result.schema == 1


def test_parse_keeps_game_version():
    result = armour.parse(raw_config())
    assert result.game_version == "3.25"


def test_parse_keeps_attribute_groups():
    raw = raw_config(
        str={"Body Armours": {"Astral Plate": {"band": "A"}}},
        str_int={"Body Armours": {"Sacred Chainmail": {"band": "B"}}},
    )
    result = armour.parse(raw)
    assert set(result.categories) == {AttributeGroup.STR, AttributeGroup.STR_INT}


def test_parse_keeps_armour_classes():
    raw = raw_config(
        str={
            "Helmets": {"Royal Burgonet": {"band": "A"}},
            "Body Armours": {"Astral Plate": {"band": "A"}},
        }
    )
    result = armour.parse(raw)
    assert set(result.categories[AttributeGroup.STR]) == {
        ArmourClass.HELMETS,
        ArmourClass.BODY_ARMOURS,
    }


def test_parse_keeps_empty_armour_class():
    raw = raw_config(str={"Helmets": {}})
    result = armour.parse(raw)
    assert result.categories[AttributeGroup.STR][ArmourClass.HELMETS] == {}


def test_parse_keeps_item_band():
    raw = raw_config(str={"Body Armours": {"Astral Plate": {"band": "A"}}})
    result = armour.parse(raw)
    assert (
        result.categories[AttributeGroup.STR][ArmourClass.BODY_ARMOURS]["Astral Plate"].band == "A"
    )


def test_parse_converts_group_to_enum():
    result = armour.parse(raw_config())
    assert all(type(group) is AttributeGroup for group in result.categories)


def test_parse_converts_armour_class_to_enum():
    result = armour.parse(raw_config())
    assert all(
        type(armour_class) is ArmourClass
        for armour_classes in result.categories.values()
        for armour_class in armour_classes
    )


def test_parse_rejects_unknown_group():
    raw = raw_config(str_itn={"Body Armours": {"Sacred Chainmail": {"band": "A"}}})
    with pytest.raises(ValueError):
        armour.parse(raw)


def test_parse_rejects_unknown_armour_class():
    raw = raw_config(str={"Body Armour": {"Astral Plate": {"band": "A"}}})
    with pytest.raises(ValueError):
        armour.parse(raw)
