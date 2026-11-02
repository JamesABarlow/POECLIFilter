import pytest

from poeclifilter import resources
from poeclifilter.filters import GameVersion
from poeclifilter.models.filter_data import files
from poeclifilter.section_list import SECTIONS


def test_sections_are_in_filter_order():
    # Section order is load-bearing (plan §7.1): the game uses the first block an item matches,
    # so uniques must come before gear or a unique armour or weapon gets gear's display
    assert [section.name for section in SECTIONS] == [
        "miscellaneous",
        "currency",
        "uniques",
        "cards",
        "gear",
        "jewellery",
    ]


def test_section_names_are_unique():
    names = [section.name for section in SECTIONS]
    assert len(names) == len(set(names))


def test_section_file_names_are_unique():
    file_names = [section.file_name for section in SECTIONS]
    assert len(file_names) == len(set(file_names))


@pytest.mark.parametrize("section", SECTIONS, ids=lambda section: section.name)
def test_section_base_config_parses(section):
    section_filter_data = files.read_filter_data(
        resources.base_config_dir(GameVersion.POE1), section.file_name, section.parse
    )
    assert section_filter_data.schema is not None
    assert section_filter_data.rules


@pytest.mark.parametrize("section", SECTIONS, ids=lambda section: section.name)
def test_section_base_config_round_trips(section, tmp_path):
    original = files.read_filter_data(
        resources.base_config_dir(GameVersion.POE1), section.file_name, section.parse
    )
    files.write_filter_data(original, tmp_path, section.file_name)
    assert files.read_filter_data(tmp_path, section.file_name, section.parse) == original
