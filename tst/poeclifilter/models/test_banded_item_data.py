from poeclifilter import resources
from poeclifilter.filters import GameVersion
from poeclifilter.models import banded_item_data


def raw_config(**basetypes):
    raw_basetypes = basetypes or {"base": {"Divine Orb": {"band": "A"}}}
    return {"schema": 1, "game_version": "3.25", "basetypes": raw_basetypes}


def test_load_success():
    result = banded_item_data.get_banded_item_data(resources.item_data_dir(GameVersion.POE1))
    assert result.currency is not None
    assert result.currency.schema is not None
    assert result.currency.game_version is not None
    assert result.currency.basetypes is not None


def test_parse_keeps_schema():
    result = banded_item_data.parse(raw_config())
    assert result.schema == 1


def test_parse_keeps_game_version():
    result = banded_item_data.parse(raw_config())
    assert result.game_version == "3.25"


def test_parse_keeps_categories():
    raw = raw_config(
        base={"Divine Orb": {"band": "A"}},
        fossils={"Hollow Fossil": {"band": "S"}},
    )
    result = banded_item_data.parse(raw)
    assert set(result.basetypes) == {"base", "fossils"}


def test_parse_keeps_item_band():
    raw = raw_config(base={"Divine Orb": {"band": "A"}})
    result = banded_item_data.parse(raw)
    assert result.basetypes["base"]["Divine Orb"].band == "A"


def test_parse_item_without_stacks_is_none():
    raw = raw_config(base={"Divine Orb": {"band": "A"}})
    result = banded_item_data.parse(raw)
    assert result.basetypes["base"]["Divine Orb"].stacks is None


def test_parse_keeps_stacks():
    raw = raw_config(base={"Scroll of Wisdom": {"band": "E", "stacks": [20, 40]}})
    result = banded_item_data.parse(raw)
    assert result.basetypes["base"]["Scroll of Wisdom"].stacks == [20, 40]
