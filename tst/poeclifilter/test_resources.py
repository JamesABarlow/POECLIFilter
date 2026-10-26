from pathlib import PosixPath

from poeclifilter import resources


def test_base_config_dir():
    assert resources.base_config_dir("poe1").endswith(
        "poeclifilter/poe1/base_filter_config"
    )


def test_item_data_dir():
    assert resources.item_data_dir("poe1").endswith("poeclifilter/poe1/item_data")


def test_filters_root():
    assert resources.filters_root() == PosixPath("filters")


def test_filter_dir():
    assert resources.filter_dir("testDir") == PosixPath("filters/testDir")


# TODO: fix this test
# def list_filter_names():
#     assert resources.list_filter_names() == []
