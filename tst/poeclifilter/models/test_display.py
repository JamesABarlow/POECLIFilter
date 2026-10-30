from poeclifilter.models import display
from poeclifilter.models.display import Display


def test_parse_missing_display_is_none():
    assert display.parse(None) is None


def test_parse_empty_display_leaves_every_field_unset():
    assert display.parse({}) == Display()
