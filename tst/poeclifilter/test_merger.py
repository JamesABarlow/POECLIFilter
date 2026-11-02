from unittest.mock import Mock

import pytest
from builders import (
    make_armour_entry,
    make_armour_item_data,
    make_band,
    make_currency_entry,
    make_currency_item_data,
    make_flat_bands_filter_data,
    make_grouped_bands_filter_data,
    make_weapon_entry,
    make_weapon_item_data,
)

from poeclifilter import merger, resources
from poeclifilter.filters import BandNames, FilterRef, GameVersion, GearGroup
from poeclifilter.game import ArmourClass
from poeclifilter.merger import merge_armour, merge_currency, merge_weapons

filter_ref = FilterRef(game_version=GameVersion.POE1, name="test")


def test_merge_filter_creates_new_filter(in_tmp_config_home, monkeypatch):
    mock_merge_currency = Mock()
    mock_merge_armour = Mock()
    mock_merge_weapons = Mock()
    monkeypatch.setattr(merger, "merge_currency", mock_merge_currency)
    monkeypatch.setattr(merger, "merge_armour", mock_merge_armour)
    monkeypatch.setattr(merger, "merge_weapons", mock_merge_weapons)
    resources.filter_dir(filter_ref).mkdir(parents=True)
    assert not (resources.filter_dir(filter_ref) / "currency.yaml").is_file()
    assert not (resources.filter_dir(filter_ref) / "gear.yaml").is_file()

    merger.merge_filter(filter_ref, False)

    mock_merge_currency.assert_called_once()
    mock_merge_armour.assert_called_once()
    mock_merge_weapons.assert_called_once()
    assert (resources.filter_dir(filter_ref) / "currency.yaml").is_file()
    assert (resources.filter_dir(filter_ref) / "gear.yaml").is_file()


def test_merge_filter_update_not_implemented():
    with pytest.raises(NotImplementedError):
        merger.merge_filter(filter_ref, True)


def test_merge_currency_adds_missing_item_to_its_default_band():
    filter_data = make_flat_bands_filter_data(bands={BandNames.A: make_band()})
    item_data = make_currency_item_data(
        {"base": {"Divine Orb": make_currency_entry(band=BandNames.A)}}
    )

    merge_currency(filter_data, item_data)

    assert filter_data.bands[BandNames.A].base_types == ["Divine Orb"]


def test_merge_currency_leaves_existing_item_alone():
    filter_data = make_flat_bands_filter_data(
        bands={
            BandNames.A: make_band(),
            BandNames.B: make_band(base_types=["Divine Orb"]),
        }
    )
    item_data = make_currency_item_data(
        {"base": {"Divine Orb": make_currency_entry(band=BandNames.A)}}
    )

    merge_currency(filter_data, item_data)

    assert filter_data.bands[BandNames.B].base_types == ["Divine Orb"]
    assert filter_data.bands[BandNames.A].base_types == []


def test_merge_currency_raises_when_band_missing_from_filter():
    filter_data = make_flat_bands_filter_data(bands={})
    item_data = make_currency_item_data(
        {"base": {"Divine Orb": make_currency_entry(band=BandNames.A)}}
    )

    with pytest.raises(ValueError, match="Band not found"):
        merge_currency(filter_data, item_data)


def test_merge_currency_merges_every_category_into_the_flat_bands():
    filter_data = make_flat_bands_filter_data(
        bands={BandNames.A: make_band(), BandNames.S: make_band()}
    )
    item_data = make_currency_item_data(
        {
            "base": {"Divine Orb": make_currency_entry(band=BandNames.S)},
            "fossils": {"Hollow Fossil": make_currency_entry(band=BandNames.S)},
        }
    )

    merge_currency(filter_data, item_data)

    assert filter_data.bands[BandNames.S].base_types == ["Divine Orb", "Hollow Fossil"]
    assert filter_data.bands[BandNames.A].base_types == []


def test_merge_currency_keeps_first_band_for_item_in_two_categories():
    filter_data = make_flat_bands_filter_data(
        bands={BandNames.S: make_band(), BandNames.B: make_band()}
    )
    item_data = make_currency_item_data(
        {
            "base": {"Divine Orb": make_currency_entry(band=BandNames.S)},
            "fossils": {"Divine Orb": make_currency_entry(band=BandNames.B)},
        }
    )

    merge_currency(filter_data, item_data)

    assert filter_data.bands[BandNames.S].base_types == ["Divine Orb"]
    assert filter_data.bands[BandNames.B].base_types == []


def test_merge_armour_adds_missing_item_to_its_default_band():
    filter_data = make_grouped_bands_filter_data({GearGroup.STR: {BandNames.A: make_band()}})
    item_data = make_armour_item_data(
        {
            GearGroup.STR: {
                ArmourClass.BODY_ARMOURS: {"Astral Plate": make_armour_entry(band=BandNames.A)}
            }
        }
    )

    merge_armour(filter_data, item_data)

    assert filter_data.bands[GearGroup.STR][BandNames.A].base_types == ["Astral Plate"]


