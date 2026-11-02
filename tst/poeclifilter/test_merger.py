from unittest.mock import Mock

import pytest
from builders import (
    make_armour_entry,
    make_armour_item_data,
    make_band,
    make_card_entry,
    make_card_item_data,
    make_currency_entry,
    make_currency_item_data,
    make_flat_bands_filter_data,
    make_grouped_bands_filter_data,
    make_unique_entry,
    make_unique_item_data,
    make_weapon_entry,
    make_weapon_item_data,
)

from poeclifilter import merger, resources
from poeclifilter.filters import BandNames, GameVersion, GearGroup
from poeclifilter.game import ArmourClass
from poeclifilter.merger import (
    merge_armour,
    merge_cards,
    merge_currency,
    merge_uniques,
    merge_weapons,
)
from poeclifilter.models.item_data.armour import ArmourItemData
from poeclifilter.models.item_data.cards import CardItemData
from poeclifilter.models.item_data.currency import CurrencyItemData
from poeclifilter.models.item_data.uniques import UniqueItemData
from poeclifilter.models.item_data.weapons import WeaponItemData


def test_merge_currency_section_merges_currency_item_data(monkeypatch):
    mock_merge_currency = Mock()
    monkeypatch.setattr(merger, "merge_currency", mock_merge_currency)
    filter_data = make_flat_bands_filter_data()

    merger.merge_currency_section(filter_data, resources.item_data_dir(GameVersion.POE1))

    mock_merge_currency.assert_called_once()
    called_filter_data, called_item_data = mock_merge_currency.call_args.args
    assert called_filter_data is filter_data
    assert isinstance(called_item_data, CurrencyItemData)


def test_merge_gear_section_merges_armour_and_weapon_item_data(monkeypatch):
    mock_merge_armour = Mock()
    mock_merge_weapons = Mock()
    monkeypatch.setattr(merger, "merge_armour", mock_merge_armour)
    monkeypatch.setattr(merger, "merge_weapons", mock_merge_weapons)
    filter_data = make_grouped_bands_filter_data()

    merger.merge_gear_section(filter_data, resources.item_data_dir(GameVersion.POE1))

    armour_filter_data, armour_item_data = mock_merge_armour.call_args.args
    weapons_filter_data, weapon_item_data = mock_merge_weapons.call_args.args
    assert armour_filter_data is filter_data
    assert weapons_filter_data is filter_data
    assert isinstance(armour_item_data, ArmourItemData)
    assert isinstance(weapon_item_data, WeaponItemData)


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


def test_merge_unique_section_merges_unique_item_data(monkeypatch):
    mock_merge_uniques = Mock()
    monkeypatch.setattr(merger, "merge_uniques", mock_merge_uniques)
    filter_data = make_flat_bands_filter_data()

    merger.merge_unique_section(filter_data, resources.item_data_dir(GameVersion.POE1))

    mock_merge_uniques.assert_called_once()
    called_filter_data, called_item_data = mock_merge_uniques.call_args.args
    assert called_filter_data is filter_data
    assert isinstance(called_item_data, UniqueItemData)


def test_merge_uniques_adds_missing_item_to_its_default_band():
    filter_data = make_flat_bands_filter_data(bands={BandNames.S: make_band()})
    item_data = make_unique_item_data(
        {"belts": {"Leather Belt": make_unique_entry(band=BandNames.S)}}
    )

    merge_uniques(filter_data, item_data)

    assert filter_data.bands[BandNames.S].base_types == ["Leather Belt"]


def test_merge_uniques_leaves_existing_item_alone():
    filter_data = make_flat_bands_filter_data(
        bands={
            BandNames.S: make_band(),
            BandNames.B: make_band(base_types=["Leather Belt"]),
        }
    )
    item_data = make_unique_item_data(
        {"belts": {"Leather Belt": make_unique_entry(band=BandNames.S)}}
    )

    merge_uniques(filter_data, item_data)

    assert filter_data.bands[BandNames.B].base_types == ["Leather Belt"]
    assert filter_data.bands[BandNames.S].base_types == []


