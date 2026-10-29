from unittest.mock import Mock

import pytest
from builders import (
    make_band,
    make_banded_item_class,
    make_banded_item_data_class,
    make_item_entry,
)

from poeclifilter import merger, resources
from poeclifilter.filters import BandNames, FilterRef, GameVersion
from poeclifilter.merger import merge_category
from tst.poeclifilter.conftest import in_tmp_config_home

filter_ref = FilterRef(game_version=GameVersion.POE1, name="test")


def test_merge_filter_creates_new_filter(in_tmp_config_home, monkeypatch):
    mock_merge_category = Mock()
    monkeypatch.setattr(merger, "merge_category", mock_merge_category)
    resources.filter_dir(filter_ref).mkdir(parents=True)
    assert not (resources.filter_dir(filter_ref) / "currency.yaml").is_file()

    merger.merge_filter(filter_ref, False)

    mock_merge_category.assert_called_once()
    assert (resources.filter_dir(filter_ref) / "currency.yaml").is_file()


def test_merge_filter_update_not_implemented():
    with pytest.raises(NotImplementedError):
        merger.merge_filter(filter_ref, True)


def test_merge_category_adds_missing_item_to_its_default_band():
    filter_items = make_banded_item_class({BandNames.A: make_band()})
    items_data = make_banded_item_data_class(
        base_types={"base": {"Divine Orb": make_item_entry(band="A")}}
    )

    merge_category("currency", filter_items, items_data)

    assert filter_items.bands[BandNames.A].base_types == ["Divine Orb"]


def test_merge_category_leaves_existing_item_alone():
    filter_items = make_banded_item_class(
        {
            BandNames.A: make_band(),
            BandNames.B: make_band(base_types=["Divine Orb"]),
        }
    )
    items_data = make_banded_item_data_class(
        base_types={"base": {"Divine Orb": make_item_entry(band="A")}}
    )

    merge_category("currency", filter_items, items_data)

    assert filter_items.bands[BandNames.B].base_types == ["Divine Orb"]
    assert filter_items.bands[BandNames.A].base_types == []


def test_merge_category_raises_when_band_missing_from_filter():
    filter_items = make_banded_item_class({})
    items_data = make_banded_item_data_class(
        base_types={"base": {"Divine Orb": make_item_entry(band="A")}}
    )

    with pytest.raises(ValueError, match="Band not found"):
        merge_category("currency", filter_items, items_data)


def test_merge_category_merges_across_multiple_categories():
    filter_items = make_banded_item_class({BandNames.A: make_band(), BandNames.S: make_band()})
    items_data = make_banded_item_data_class(
        base_types={
            "base": {"Divine Orb": make_item_entry(band="A")},
            "fossils": {"Hollow Fossil": make_item_entry(band="S")},
        }
    )

    merge_category("currency", filter_items, items_data)

    assert filter_items.bands[BandNames.A].base_types == ["Divine Orb"]
    assert filter_items.bands[BandNames.S].base_types == ["Hollow Fossil"]
