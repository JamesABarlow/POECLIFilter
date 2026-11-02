import pytest
from builders import make_gear_band, make_gear_filter_data

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


def test_write_round_trips_rule_bands(tmp_path):
    # Field names are the written YAML keys, so a rule field renamed away from the key the
    # parser reads would lose every rule's bands on write
    raw = raw_config()
    raw["rules"] = [
        {
            "id": "endgame_rares",
            "comment": "Rares shown in endgame",
            "hide": False,
            "bands": {"str": ["A"], "bows": ["A"]},
            "rarity": {"operator": "==", "rarity": "Rare"},
        }
    ]
    original = gear.parse(raw)
    gear.write_filter_data(original, tmp_path)
    reread = gear.get_filter_data(tmp_path)
    assert reread == original
    assert reread.rules[0].bands == {GearGroup.STR: [BandNames.A], GearGroup.BOWS: [BandNames.A]}


def test_resolve_bands_returns_the_bands_base_types():
    gear_filter_data = make_gear_filter_data(
        bands={GearGroup.STR: {BandNames.A: make_gear_band(base_types=["Astral Plate"])}}
    )
    assert gear_filter_data.resolve_bands({GearGroup.STR: [BandNames.A]}) == ["Astral Plate"]


def test_resolve_bands_joins_bands_across_groups_and_band_names():
    gear_filter_data = make_gear_filter_data(
        bands={
            GearGroup.STR: {
                BandNames.S: make_gear_band(base_types=["Glorious Plate"]),
                BandNames.A: make_gear_band(base_types=["Astral Plate"]),
            },
            GearGroup.BOWS: {BandNames.A: make_gear_band(base_types=["Thicket Bow"])},
        }
    )
    result = gear_filter_data.resolve_bands(
        {GearGroup.STR: [BandNames.A, BandNames.S], GearGroup.BOWS: [BandNames.A]}
    )
    assert result == ["Astral Plate", "Glorious Plate", "Thicket Bow"]


def test_resolve_bands_of_empty_band_is_empty():
    gear_filter_data = make_gear_filter_data(bands={GearGroup.STR: {BandNames.B: make_gear_band()}})
    assert gear_filter_data.resolve_bands({GearGroup.STR: [BandNames.B]}) == []


def test_parse_rule_bands_converts_to_enums():
    result = gear.parse_rule_bands({"str": ["A"], "str_int": ["B"]})
    assert result == {GearGroup.STR: [BandNames.A], GearGroup.STR_INT: [BandNames.B]}
    assert all(type(group) is GearGroup for group in result)
    assert all(type(band) is BandNames for bands in result.values() for band in bands)


def test_parse_rule_bands_accepts_weapon_and_armour_groups_together():
    result = gear.parse_rule_bands({"str": ["A"], "bows": ["S"]})
    assert result == {GearGroup.STR: [BandNames.A], GearGroup.BOWS: [BandNames.S]}


def test_parse_rule_bands_rejects_unknown_gear_group():
    with pytest.raises(ValueError):
        gear.parse_rule_bands({"str_itn": ["A"]})


def test_parse_rule_bands_rejects_unknown_band():
    with pytest.raises(ValueError):
        gear.parse_rule_bands({"str": ["Z"]})


def test_parse_uses_gear_bands_for_rules():
    raw = raw_config()
    raw["rules"] = [{"id": "r", "comment": "c", "hide": False, "bands": {"bows": ["A"]}}]
    result = gear.parse(raw)
    assert result.rules[0].bands == {GearGroup.BOWS: [BandNames.A]}
