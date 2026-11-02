import pytest

from poeclifilter import resources
from poeclifilter.filters import BandNames, GameVersion
from poeclifilter.models.item_data import flasks


def raw_config(**categories):
    raw_categories = categories or {"utility": {"Quicksilver Flask": {"band": "B"}}}
    return {"schema": 1, "game_version": "3.25", "categories": raw_categories}


def test_load_success():
    result = flasks.get_item_data(resources.item_data_dir(GameVersion.POE1))
    assert result.schema is not None
    assert result.game_version is not None
    assert result.categories is not None


def test_parse_keeps_schema():
    result = flasks.parse(raw_config())
    assert result.schema == 1


def test_parse_keeps_game_version():
    result = flasks.parse(raw_config())
    assert result.game_version == "3.25"


def test_parse_keeps_categories():
    raw = raw_config(
        life={"Divine Life Flask": {"band": "C"}},
        utility={"Quicksilver Flask": {"band": "B"}},
    )
    result = flasks.parse(raw)
    assert set(result.categories) == {"life", "utility"}


def test_parse_keeps_empty_category():
    result = flasks.parse(raw_config(hybrid={}))
    assert result.categories["hybrid"] == {}


def test_parse_keeps_item_band():
    result = flasks.parse(raw_config())
    assert result.categories["utility"]["Quicksilver Flask"].band == BandNames.B


def test_parse_converts_band_to_enum():
    result = flasks.parse(raw_config())
    assert type(result.categories["utility"]["Quicksilver Flask"].band) is BandNames


def test_parse_rejects_unknown_band():
    with pytest.raises(ValueError):
        flasks.parse(raw_config(utility={"Quicksilver Flask": {"band": "Z"}}))
