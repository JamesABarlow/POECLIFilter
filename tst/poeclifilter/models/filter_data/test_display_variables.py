from poeclifilter import loader, resources
from poeclifilter.filters import GameVersion
from poeclifilter.models.filter_data import display_variables


def test_load_success():
    result = display_variables.get_filter_data(resources.base_config_dir(GameVersion.POE1))
    assert result.colors != None
    assert result.font_size != None
    assert result.sound_alert != None
    assert result.displays != None
    assert result.schema != None


def test_empty_named_display_parses_to_none():
    raw = loader.load("""
schema: 1
colors: {background: {}, border: {}, text: {}}
font_size: {}
sound_alert: {}
displays:
  default:
""")

    result = display_variables.parse(raw)

    assert result.displays == {"default": None}


# TODO: More test once real validation is added.
