from typing import get_args

from poeclifilter.game import ItemClass


def test_item_class_values_are_unique_across_enums():
    # parse_item_class returns the first enum that accepts a value, so a value in two enums
    # would silently always parse as the first
    values = [member.value for enum in get_args(ItemClass.__value__) for member in enum]
    assert len(values) == len(set(values))
