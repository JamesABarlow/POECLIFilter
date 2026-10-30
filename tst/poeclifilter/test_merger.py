from unittest.mock import Mock

import pytest
from builders import (
    make_armour_band,
    make_armour_entry,
    make_armour_filter_data,
    make_armour_item_data,
    make_band,
    make_banded_item_class,
    make_banded_item_data_class,
    make_item_entry,
)

from poeclifilter import merger, resources
from poeclifilter.filters import AttributeGroup, BandNames, FilterRef, GameVersion
from poeclifilter.game import ArmourClass
from poeclifilter.merger import merge_armour, merge_banded_item_category

filter_ref = FilterRef(game_version=GameVersion.POE1, name="test")


def test_merge_filter_creates_new_filter(in_tmp_config_home, monkeypatch):
    mock_merge_banded_item_category = Mock()
    mock_merge_armour = Mock()
    monkeypatch.setattr(merger, "merge_banded_item_category", mock_merge_banded_item_category)
    monkeypatch.setattr(merger, "merge_armour", mock_merge_armour)
    resources.filter_dir(filter_ref).mkdir(parents=True)
    assert not (resources.filter_dir(filter_ref) / "currency.yaml").is_file()
    assert not (resources.filter_dir(filter_ref) / "armour.yaml").is_file()

    merger.merge_filter(filter_ref, False)

    mock_merge_banded_item_category.assert_called_once()
    mock_merge_armour.assert_called_once()
    assert (resources.filter_dir(filter_ref) / "currency.yaml").is_file()
    assert (resources.filter_dir(filter_ref) / "armour.yaml").is_file()


def test_merge_filter_update_not_implemented():
    with pytest.raises(NotImplementedError):
        merger.merge_filter(filter_ref, True)


def test_merge_banded_item_category_adds_missing_item_to_its_default_band():
    filter_items = make_banded_item_class({BandNames.A: make_band()})
    items_data = make_banded_item_data_class(
        categories={"base": {"Divine Orb": make_item_entry(band=BandNames.A)}}
    )

    merge_banded_item_category("currency", filter_items, items_data)

    assert filter_items.bands[BandNames.A].base_types == ["Divine Orb"]


def test_merge_banded_item_category_leaves_existing_item_alone():
    filter_items = make_banded_item_class(
        {
            BandNames.A: make_band(),
            BandNames.B: make_band(base_types=["Divine Orb"]),
        }
    )
    items_data = make_banded_item_data_class(
        categories={"base": {"Divine Orb": make_item_entry(band=BandNames.A)}}
    )

    merge_banded_item_category("currency", filter_items, items_data)

    assert filter_items.bands[BandNames.B].base_types == ["Divine Orb"]
    assert filter_items.bands[BandNames.A].base_types == []


def test_merge_banded_item_category_raises_when_band_missing_from_filter():
    filter_items = make_banded_item_class({})
    items_data = make_banded_item_data_class(
        categories={"base": {"Divine Orb": make_item_entry(band=BandNames.A)}}
    )

    with pytest.raises(ValueError, match="Band not found"):
        merge_banded_item_category("currency", filter_items, items_data)


def test_merge_banded_item_category_merges_across_multiple_categories():
    filter_items = make_banded_item_class({BandNames.A: make_band(), BandNames.S: make_band()})
    items_data = make_banded_item_data_class(
        categories={
            "base": {"Divine Orb": make_item_entry(band=BandNames.A)},
            "fossils": {"Hollow Fossil": make_item_entry(band=BandNames.S)},
        }
    )

    merge_banded_item_category("currency", filter_items, items_data)

    assert filter_items.bands[BandNames.A].base_types == ["Divine Orb"]
    assert filter_items.bands[BandNames.S].base_types == ["Hollow Fossil"]


def test_merge_armour_adds_missing_item_to_its_default_band():
    filter_data = make_armour_filter_data({AttributeGroup.STR: {BandNames.A: make_armour_band()}})
    item_data = make_armour_item_data(
        {
            AttributeGroup.STR: {
                ArmourClass.BODY_ARMOURS: {"Astral Plate": make_armour_entry(band=BandNames.A)}
            }
        }
    )

    merge_armour(filter_data, item_data)

    assert filter_data.armour_categories[AttributeGroup.STR][BandNames.A].base_types == [
        "Astral Plate"
    ]


def test_merge_armour_leaves_existing_item_alone():
    filter_data = make_armour_filter_data(
        {
            AttributeGroup.STR: {
                BandNames.A: make_armour_band(),
                BandNames.B: make_armour_band(base_types=["Astral Plate"]),
            }
        }
    )
    item_data = make_armour_item_data(
        {
            AttributeGroup.STR: {
                ArmourClass.BODY_ARMOURS: {"Astral Plate": make_armour_entry(band=BandNames.A)}
            }
        }
    )

    merge_armour(filter_data, item_data)

    assert filter_data.armour_categories[AttributeGroup.STR][BandNames.B].base_types == [
        "Astral Plate"
    ]
    assert filter_data.armour_categories[AttributeGroup.STR][BandNames.A].base_types == []


def test_merge_armour_raises_when_band_missing_from_filter():
    filter_data = make_armour_filter_data({AttributeGroup.STR: {}})
    item_data = make_armour_item_data(
        {
            AttributeGroup.STR: {
                ArmourClass.BODY_ARMOURS: {"Astral Plate": make_armour_entry(band=BandNames.A)}
            }
        }
    )

    with pytest.raises(ValueError, match="Band not found"):
        merge_armour(filter_data, item_data)


def test_merge_armour_merges_across_multiple_groups():
    filter_data = make_armour_filter_data(
        {
            AttributeGroup.STR: {BandNames.A: make_armour_band()},
            AttributeGroup.INT: {BandNames.S: make_armour_band()},
        }
    )
    item_data = make_armour_item_data(
        {
            AttributeGroup.STR: {
                ArmourClass.BODY_ARMOURS: {"Astral Plate": make_armour_entry(band=BandNames.A)}
            },
            AttributeGroup.INT: {
                ArmourClass.BODY_ARMOURS: {"Twilight Regalia": make_armour_entry(band=BandNames.S)}
            },
        }
    )

    merge_armour(filter_data, item_data)

    assert filter_data.armour_categories[AttributeGroup.STR][BandNames.A].base_types == [
        "Astral Plate"
    ]
    assert filter_data.armour_categories[AttributeGroup.INT][BandNames.S].base_types == [
        "Twilight Regalia"
    ]


def test_merge_armour_merges_every_armour_class_into_the_group_bands():
    filter_data = make_armour_filter_data({AttributeGroup.STR: {BandNames.A: make_armour_band()}})
    item_data = make_armour_item_data(
        {
            AttributeGroup.STR: {
                ArmourClass.HELMETS: {"Royal Burgonet": make_armour_entry(band=BandNames.A)},
                ArmourClass.BODY_ARMOURS: {"Astral Plate": make_armour_entry(band=BandNames.A)},
            }
        }
    )

    merge_armour(filter_data, item_data)

    assert filter_data.armour_categories[AttributeGroup.STR][BandNames.A].base_types == [
        "Royal Burgonet",
        "Astral Plate",
    ]
