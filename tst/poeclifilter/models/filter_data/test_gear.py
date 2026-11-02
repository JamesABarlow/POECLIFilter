import pytest

from poeclifilter import resources
from poeclifilter.filters import BandNames, GameVersion, GearGroup
from poeclifilter.models.filter_data import gear


def raw_config(**groups):
    raw_groups = groups or {
        "str": {"A": {"base_types": ["Astral Plate"]}},
        "bows": {"A": {"base_types": ["Thicket Bow"]}},
    }
    rule = {"id": "test_id", "comment": "test_comment", "hide": False}
    return {"schema": 1, "bands": raw_groups, "rules": [rule]}


def test_load_success():
    result = gear.get_filter_data(resources.base_config_dir(GameVersion.POE1))
    assert result.schema is not None
    assert result.bands is not None


def test_parse_keeps_schema():
    result = gear.parse(raw_config())
    assert result.schema == 1


def test_parse_keeps_attribute_groups():
    raw = raw_config(
        str={"A": {"base_types": ["Astral Plate"]}},
        str_int={"A": {"base_types": ["Sacred Chainmail"]}},
    )
    result = gear.parse(raw)
    assert set(result.bands) == {GearGroup.STR, GearGroup.STR_INT}


def test_parse_converts_group_to_enum():
    result = gear.parse(raw_config())
    assert all(type(group) is GearGroup for group in result.bands)


def test_parse_rejects_unknown_group():
    raw = raw_config(str_itn={"A": {"base_types": ["Sacred Chainmail"]}})
    with pytest.raises(ValueError):
        gear.parse(raw)


def test_parse_keeps_bands():
    raw = raw_config(str={"S": {"base_types": []}, "A": {"base_types": ["Astral Plate"]}})
    result = gear.parse(raw)
    assert set(result.bands[GearGroup.STR]) == {BandNames.S, BandNames.A}


def test_parse_converts_band_name_to_enum():
    result = gear.parse(raw_config())
    assert all(type(band_name) is BandNames for band_name in result.bands[GearGroup.STR])


def test_parse_rejects_unknown_band_name():
    raw = raw_config(str={"Z": {"base_types": []}})
    with pytest.raises(ValueError):
        gear.parse(raw)


def test_parse_keeps_band_base_types():
    raw = raw_config(str={"A": {"base_types": ["Astral Plate", "Glorious Plate"]}})
    result = gear.parse(raw)
    assert result.bands[GearGroup.STR][BandNames.A].base_types == [
        "Astral Plate",
        "Glorious Plate",
    ]


def test_parse_band_without_base_types_is_empty():
    raw = raw_config(str={"A": {}})
    result = gear.parse(raw)
    assert result.bands[GearGroup.STR][BandNames.A].base_types == []


def test_parse_keeps_weapon_groups():
    raw = raw_config(
        bows={"A": {"base_types": ["Thicket Bow"]}},
        wands={"S": {"base_types": ["Imbued Wand"]}},
    )
    result = gear.parse(raw)
    assert set(result.bands) == {GearGroup.BOWS, GearGroup.WANDS}
    assert all(type(group) is GearGroup for group in result.bands)


def test_parse_keeps_weapon_band_base_types():
    result = gear.parse(raw_config())
    assert result.bands[GearGroup.BOWS][BandNames.A].base_types == ["Thicket Bow"]


def test_parse_rejects_unknown_weapon_group():
    raw = raw_config(bow={"A": {"base_types": []}})
    with pytest.raises(ValueError):
        gear.parse(raw)


def test_write_creates_file(tmp_path):
    gear.write_filter_data(gear.parse(raw_config()), tmp_path)
    assert (tmp_path / "gear.yaml").exists()


def test_write_round_trips(tmp_path):
    original = gear.parse(
        raw_config(
            str={"S": {"base_types": []}, "A": {"base_types": ["Astral Plate"]}},
            dex={"A": {"base_types": ["Syndicate's Garb"]}},
        )
    )
    gear.write_filter_data(original, tmp_path)
    assert gear.get_filter_data(tmp_path) == original