def test_merge_uniques_raises_when_band_missing_from_filter():
    filter_data = make_flat_bands_filter_data(bands={})
    item_data = make_unique_item_data(
        {"belts": {"Leather Belt": make_unique_entry(band=BandNames.S)}}
    )

    with pytest.raises(ValueError, match="Band not found"):
        merge_uniques(filter_data, item_data)


def test_merge_uniques_merges_every_category_into_the_flat_bands():
    filter_data = make_flat_bands_filter_data(
        bands={BandNames.S: make_band(), BandNames.A: make_band()}
    )
    item_data = make_unique_item_data(
        {
            "belts": {"Leather Belt": make_unique_entry(band=BandNames.S)},
            "body_armours": {"Glorious Plate": make_unique_entry(band=BandNames.S)},
        }
    )

    merge_uniques(filter_data, item_data)

    assert filter_data.bands[BandNames.S].base_types == ["Leather Belt", "Glorious Plate"]
    assert filter_data.bands[BandNames.A].base_types == []


def test_merge_uniques_merges_base_only_never_unique_names():
    # A filter can only match the base (plan §5.5), so unique names must not reach the bands
    filter_data = make_flat_bands_filter_data(bands={BandNames.S: make_band()})
    item_data = make_unique_item_data(
        {
            "belts": {
                "Leather Belt": make_unique_entry(
                    band=BandNames.S, uniques=["Headhunter", "Wurm's Molt"]
                )
            }
        }
    )

    merge_uniques(filter_data, item_data)

    assert filter_data.bands[BandNames.S].base_types == ["Leather Belt"]


def test_merge_cards_section_merges_card_item_data(monkeypatch):
    mock_merge_cards = Mock()
    monkeypatch.setattr(merger, "merge_cards", mock_merge_cards)
    filter_data = make_flat_bands_filter_data()

    merger.merge_cards_section(filter_data, resources.item_data_dir(GameVersion.POE1))

    mock_merge_cards.assert_called_once()
    called_filter_data, called_item_data = mock_merge_cards.call_args.args
    assert called_filter_data is filter_data
    assert isinstance(called_item_data, CardItemData)


def test_merge_cards_adds_missing_item_to_its_default_band():
    filter_data = make_flat_bands_filter_data(bands={BandNames.S: make_band()})
    item_data = make_card_item_data({"uniques": {"The Doctor": make_card_entry(band=BandNames.S)}})

    merge_cards(filter_data, item_data)

    assert filter_data.bands[BandNames.S].base_types == ["The Doctor"]


def test_merge_cards_leaves_existing_item_alone():
    filter_data = make_flat_bands_filter_data(
        bands={
            BandNames.S: make_band(),
            BandNames.B: make_band(base_types=["The Doctor"]),
        }
    )
    item_data = make_card_item_data({"uniques": {"The Doctor": make_card_entry(band=BandNames.S)}})

    merge_cards(filter_data, item_data)

    assert filter_data.bands[BandNames.B].base_types == ["The Doctor"]
    assert filter_data.bands[BandNames.S].base_types == []


def test_merge_cards_raises_when_band_missing_from_filter():
    filter_data = make_flat_bands_filter_data(bands={})
    item_data = make_card_item_data({"uniques": {"The Doctor": make_card_entry(band=BandNames.S)}})

    with pytest.raises(ValueError, match="Band not found"):
        merge_cards(filter_data, item_data)


def test_merge_cards_merges_every_category_into_the_flat_bands():
    filter_data = make_flat_bands_filter_data(
        bands={BandNames.S: make_band(), BandNames.A: make_band()}
    )
    item_data = make_card_item_data(
        {
            "currency": {"House of Mirrors": make_card_entry(band=BandNames.S)},
            "uniques": {"The Doctor": make_card_entry(band=BandNames.S)},
        }
    )

    merge_cards(filter_data, item_data)

    assert filter_data.bands[BandNames.S].base_types == ["House of Mirrors", "The Doctor"]
    assert filter_data.bands[BandNames.A].base_types == []


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