def test_merge_armour_leaves_existing_item_alone():
    filter_data = make_grouped_bands_filter_data(
        {
            GearGroup.STR: {
                BandNames.A: make_band(),
                BandNames.B: make_band(base_types=["Astral Plate"]),
            }
        }
    )
    item_data = make_armour_item_data(
        {
            GearGroup.STR: {
                ArmourClass.BODY_ARMOURS: {"Astral Plate": make_armour_entry(band=BandNames.A)}
            }
        }
    )

    merge_armour(filter_data, item_data)

    assert filter_data.bands[GearGroup.STR][BandNames.B].base_types == ["Astral Plate"]
    assert filter_data.bands[GearGroup.STR][BandNames.A].base_types == []


def test_merge_armour_raises_when_band_missing_from_filter():
    filter_data = make_grouped_bands_filter_data({GearGroup.STR: {}})
    item_data = make_armour_item_data(
        {
            GearGroup.STR: {
                ArmourClass.BODY_ARMOURS: {"Astral Plate": make_armour_entry(band=BandNames.A)}
            }
        }
    )

    with pytest.raises(ValueError, match="Band not found"):
        merge_armour(filter_data, item_data)


def test_merge_armour_merges_across_multiple_groups():
    filter_data = make_grouped_bands_filter_data(
        {
            GearGroup.STR: {BandNames.A: make_band()},
            GearGroup.INT: {BandNames.S: make_band()},
        }
    )
    item_data = make_armour_item_data(
        {
            GearGroup.STR: {
                ArmourClass.BODY_ARMOURS: {"Astral Plate": make_armour_entry(band=BandNames.A)}
            },
            GearGroup.INT: {
                ArmourClass.BODY_ARMOURS: {"Twilight Regalia": make_armour_entry(band=BandNames.S)}
            },
        }
    )

    merge_armour(filter_data, item_data)

    assert filter_data.bands[GearGroup.STR][BandNames.A].base_types == ["Astral Plate"]
    assert filter_data.bands[GearGroup.INT][BandNames.S].base_types == ["Twilight Regalia"]


def test_merge_armour_merges_every_armour_class_into_the_group_bands():
    filter_data = make_grouped_bands_filter_data({GearGroup.STR: {BandNames.A: make_band()}})
    item_data = make_armour_item_data(
        {
            GearGroup.STR: {
                ArmourClass.HELMETS: {"Royal Burgonet": make_armour_entry(band=BandNames.A)},
                ArmourClass.BODY_ARMOURS: {"Astral Plate": make_armour_entry(band=BandNames.A)},
            }
        }
    )

    merge_armour(filter_data, item_data)

    assert filter_data.bands[GearGroup.STR][BandNames.A].base_types == [
        "Royal Burgonet",
        "Astral Plate",
    ]


def test_merge_weapons_adds_missing_item_to_its_default_band():
    filter_data = make_grouped_bands_filter_data(bands={GearGroup.BOWS: {BandNames.A: make_band()}})
    item_data = make_weapon_item_data(
        {GearGroup.BOWS: {"Thicket Bow": make_weapon_entry(band=BandNames.A)}}
    )

    merge_weapons(filter_data, item_data)

    assert filter_data.bands[GearGroup.BOWS][BandNames.A].base_types == ["Thicket Bow"]


def test_merge_weapons_leaves_existing_item_alone():
    filter_data = make_grouped_bands_filter_data(
        bands={
            GearGroup.BOWS: {
                BandNames.A: make_band(),
                BandNames.B: make_band(base_types=["Thicket Bow"]),
            }
        }
    )
    item_data = make_weapon_item_data(
        {GearGroup.BOWS: {"Thicket Bow": make_weapon_entry(band=BandNames.A)}}
    )

    merge_weapons(filter_data, item_data)

    assert filter_data.bands[GearGroup.BOWS][BandNames.B].base_types == ["Thicket Bow"]
    assert filter_data.bands[GearGroup.BOWS][BandNames.A].base_types == []


def test_merge_weapons_raises_when_band_missing_from_filter():
    filter_data = make_grouped_bands_filter_data(bands={GearGroup.BOWS: {}})
    item_data = make_weapon_item_data(
        {GearGroup.BOWS: {"Thicket Bow": make_weapon_entry(band=BandNames.A)}}
    )

    with pytest.raises(ValueError, match="Band not found"):
        merge_weapons(filter_data, item_data)


def test_merge_weapons_leaves_armour_bands_alone():
    filter_data = make_grouped_bands_filter_data(
        bands={
            GearGroup.STR: {BandNames.A: make_band()},
            GearGroup.BOWS: {BandNames.A: make_band()},
        },
    )
    item_data = make_weapon_item_data(
        {GearGroup.BOWS: {"Thicket Bow": make_weapon_entry(band=BandNames.A)}}
    )

    merge_weapons(filter_data, item_data)

    assert filter_data.bands[GearGroup.STR][BandNames.A].base_types == []
