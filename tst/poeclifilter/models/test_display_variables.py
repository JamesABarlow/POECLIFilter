import pytest

from poeclifilter import resources
from poeclifilter.models import display_variables


def test_load_success():
    result = display_variables.get_display_variables(resources.base_config_dir("poe1"))
    assert result.colors != None
    assert result.font_size != None
    assert result.sound_alert != None
    assert result.schema != None


# TODO: More test once real validation is added.
