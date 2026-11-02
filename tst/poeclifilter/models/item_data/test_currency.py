import pytest

from poeclifilter import resources
from poeclifilter.filters import BandNames, GameVersion
from poeclifilter.models.item_data import currency


def raw_config(**categories):
    raw_categories = categories or {"base": {"Divine Orb": {"band": "S"}}}
    return {"schema": 1, "game_version": "3.25", "categories": raw_categories}


def test_load_success():
    result = currency.get_item_data(resources.item_data_dir(GameVersion.POE1))
    assert result.schema is not None
    assert result.game_version is not None
    assert result.categories is not None


def test_parse_keeps_schema():
    result = currency.parse(raw_config())
    assert result.schema == 1


def test_parse_keeps_game_version():
    result = currency.parse(raw_config())
    assert result.game_version == "3.25"


def test_parse_keeps_categories():
    raw = raw_config(
        base={"Divine Orb": {"band": "S"}},
        fossils={"Hollow Fossil": {"band": "S"}},
    )
    result = currency.parse(raw)
    assert set(result.categories) == {"base", "fossils"}


def test_parse_keeps_empty_category():
    result = currency.parse(raw_config(fossils={}))
    assert result.categories["fossils"] == {}


def test_parse_keeps_item_band():
    result = currency.parse(raw_config())
    assert result.categories["base"]["Divine Orb"].band == BandNames.S


def test_parse_converts_band_to_enum():
    result = currency.parse(raw_config())
    assert type(result.categories["base"]["Divine Orb"].band) is BandNames


def test_parse_rejects_unknown_band():
    with pytest.raises(ValueError):
        currency.parse(raw_config(base={"Divine Orb": {"band": "Z"}}))


def test_parse_item_without_stacks_is_none():
    result = currency.parse(raw_config())
    assert result.categories["base"]["Divine Orb"].stacks is None


def test_parse_keeps_stacks():
    raw = raw_config(base={"Scroll of Wisdom": {"band": "E", "stacks": [20, 40]}})
    result = currency.parse(raw)
    assert result.categories["base"]["Scroll of Wisdom"].stacks == [20, 40]
