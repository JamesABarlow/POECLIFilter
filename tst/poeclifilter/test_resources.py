from pathlib import Path

import pytest

from poeclifilter import resources
from poeclifilter.filters import FilterRef, GameVersion


def test_base_config_dir():
    assert str(resources.base_config_dir(GameVersion.POE1)).endswith(
        "poeclifilter/poe1/base_filter_config"
    )


def test_item_data_dir():
    assert str(resources.item_data_dir(GameVersion.POE1)).endswith("poeclifilter/poe1/item_data")


def test_filters_root(in_tmp_config_home):
    assert resources.filters_root(GameVersion.POE1) == in_tmp_config_home / "poeclifilter/filters/poe1"


def test_filter_dir(in_tmp_config_home):
    filter_ref = FilterRef(game_version=GameVersion.POE1, name="test")
    assert resources.filter_dir(filter_ref) == in_tmp_config_home / "poeclifilter/filters/poe1/test"


# TODO: fix this test
# def list_filter_names():
#     assert resources.list_filter_names() == []


def test_game_filter_dir_poe1():
    expected = Path.home() / (
        ".steam/steam/steamapps/compatdata/238960/pfx/drive_c/users/steamuser"
        "/My Documents/My Games/Path of Exile"
    )
    assert resources.game_filter_dir(GameVersion.POE1) == expected


def test_game_filter_dir_unsupported():
    with pytest.raises(NotImplementedError):
        resources.game_filter_dir(GameVersion.POE2)


def test_built_filter_path():
    filter_ref = FilterRef(game_version=GameVersion.POE1, name="test")

    assert resources.built_filter_path(filter_ref) == resources.game_filter_dir(
        GameVersion.POE1
    ).joinpath("test.filter")
