import yaml
from builders import make_display, make_range, make_rule

from poeclifilter import writer


def dump_and_load(data):
    return yaml.safe_load(writer.dump(data))


def test_dump_drops_none_fields():
    result = dump_and_load(make_rule(id="rule", comment="", hide=False))
    assert result == {"id": "rule", "comment": "", "hide": False, "include": True}


def test_dump_drops_none_fields_in_nested_dataclasses():
    result = dump_and_load(make_rule(item_level=make_range(min=60)))
    assert result["item_level"] == {"min": 60}


def test_dump_writes_dataclass_with_every_field_unset_as_empty_mapping():
    result = dump_and_load(make_rule(display=make_display()))
    assert result["display"] == {}


def test_dump_keeps_falsy_values_that_are_not_none():
    result = dump_and_load(make_rule(hide=False, include=False, base_types=[]))
    assert result["hide"] is False
    assert result["include"] is False
    assert result["base_types"] == []
