import pytest

from poeclifilter import resources
from poeclifilter.filters import BandNames, GameVersion, JewelleryGroup
from poeclifilter.models.item_data import jewellery


def raw_config(**categories):
    raw_categories = categories or {"rings": {"Steel Ring": {"band": "A"}}}
    return {"schema": 1, "game_version": "3.25", "categories": raw_categories}


def test_load_success():
    result = jewellery.get_item_data(resources.item_data_dir(GameVersion.POE1))
    assert result.schema is not None
    assert result.game_version is not None
    assert result.categories is not None


def test_parse_keeps_schema():
    result = jewellery.parse(raw_config())
    assert result.schema == 1


def test_parse_keeps_game_version():
    result = jewellery.parse(raw_config())
    assert result.game_version == "3.25"


def test_parse_keeps_jewellery_groups():
    raw = raw_config(
        rings={"Steel Ring": {"band": "A"}},
        talismans={"Black Maw Talisman": {"band": "B"}},
    )
    result = jewellery.parse(raw)
    assert set(result.categories) == {JewelleryGroup.RINGS, JewelleryGroup.TALISMANS}


def test_parse_keeps_empty_group():
    result = jewellery.parse(raw_config(belts={}))
    assert result.categories[JewelleryGroup.BELTS] == {}


def test_parse_keeps_item_band():
    result = jewellery.parse(raw_config())
    assert result.categories[JewelleryGroup.RINGS]["Steel Ring"].band == BandNames.A


def test_parse_converts_group_to_enum():
    result = jewellery.parse(raw_config())
    assert all(type(group) is JewelleryGroup for group in result.categories)


def test_parse_converts_band_to_enum():
    result = jewellery.parse(raw_config())
    assert type(result.categories[JewelleryGroup.RINGS]["Steel Ring"].band) is BandNames


def test_parse_rejects_unknown_group():
    with pytest.raises(ValueError):
        jewellery.parse(raw_config(ring={"Steel Ring": {"band": "A"}}))


def test_parse_rejects_unknown_band():
    with pytest.raises(ValueError):
        jewellery.parse(raw_config(rings={"Steel Ring": {"band": "Z"}}))
