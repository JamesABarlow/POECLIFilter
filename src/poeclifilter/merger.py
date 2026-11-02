from collections.abc import Mapping
from typing import Protocol

from poeclifilter import resources
from poeclifilter.filters import FilterRef
from poeclifilter.models.filter_data import currency as currency_filter_data_model
from poeclifilter.models.filter_data import files
from poeclifilter.models.filter_data import gear as gear_filter_data_model
from poeclifilter.models.filter_data.currency import CurrencyFilterData
from poeclifilter.models.filter_data.gear import GearFilterData
from poeclifilter.models.item_data import armour as armour_item_data_model
from poeclifilter.models.item_data import currency as currency_item_data_model
from poeclifilter.models.item_data import weapons as weapon_item_data_model
from poeclifilter.models.item_data.armour import ArmourItemData
from poeclifilter.models.item_data.currency import CurrencyItemData
from poeclifilter.models.item_data.weapons import WeaponItemData


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

        gear_filter_data = files.read_filter_data(
            base_config_dir, gear_filter_data_model.file_name, gear_filter_data_model.parse
        )
        currency_filter_data = files.read_filter_data(
            base_config_dir, currency_filter_data_model.file_name, currency_filter_data_model.parse
        )
        armour_item_data = armour_item_data_model.get_item_data(item_config_dir)
        weapon_item_data = weapon_item_data_model.get_item_data(item_config_dir)
        currency_item_data = currency_item_data_model.get_item_data(item_config_dir)
    else:
        raise NotImplementedError

    merge_armour(gear_filter_data, armour_item_data)
    merge_weapons(gear_filter_data, weapon_item_data)
    merge_currency(currency_filter_data, currency_item_data)

    filter_dir = resources.filter_dir(filter_ref)
    files.write_filter_data(gear_filter_data, filter_dir, gear_filter_data_model.file_name)
    files.write_filter_data(currency_filter_data, filter_dir, currency_filter_data_model.file_name)

    # Should also eventually be able to show what's changed in the filter over the default as a report
    return False


def merge_armour(filter_data: GearFilterData, armour_item_data: ArmourItemData):
    for armour_category_name, armour_classes in armour_item_data.categories.items():
        print(f"Merging armour - {armour_category_name}")
        # Filter data has no armour class level, so every class's bases merge into the group's bands
        for items in armour_classes.values():
            for item_name, item_data in items.items():
                # check if exists

                exists_in_filter = check_item_exists_in_bands(
                    item_name, filter_data.bands[armour_category_name]
                )

                if not exists_in_filter:
                    target_band = filter_data.bands[armour_category_name].get(item_data.band)
                    if not target_band:
                        raise ValueError(f"Band not found {item_data.band}")
                    else:
                        target_band.base_types.append(item_name)
                else:
                    print(f"{item_name} already exists in filter can't handle this yet")

    return False


def merge_weapons(filter_data: GearFilterData, weapon_item_data: WeaponItemData):
    for weapon_category_name, items in weapon_item_data.categories.items():
        print(f"Merging weapons - {weapon_category_name}")
        for item_name, item_data in items.items():
            exists_in_filter = check_item_exists_in_bands(
                item_name, filter_data.bands[weapon_category_name]
            )

            if not exists_in_filter:
                target_band = filter_data.bands[weapon_category_name].get(item_data.band)
                if not target_band:
                    raise ValueError(f"Band not found {item_data.band}")
                else:
                    target_band.base_types.append(item_name)
            else:
                print(f"{item_name} already exists in filter can't handle this yet")

    return False


def merge_currency(filter_items: CurrencyFilterData, currency_items_data: CurrencyItemData):
    for category_key, items in currency_items_data.categories.items():
        print(f"Merging currency - {category_key}")
        for item_name, item_data in items.items():
            print(f"Item name: {item_name} - {item_data}")
            exists_in_filter = check_item_exists_in_bands(item_name, filter_items.bands)

            if not exists_in_filter:
                band = filter_items.bands.get(item_data.band)
                if not band:
                    raise ValueError(f"Band not found {item_data.band}")
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
