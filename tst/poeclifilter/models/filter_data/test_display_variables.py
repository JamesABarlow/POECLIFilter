from poeclifilter import resources
from poeclifilter.filters import GameVersion
from poeclifilter.models.filter_data import display_variables


def test_load_success():
    result = display_variables.get_filter_data(resources.base_config_dir(GameVersion.POE1))
    assert result.colors != None
    assert result.font_size != None
    assert result.sound_alert != None
    assert result.schema != None


# TODO: More test once real validation is added.
