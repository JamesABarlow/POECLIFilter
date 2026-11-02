import shutil
from pathlib import Path

from poeclifilter import resources
from poeclifilter.filters import FilterRef, is_valid_filter_name
from poeclifilter.models.filter_data import files
from poeclifilter.section_list import SECTIONS


def bootstrap_new_filter(filter_ref: FilterRef):
    new_filter_path = prepare_filter_dir(filter_ref)

    # Copy files over
    copy_files_for_new_filter(filter_ref, new_filter_path)

    # Write files with default item data
    merge_filter(filter_ref, False)
    return False


# TODO: slight difference on creating vs resetting. On create we need to care if it already exists and fail if so
def prepare_filter_dir(filter_ref: FilterRef) -> Path:
    path = _safe_filter_dir(filter_ref)

    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        raise ValueError(f"{path} exists and is not a directory")

    path.mkdir(parents=True)
    return path


def _safe_filter_dir(filter_ref: FilterRef) -> Path:
    if not is_valid_filter_name(filter_ref.name):
        raise ValueError(f"Invalid filter name: {filter_ref.name!r}")

    root = resources.filters_root(filter_ref.game_version).resolve()
    path = resources.filter_dir(filter_ref).resolve()
    if not is_safe_filter_path(root, path):
        # Regex above should make this impossible to reach but keeping it for safety
        raise ValueError(f"unsafe filter name: {filter_ref.name!r}")
    return path


def is_safe_filter_path(root: Path, path: Path) -> bool:
    return path != root and path.is_relative_to(root)


# TODO: Do this better. Handle other files that need to be copied
def copy_files_for_new_filter(filter_ref: FilterRef, dest: Path) -> None:
    src = resources.base_config_dir(filter_ref.game_version).joinpath("display_variables.yaml")
    dest.joinpath("display_variables.yaml").write_text(
        src.read_text(encoding="utf-8"), encoding="utf-8"
    )


def delete_filter(filter_ref: FilterRef) -> None:
    config_path = _safe_filter_dir(filter_ref)
    if config_path.is_dir():
        shutil.rmtree(config_path)

    resources.built_filter_path(filter_ref).unlink(missing_ok=True)


def merge_filter(filter_ref: FilterRef, is_filter_update: bool):
    # Two similar operations here.
    # Copy all for new filter / reset to default - needs to load data from base
    # Checking if new items have been added since last update, pushing this back for now - needs to load data from filter
    #
    if is_filter_update:
        raise NotImplementedError

    base_config_dir = resources.base_config_dir(filter_ref.game_version)
    item_data_dir = resources.item_data_dir(filter_ref.game_version)
    filter_dir = resources.filter_dir(filter_ref)

    # Should also eventually be able to show what's changed in the filter over the default as a report
    for section in SECTIONS:
        section_filter_data = files.read_filter_data(
            base_config_dir, section.file_name, section.parse
        )
        section.merge(section_filter_data, item_data_dir)
        files.write_filter_data(section_filter_data, filter_dir, section.file_name)
