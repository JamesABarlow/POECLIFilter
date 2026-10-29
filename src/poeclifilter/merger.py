from poeclifilter import resources
from poeclifilter.filters import BandNames, FilterRef
from poeclifilter.models.filter_data import banded_items
from poeclifilter.models.filter_data.banded_items import BandedItemClass
from poeclifilter.models.item_data import banded
from poeclifilter.models.item_data.banded import BandedItemDataClass


def merge_filter(filter_ref: FilterRef, is_filter_update: bool):

    # two similar operations here.
    # Copy all for new filter / reset to default - needs to load data from base
    # Checking if new items have been added since last update, pushing this back for now - needs to load data from filter
    #

    if not is_filter_update:
        # load files
        banded_items_filter_data = banded_items.get_filter_data(
            resources.base_config_dir(filter_ref.game_version)
        )
        banded_item_data = banded.get_item_data(resources.item_data_dir(filter_ref.game_version))
    else:
        raise NotImplementedError

    merge_category("currency", banded_items_filter_data.currency, banded_item_data.currency)

    banded_items.write_filter_data(banded_items_filter_data, resources.filter_dir(filter_ref))

    # Should also eventually be able to show what's changed in the filter over the default as a report
    return False


def merge_category(category: str, filter_items: BandedItemClass, items_data: BandedItemDataClass):
    for category_key, items in items_data.base_types.items():
        print(f"Merging {category_key}")
        for item_name, item_data in items.items():
            print(f"Item name: {item_name} - {item_data}")
            exists_in_filter = check_item_exists_in_filter(item_name, filter_items)

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


def check_item_exists_in_filter(item_name: str, filter_items: BandedItemClass):
    for band_name, band in filter_items.bands.items():
        if item_name in band.base_types:
            print(f"Found {item_name} existing in filter band {band_name}")
            return True

    return False
