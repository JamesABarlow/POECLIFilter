import pytest

from poeclifilter.models import display


def test_load_success():
    result = display.getDisplayVariables()
    assert result.colors != None
    assert result.font_size != None
    assert result.sound_alert != None
    assert result.schema != None


# TODO: More test once real validation is added.
