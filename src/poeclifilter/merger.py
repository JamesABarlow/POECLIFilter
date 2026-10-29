from collections.abc import Mapping
from typing import Protocol

from poeclifilter import resources
from poeclifilter.filters import BandNames, FilterRef
from poeclifilter.models.filter_data import armour as armour_filter_data_model
from poeclifilter.models.filter_data import banded_items
from poeclifilter.models.filter_data.armour import ArmourFilterData
from poeclifilter.models.filter_data.banded_items import BandedItemClass
from poeclifilter.models.item_data import armour as armour_item_data_model
from poeclifilter.models.item_data import banded
from poeclifilter.models.item_data.armour import ArmourItemData
from poeclifilter.models.item_data.banded import BandedItemDataClass


class HasBaseTypes(Protocol):
    @property
    def base_types(self) -> list[str]: ...


def merge_filter(filter_ref: FilterRef, is_filter_update: bool):

    # two similar operations here.
    # Copy all for new filter / reset to default - needs to load data from base
    # Checking if new items have been added since last update, pushing this back for now - needs to load data from filter
    #

    if not is_filter_update:
        # load files
        base_config_dir = resources.base_config_dir(filter_ref.game_version)
        item_config_dir = resources.item_data_dir(filter_ref.game_version)

        banded_items_filter_data = banded_items.get_filter_data(base_config_dir)
        banded_item_data = banded.get_item_data(item_config_dir)

        armour_filter_data = armour_filter_data_model.get_filter_data(base_config_dir)
        armour_item_data = armour_item_data_model.get_item_data(item_config_dir)
    else:
        raise NotImplementedError

    merge_banded_item_category(
        "currency", banded_items_filter_data.currency, banded_item_data.currency
    )

    merge_armour(armour_filter_data, armour_item_data)

    filter_dir = resources.filter_dir(filter_ref)
    banded_items.write_filter_data(banded_items_filter_data, filter_dir)
    armour_filter_data_model.write_filter_data(armour_filter_data, filter_dir)

    # Should also eventually be able to show what's changed in the filter over the default as a report
    return False


def merge_armour(filter_data: ArmourFilterData, armour_item_data: ArmourItemData):
    for armour_category_name, items in armour_item_data.categories.items():
        print(f"Merging armour - {armour_category_name}")
        for item_name, item_data in items.items():
            # check if exists

            exists_in_filter = check_item_exists_in_bands(
                item_name, filter_data.armour_categories[armour_category_name]
            )

            if not exists_in_filter:
                target_band = filter_data.armour_categories[armour_category_name].get(
                    item_data.band
                )
                if not target_band:
                    raise ValueError(f"Band not found {item_data.band}")
                else:
                    target_band.base_types.append(item_name)
            else:
                print(f"{item_name} already exists in filter can't handle this yet")

    return False


def merge_banded_item_category(
    category: str, filter_items: BandedItemClass, items_data: BandedItemDataClass
):
    for category_key, items in items_data.categories.items():
        print(f"Merging {category} - {category_key}")
        for item_name, item_data in items.items():
            print(f"Item name: {item_name} - {item_data}")
            exists_in_filter = check_item_exists_in_bands(item_name, filter_items.bands)

            if not exists_in_filter:
                band_name = BandNames(item_data.band)
                band = filter_items.bands.get(band_name)
                if not band:
                    raise ValueError(f"Band not found {band_name}")
                else:
                    band.base_types.append(item_name)
            else:
                # If not update this means item exists twice in item_data that should be fixed or read
                print(f"{item_name} already exists in filter can't handle this yet")


def check_item_exists_in_bands[K](item_name: str, bands: Mapping[K, HasBaseTypes]) -> bool:
    for band_name, band in bands.items():
        if item_name in band.base_types:
            print(f"Found {item_name} existing in filter band {band_name}")
            return True

    return False
