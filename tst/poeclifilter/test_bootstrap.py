import pytest

from poeclifilter import bootstrap
from poeclifilter.filters import FilterRef, GameVersion
from tst.poeclifilter.conftest import in_tmp_cwd

filter_ref = FilterRef(game_version=GameVersion.POE1, name="test")


def test_full_bootstrap_successful(in_tmp_cwd):
    bootstrap.bootstrap_new_filter(filter_ref)

    expected_path = in_tmp_cwd / "filters/poe1/test"
    assert expected_path.is_dir()
    assert list(expected_path.iterdir()) != []
    assert any(
        str(path).endswith("filters/poe1/test/display_variables.yaml")
        for path in list(expected_path.iterdir())
    )


def test_wipes_existing_filter_contents(in_tmp_cwd):
    stale_file = in_tmp_cwd / "filters/poe1/test/stale.yaml"
    stale_file.parent.mkdir(parents=True)
    stale_file.write_text("old")

    path = bootstrap.prepare_filter_dir(filter_ref)

    assert path.is_dir()
    assert list(path.iterdir()) == []


def test_path_not_dir(in_tmp_cwd):
    existing_file = in_tmp_cwd / "filters/poe1/test"
    existing_file.parent.mkdir(parents=True)
    existing_file.write_text("existing")

    with pytest.raises(ValueError, match="test exists and is not a directory"):
        bootstrap.prepare_filter_dir(filter_ref)


def test_pathname_unsafe(in_tmp_cwd):
    filter_ref = FilterRef(game_version=GameVersion.POE1, name="/test")
    with pytest.raises(ValueError, match="Invalid filter name"):
        bootstrap.prepare_filter_dir(filter_ref)


def test_resolve_guard_still_blocks_escape_if_name_check_bypassed(in_tmp_cwd, monkeypatch):
    monkeypatch.setattr(bootstrap, "is_valid_filter_name", lambda name: True)
    ref = FilterRef(game_version=GameVersion.POE1, name="..")

    with pytest.raises(ValueError, match="unsafe filter name"):
        bootstrap.prepare_filter_dir(ref)
