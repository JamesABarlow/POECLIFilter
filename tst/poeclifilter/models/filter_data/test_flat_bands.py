import pytest
from builders import make_band, make_flat_bands_filter_data

from poeclifilter.filters import BandNames
from poeclifilter.models.filter_data import files, flat_bands


def raw_config(**bands):
    raw_bands = bands or {"S": {"base_types": ["Divine Orb"]}, "A": {"base_types": ["Chaos Orb"]}}
    rule = {"id": "test_id", "comment": "test_comment", "hide": False}
    return {"schema": 1, "bands": raw_bands, "rules": [rule]}


def test_parse_keeps_schema():
    result = flat_bands.parse(raw_config())
    assert result.schema == 1


def test_parse_converts_band_names_to_enum():
    result = flat_bands.parse(raw_config())
    assert set(result.bands) == {BandNames.S, BandNames.A}
    assert all(type(band_name) is BandNames for band_name in result.bands)


def test_parse_rejects_unknown_band_name():
    with pytest.raises(ValueError):
        flat_bands.parse(raw_config(Z={"base_types": []}))


def test_parse_keeps_band_base_types():
    result = flat_bands.parse(raw_config(S={"base_types": ["Divine Orb", "Mirror of Kalandra"]}))
    assert result.bands[BandNames.S].base_types == ["Divine Orb", "Mirror of Kalandra"]


def test_parse_band_without_base_types_is_empty():
    result = flat_bands.parse(raw_config(S={}))
    assert result.bands[BandNames.S].base_types == []


def test_parse_rule_bands_converts_to_enums():
    result = flat_bands.parse_rule_bands(["S", "A"])
    assert result == [BandNames.S, BandNames.A]
    assert all(type(band_name) is BandNames for band_name in result)


def test_parse_rule_bands_rejects_unknown_band():
    with pytest.raises(ValueError):
        flat_bands.parse_rule_bands(["Z"])


def test_parse_uses_currency_bands_for_rules():
    raw = raw_config()
    raw["rules"] = [{"id": "r", "comment": "c", "hide": False, "bands": ["S"]}]
    result = flat_bands.parse(raw)
    assert result.rules[0].bands == [BandNames.S]


def test_resolve_bands_returns_the_band_base_types():
    currency_filter_data = make_flat_bands_filter_data(
        bands={BandNames.S: make_band(base_types=["Divine Orb"])}
    )
    assert currency_filter_data.resolve_bands([BandNames.S]) == ["Divine Orb"]


def test_resolve_bands_joins_bands_in_rule_order():
    currency_filter_data = make_flat_bands_filter_data(
        bands={
            BandNames.S: make_band(base_types=["Divine Orb"]),
            BandNames.A: make_band(base_types=["Chaos Orb"]),
        }
    )
    result = currency_filter_data.resolve_bands([BandNames.A, BandNames.S])
    assert result == ["Chaos Orb", "Divine Orb"]


def test_resolve_bands_of_empty_band_is_empty():
    currency_filter_data = make_flat_bands_filter_data(bands={BandNames.B: make_band()})
    assert currency_filter_data.resolve_bands([BandNames.B]) == []


def test_write_round_trips_rule_bands(tmp_path):
    raw = raw_config()
    raw["rules"] = [
        {
            "id": "currency_s",
            "comment": "Currency band S",
            "hide": False,
            "bands": ["S"],
            "item_classes": ["Stackable Currency"],
            "display": {"font_size": "$normal"},
        }
    ]
    original = flat_bands.parse(raw)
    files.write_filter_data(original, tmp_path, "flat.yaml")
    reread = files.read_filter_data(tmp_path, "flat.yaml", flat_bands.parse)
    assert reread == original
    assert reread.rules[0].bands == [BandNames.S]
