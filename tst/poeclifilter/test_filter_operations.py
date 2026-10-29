from unittest.mock import Mock

import pytest

from poeclifilter import filter_operations
from poeclifilter.filters import FilterRef, GameVersion
from tst.poeclifilter.conftest import in_tmp_config_home

filter_ref = FilterRef(game_version=GameVersion.POE1, name="test")


def test_full_bootstrap_successful(in_tmp_config_home):
    filter_operations.bootstrap_new_filter(filter_ref)

    expected_path = in_tmp_config_home / "poeclifilter/filters/poe1/test"
    assert expected_path.is_dir()
    assert list(expected_path.iterdir()) != []
    assert any(
        str(path).endswith("filters/poe1/test/display_variables.yaml")
        for path in list(expected_path.iterdir())
    )


def test_wipes_existing_filter_contents(in_tmp_config_home):
    stale_file = in_tmp_config_home / "poeclifilter/filters/poe1/test/stale.yaml"
    stale_file.parent.mkdir(parents=True)
    stale_file.write_text("old")

    path = filter_operations.prepare_filter_dir(filter_ref)

    assert path.is_dir()
    assert list(path.iterdir()) == []


def test_path_not_dir(in_tmp_config_home):
    existing_file = in_tmp_config_home / "poeclifilter/filters/poe1/test"
    existing_file.parent.mkdir(parents=True)
    existing_file.write_text("existing")

    with pytest.raises(ValueError, match="test exists and is not a directory"):
        filter_operations.prepare_filter_dir(filter_ref)


def test_pathname_unsafe(in_tmp_config_home):
    filter_ref = FilterRef(game_version=GameVersion.POE1, name="/test")
    with pytest.raises(ValueError, match="Invalid filter name"):
        filter_operations.prepare_filter_dir(filter_ref)


def test_resolve_guard_still_blocks_escape_if_name_check_bypassed(in_tmp_config_home, monkeypatch):
    monkeypatch.setattr(filter_operations,"is_valid_filter_name", lambda name: True)
    ref = FilterRef(game_version=GameVersion.POE1, name="..")

    with pytest.raises(ValueError, match="unsafe filter name"):
        filter_operations.prepare_filter_dir(ref)


def test_copy_files_writes_display_variables(tmp_path):
    filter_operations.copy_files(filter_ref, tmp_path)

    assert (tmp_path / "display_variables.yaml").exists()


def test_bootstrap_calls_merge_filter(in_tmp_config_home, monkeypatch):
    mock_merge_filter = Mock()
    monkeypatch.setattr(filter_operations,"merge_filter", mock_merge_filter)

    filter_operations.bootstrap_new_filter(filter_ref)

    mock_merge_filter.assert_called_once_with(filter_ref, False)
