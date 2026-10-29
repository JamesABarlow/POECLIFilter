import pytest

from poeclifilter import resources
from poeclifilter.filters import AttributeGroup, GameVersion
from poeclifilter.models.filter_data import armour


def raw_config(**groups):
    raw_groups = groups or {"str": {"A": {"base_types": ["Astral Plate"]}}}
    return {"schema": 1, "armour": raw_groups}


def test_load_success():
    result = armour.get_armour(resources.base_config_dir(GameVersion.POE1))
    assert result.schema is not None
    assert result.armour is not None


def test_parse_keeps_schema():
    result = armour.parse(raw_config())
    assert result.schema == 1


def test_parse_keeps_attribute_groups():
    raw = raw_config(
        str={"A": {"base_types": ["Astral Plate"]}},
        str_int={"A": {"base_types": ["Sacred Chainmail"]}},
    )
    result = armour.parse(raw)
    assert set(result.armour) == {AttributeGroup.STR, AttributeGroup.STR_INT}


def test_parse_converts_group_to_enum():
    result = armour.parse(raw_config())
    assert all(type(group) is AttributeGroup for group in result.armour)


def test_parse_rejects_unknown_group():
    raw = raw_config(str_itn={"A": {"base_types": ["Sacred Chainmail"]}})
    with pytest.raises(ValueError):
        armour.parse(raw)


def test_parse_keeps_bands():
    raw = raw_config(str={"S": {"base_types": []}, "A": {"base_types": ["Astral Plate"]}})
    result = armour.parse(raw)
    assert set(result.armour[AttributeGroup.STR]) == {"S", "A"}


def test_parse_keeps_band_base_types():
    raw = raw_config(str={"A": {"base_types": ["Astral Plate", "Glorious Plate"]}})
    result = armour.parse(raw)
    assert result.armour[AttributeGroup.STR]["A"].base_types == ["Astral Plate", "Glorious Plate"]


def test_parse_band_without_base_types_is_empty():
    raw = raw_config(str={"A": {}})
    result = armour.parse(raw)
    assert result.armour[AttributeGroup.STR]["A"].base_types == []


def test_write_creates_file(tmp_path):
    armour.write_armour(armour.parse(raw_config()), tmp_path)
    assert (tmp_path / "armour.yaml").exists()


def test_write_round_trips(tmp_path):
    original = armour.parse(
        raw_config(
            str={"S": {"base_types": []}, "A": {"base_types": ["Astral Plate"]}},
            dex={"A": {"base_types": ["Syndicate's Garb"]}},
        )
    )
    armour.write_armour(original, tmp_path)
    assert armour.get_armour(tmp_path) == original
