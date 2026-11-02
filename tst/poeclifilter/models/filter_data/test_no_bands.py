import pytest
from builders import make_no_bands_filter_data

from poeclifilter.models.filter_data import files, no_bands


def raw_config(*rules):
    raw_rules = list(rules) or [{"id": "test_id", "comment": "test_comment", "hide": False}]
    return {"schema": 1, "rules": raw_rules}


def test_parse_keeps_schema():
    result = no_bands.parse(raw_config())
    assert result.schema == 1


def test_parse_keeps_rules_in_order():
    result = no_bands.parse(
        raw_config(
            {"id": "first", "comment": "c", "hide": False},
            {"id": "second", "comment": "c", "hide": True},
        )
    )
    assert [rule.id for rule in result.rules] == ["first", "second"]


def test_parse_rule_without_bands_has_none():
    result = no_bands.parse(raw_config())
    assert result.rules[0].bands is None


def test_parse_rejects_rule_with_bands():
    with pytest.raises(ValueError, match="no bands"):
        no_bands.parse(raw_config({"id": "r", "comment": "c", "hide": False, "bands": ["S"]}))


def test_parse_rejects_child_rule_with_bands():
    child = {"id": "child", "comment": "c", "bands": ["S"]}
    with pytest.raises(ValueError, match="no bands"):
        no_bands.parse(raw_config({"id": "r", "comment": "c", "hide": False, "rules": [child]}))


def test_parse_rule_bands_rejects_anything():
    with pytest.raises(ValueError):
        no_bands.parse_rule_bands([])


def test_resolve_bands_raises():
    with pytest.raises(TypeError):
        make_no_bands_filter_data().resolve_bands([])  # pyright: ignore[reportArgumentType]


def test_write_round_trips_rules(tmp_path):
    raw = raw_config(
        {
            "id": "quest_items",
            "comment": "Quest items",
            "hide": False,
            "item_classes": ["Quest Items"],
            "display": {"font_size": "$normal"},
        }
    )
    original = no_bands.parse(raw)
    files.write_filter_data(original, tmp_path, "no_bands.yaml")
    reread = files.read_filter_data(tmp_path, "no_bands.yaml", no_bands.parse)
    assert reread == original
    assert reread.rules[0].bands is None
