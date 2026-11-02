import pytest

from poeclifilter import resources
from poeclifilter.filters import BandNames, GameVersion
from poeclifilter.models.item_data import uniques


def raw_config(**categories):
    raw_categories = categories or {
        "belts": {"Leather Belt": {"band": "S", "uniques": ["Headhunter"]}}
    }
    return {"schema": 1, "game_version": "3.25", "categories": raw_categories}


def test_load_success():
    result = uniques.get_item_data(resources.item_data_dir(GameVersion.POE1))
    assert result.schema is not None
    assert result.game_version is not None
    assert result.categories is not None


def test_parse_keeps_schema():
    result = uniques.parse(raw_config())
    assert result.schema == 1


def test_parse_keeps_game_version():
    result = uniques.parse(raw_config())
    assert result.game_version == "3.25"


def test_parse_keeps_categories():
    raw = raw_config(
        belts={"Leather Belt": {"band": "S", "uniques": ["Headhunter"]}},
        rings={"Iron Ring": {"band": "F", "uniques": ["Le Heup of All"]}},
    )
    result = uniques.parse(raw)
    assert set(result.categories) == {"belts", "rings"}


def test_parse_keeps_empty_category():
    result = uniques.parse(raw_config(rings={}))
    assert result.categories["rings"] == {}


def test_parse_keeps_item_band():
    result = uniques.parse(raw_config())
    assert result.categories["belts"]["Leather Belt"].band == BandNames.S


def test_parse_converts_band_to_enum():
    result = uniques.parse(raw_config())
    assert type(result.categories["belts"]["Leather Belt"].band) is BandNames


def test_parse_rejects_unknown_band():
    with pytest.raises(ValueError):
        uniques.parse(raw_config(belts={"Leather Belt": {"band": "Z", "uniques": []}}))


def test_parse_keeps_uniques_in_order():
    raw = raw_config(
        belts={"Leather Belt": {"band": "S", "uniques": ["Headhunter", "Wurm's Molt"]}}
    )
    result = uniques.parse(raw)
    assert result.categories["belts"]["Leather Belt"].uniques == ["Headhunter", "Wurm's Molt"]


def test_parse_requires_uniques():
    # Unlike currency's optional stacks, every base must say which uniques drop on it
    with pytest.raises(KeyError):
        uniques.parse(raw_config(belts={"Leather Belt": {"band": "S"}}))
