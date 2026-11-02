import pytest

from poeclifilter import resources
from poeclifilter.filters import BandNames, GameVersion
from poeclifilter.models.item_data import cards


def raw_config(**categories):
    raw_categories = categories or {"uniques": {"The Doctor": {"band": "S"}}}
    return {"schema": 1, "game_version": "3.25", "categories": raw_categories}


def test_load_success():
    result = cards.get_item_data(resources.item_data_dir(GameVersion.POE1))
    assert result.schema is not None
    assert result.game_version is not None
    assert result.categories is not None


def test_parse_keeps_schema():
    result = cards.parse(raw_config())
    assert result.schema == 1


def test_parse_keeps_game_version():
    result = cards.parse(raw_config())
    assert result.game_version == "3.25"


def test_parse_keeps_categories():
    raw = raw_config(
        currency={"House of Mirrors": {"band": "S"}},
        uniques={"The Doctor": {"band": "S"}},
    )
    result = cards.parse(raw)
    assert set(result.categories) == {"currency", "uniques"}


def test_parse_keeps_empty_category():
    result = cards.parse(raw_config(gear={}))
    assert result.categories["gear"] == {}


def test_parse_keeps_item_band():
    result = cards.parse(raw_config())
    assert result.categories["uniques"]["The Doctor"].band == BandNames.S


def test_parse_converts_band_to_enum():
    result = cards.parse(raw_config())
    assert type(result.categories["uniques"]["The Doctor"].band) is BandNames


def test_parse_rejects_unknown_band():
    with pytest.raises(ValueError):
        cards.parse(raw_config(uniques={"The Doctor": {"band": "Z"}}))
