from unittest.mock import Mock

import pytest

from poeclifilter import filter_operations, resources
from poeclifilter.filters import FilterRef, GameVersion
from poeclifilter.models.filter_data import flat_bands
from poeclifilter.models.filter_data.flat_bands import FlatBandsFilterData
from poeclifilter.section_list import SECTIONS, Section

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
    monkeypatch.setattr(filter_operations, "is_valid_filter_name", lambda name: True)
    ref = FilterRef(game_version=GameVersion.POE1, name="..")

    with pytest.raises(ValueError, match="unsafe filter name"):
        filter_operations.prepare_filter_dir(ref)


def test_copy_files_writes_display_variables(tmp_path):
    filter_operations.copy_files_for_new_filter(filter_ref, tmp_path)

    assert (tmp_path / "display_variables.yaml").exists()


def test_bootstrap_calls_merge_filter(in_tmp_config_home, monkeypatch):
    mock_merge_filter = Mock()
    monkeypatch.setattr(filter_operations, "merge_filter", mock_merge_filter)

    filter_operations.bootstrap_new_filter(filter_ref)

    mock_merge_filter.assert_called_once_with(filter_ref, False)


def test_delete_filter_removes_config_dir_and_built_filter(
    in_tmp_config_home, tmp_path, monkeypatch
):
    monkeypatch.setattr(
        filter_operations.resources, "game_filter_dir", lambda game_version: tmp_path
    )
    config_path = filter_operations.prepare_filter_dir(filter_ref)
    built_filter = tmp_path.joinpath("test.filter")
    built_filter.write_text("some filter text")

    filter_operations.delete_filter(filter_ref)

    assert not config_path.exists()
    assert not built_filter.exists()


def test_delete_filter_when_never_built(in_tmp_config_home, tmp_path, monkeypatch):
    monkeypatch.setattr(
        filter_operations.resources, "game_filter_dir", lambda game_version: tmp_path
    )
    config_path = filter_operations.prepare_filter_dir(filter_ref)

    filter_operations.delete_filter(filter_ref)

    assert not config_path.exists()


def test_merge_filter_writes_a_file_for_every_section(in_tmp_config_home):
    resources.filter_dir(filter_ref).mkdir(parents=True)

    filter_operations.merge_filter(filter_ref, False)

    for section in SECTIONS:
        assert (resources.filter_dir(filter_ref) / section.file_name).is_file()


def test_merge_filter_merges_each_section_with_its_parsed_data(in_tmp_config_home, monkeypatch):
    mock_merge = Mock()
    test_sections = [Section("currency", "currency.yaml", flat_bands.parse, mock_merge)]
    monkeypatch.setattr(filter_operations, "SECTIONS", test_sections)
    resources.filter_dir(filter_ref).mkdir(parents=True)

    filter_operations.merge_filter(filter_ref, False)

    mock_merge.assert_called_once()
    section_filter_data, item_data_dir = mock_merge.call_args.args
    assert isinstance(section_filter_data, FlatBandsFilterData)
    assert item_data_dir == resources.item_data_dir(filter_ref.game_version)


def test_merge_filter_writes_the_merged_data(in_tmp_config_home, monkeypatch):
    def add_merged_orb(section_filter_data, item_data_dir):
        section_filter_data.bands[next(iter(section_filter_data.bands))].base_types.append(
            "Merged Orb"
        )

    test_sections = [Section("currency", "currency.yaml", flat_bands.parse, add_merged_orb)]
    monkeypatch.setattr(filter_operations, "SECTIONS", test_sections)
    resources.filter_dir(filter_ref).mkdir(parents=True)

    filter_operations.merge_filter(filter_ref, False)

    written = (resources.filter_dir(filter_ref) / "currency.yaml").read_text()
    assert "Merged Orb" in written


def test_merge_filter_update_not_implemented():
    with pytest.raises(NotImplementedError):
        filter_operations.merge_filter(filter_ref, True)
