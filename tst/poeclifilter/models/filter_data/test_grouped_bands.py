from enum import StrEnum

import pytest
from builders import make_band, make_grouped_bands_filter_data

from poeclifilter.filters import BandNames
from poeclifilter.models.filter_data import files, grouped_bands


# A group enum of the tests' own, so these tests check grouped bands work with any StrEnum,
# not just gear's groups
class Group(StrEnum):
    FIRST = "first"
    SECOND = "second"


def parse(raw):
    return grouped_bands.parse(raw, Group)


def raw_config(**groups):
    raw_groups = groups or {
        "first": {"A": {"base_types": ["Astral Plate"]}},
        "second": {"A": {"base_types": ["Thicket Bow"]}},
    }
    rule = {"id": "test_id", "comment": "test_comment", "hide": False}
    return {"schema": 1, "bands": raw_groups, "rules": [rule]}


def test_parse_keeps_schema():
    result = parse(raw_config())
    assert result.schema == 1


def test_parse_keeps_groups():
    result = parse(raw_config())
    assert set(result.bands) == {Group.FIRST, Group.SECOND}


def test_parse_converts_group_to_the_given_enum():
    result = parse(raw_config())
    assert all(type(group) is Group for group in result.bands)


def test_parse_rejects_group_not_in_the_given_enum():
    # A real gear group, but not a Group: proves the module uses the enum it is given
    raw = raw_config(str={"A": {"base_types": ["Astral Plate"]}})
    with pytest.raises(ValueError):
        parse(raw)


def test_parse_keeps_bands():
    raw = raw_config(first={"S": {"base_types": []}, "A": {"base_types": ["Astral Plate"]}})
    result = parse(raw)
    assert set(result.bands[Group.FIRST]) == {BandNames.S, BandNames.A}


def test_parse_converts_band_name_to_enum():
    result = parse(raw_config())
    assert all(type(band_name) is BandNames for band_name in result.bands[Group.FIRST])


def test_parse_rejects_unknown_band_name():
    raw = raw_config(first={"Z": {"base_types": []}})
    with pytest.raises(ValueError):
        parse(raw)


def test_parse_keeps_band_base_types():
    raw = raw_config(first={"A": {"base_types": ["Astral Plate", "Glorious Plate"]}})
    result = parse(raw)
    assert result.bands[Group.FIRST][BandNames.A].base_types == [
        "Astral Plate",
        "Glorious Plate",
    ]


def test_parse_band_without_base_types_is_empty():
    raw = raw_config(first={"A": {}})
    result = parse(raw)
    assert result.bands[Group.FIRST][BandNames.A].base_types == []


def test_parse_rule_bands_converts_to_the_given_enums():
    result = grouped_bands.parse_rule_bands({"first": ["A"], "second": ["B"]}, Group)
    assert result == {Group.FIRST: [BandNames.A], Group.SECOND: [BandNames.B]}
    assert all(type(group) is Group for group in result)
    assert all(type(band) is BandNames for bands in result.values() for band in bands)


def test_parse_rule_bands_rejects_group_not_in_the_given_enum():
    with pytest.raises(ValueError):
        grouped_bands.parse_rule_bands({"str": ["A"]}, Group)


def test_parse_rule_bands_rejects_unknown_band():
    with pytest.raises(ValueError):
        grouped_bands.parse_rule_bands({"first": ["Z"]}, Group)


def test_parse_uses_the_given_enum_for_rule_bands():
    raw = raw_config()
    raw["rules"] = [{"id": "r", "comment": "c", "hide": False, "bands": {"second": ["A"]}}]
    result = parse(raw)
    assert result.rules[0].bands == {Group.SECOND: [BandNames.A]}


def test_write_creates_file(tmp_path):
    files.write_filter_data(parse(raw_config()), tmp_path, "grouped.yaml")
    assert (tmp_path / "grouped.yaml").exists()


def test_write_round_trips(tmp_path):
    original = parse(
        raw_config(
            first={"S": {"base_types": []}, "A": {"base_types": ["Astral Plate"]}},
            second={"A": {"base_types": ["Syndicate's Garb"]}},
        )
    )
    files.write_filter_data(original, tmp_path, "grouped.yaml")
    assert files.read_filter_data(tmp_path, "grouped.yaml", parse) == original


def test_write_round_trips_rule_bands(tmp_path):
    # Field names are the written YAML keys, so a rule field renamed away from the key the
    # parser reads would lose every rule's bands on write
    raw = raw_config()
    raw["rules"] = [
        {
            "id": "endgame_rares",
            "comment": "Rares shown in endgame",
            "hide": False,
            "bands": {"first": ["A"], "second": ["A"]},
            "rarity": {"operator": "==", "rarity": "Rare"},
        }
    ]
    original = parse(raw)
    files.write_filter_data(original, tmp_path, "grouped.yaml")
    reread = files.read_filter_data(tmp_path, "grouped.yaml", parse)
    assert reread == original
    assert reread.rules[0].bands == {Group.FIRST: [BandNames.A], Group.SECOND: [BandNames.A]}


def test_resolve_bands_returns_the_bands_base_types():
    grouped_bands_filter_data = make_grouped_bands_filter_data(
        bands={Group.FIRST: {BandNames.A: make_band(base_types=["Astral Plate"])}}
    )
    assert grouped_bands_filter_data.resolve_bands({Group.FIRST: [BandNames.A]}) == ["Astral Plate"]


def test_resolve_bands_joins_bands_across_groups_and_band_names():
    grouped_bands_filter_data = make_grouped_bands_filter_data(
        bands={
            Group.FIRST: {
                BandNames.S: make_band(base_types=["Glorious Plate"]),
                BandNames.A: make_band(base_types=["Astral Plate"]),
            },
            Group.SECOND: {BandNames.A: make_band(base_types=["Thicket Bow"])},
        }
    )
    result = grouped_bands_filter_data.resolve_bands(
        {Group.FIRST: [BandNames.A, BandNames.S], Group.SECOND: [BandNames.A]}
    )
    assert result == ["Astral Plate", "Glorious Plate", "Thicket Bow"]


def test_resolve_bands_of_empty_band_is_empty():
    grouped_bands_filter_data = make_grouped_bands_filter_data(
        bands={Group.FIRST: {BandNames.B: make_band()}}
    )
    assert grouped_bands_filter_data.resolve_bands({Group.FIRST: [BandNames.B]}) == []
