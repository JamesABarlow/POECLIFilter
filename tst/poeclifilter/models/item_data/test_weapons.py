import pytest

from poeclifilter import resources
from poeclifilter.filters import BandNames, GameVersion, GearGroup
from poeclifilter.models.item_data import weapons


def raw_config(**categories):
    raw_categories = categories or {"bows": {"Thicket Bow": {"band": "A"}}}
    return {"schema": 1, "game_version": "3.25", "categories": raw_categories}


def test_load_success():
    result = weapons.get_item_data(resources.item_data_dir(GameVersion.POE1))
    assert result.schema is not None
    assert result.game_version is not None
    assert result.categories is not None


def test_parse_keeps_schema():
    result = weapons.parse(raw_config())
    assert result.schema == 1


def test_parse_keeps_game_version():
    result = weapons.parse(raw_config())
    assert result.game_version == "3.25"


def test_parse_keeps_weapon_groups():
    raw = raw_config(
        bows={"Thicket Bow": {"band": "A"}},
        wands={"Imbued Wand": {"band": "S"}},
    )
    result = weapons.parse(raw)
    assert set(result.categories) == {GearGroup.BOWS, GearGroup.WANDS}


def test_parse_keeps_empty_group():
    result = weapons.parse(raw_config(bows={}))
    assert result.categories[GearGroup.BOWS] == {}


def test_parse_keeps_item_band():
    result = weapons.parse(raw_config())
    assert result.categories[GearGroup.BOWS]["Thicket Bow"].band == BandNames.A


def test_parse_converts_group_to_enum():
    result = weapons.parse(raw_config())
    assert all(type(group) is GearGroup for group in result.categories)


def test_parse_converts_band_to_enum():
    result = weapons.parse(raw_config())
    assert type(result.categories[GearGroup.BOWS]["Thicket Bow"].band) is BandNames


def test_parse_rejects_unknown_group():
    with pytest.raises(ValueError):
        weapons.parse(raw_config(bow={"Thicket Bow": {"band": "A"}}))


def test_parse_rejects_unknown_band():
    with pytest.raises(ValueError):
        weapons.parse(raw_config(bows={"Thicket Bow": {"band": "Z"}}))
