import pytest

from poeclifilter.filters import is_valid_filter_name


@pytest.mark.parametrize("name", ["test", "MyFilter", "a"])
def test_valid_names_accepted(name):
    assert is_valid_filter_name(name)


@pytest.mark.parametrize(
    "name",
    ["", ".", "..", "/", "/etc", "has space", "with-hyphen", "under_score", "123", "café"],
)
def test_invalid_names_rejected(name):
    assert not is_valid_filter_name(name)
