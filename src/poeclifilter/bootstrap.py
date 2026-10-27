import shutil
from pathlib import Path

from poeclifilter import resources
from poeclifilter.filters import FilterRef, is_valid_filter_name
from poeclifilter.writer import write


def bootstrap_new_filter(filter_ref: FilterRef):
    new_filter_path = prepare_filter_dir(filter_ref)

    # Copy files over
    copy_files(filter_ref, new_filter_path)

    # Write files with default item data
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
    if path == root or not path.is_relative_to(root):
        # Regex above should make this impossible to reach but keeping it for safety
        raise ValueError(f"unsafe filter name: {filter_ref.name!r}")
    return path


# TODO: Do this better. Handle other files that need to be copied
def copy_files(filter_ref: FilterRef, dest: Path) -> None:
    src = Path(resources.base_config_dir(filter_ref.game_version)) / "display_variables.yaml"
    (dest / "display_variables.yaml").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
