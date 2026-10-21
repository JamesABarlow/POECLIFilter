import pytest
import yaml

from poeclifilter import loader


def test_parse_success():
    result = loader.parse("a:\n b: test\n")
    assert result == {"a": {"b": "test"}}


def test_duplicate_key_rejected():
    input = "a: \n dupe: first\n unique: test\n dupe: second \n"
    with pytest.raises(yaml.constructor.ConstructorError) as error:
        loader.parse(input)
    assert "dupe" in str(error.value)


def test_duplicate_key_seperate_mapping_success():
    input = "a: \n dupe: first\n unique: test\nb: \n dupe: second \n"
    result = loader.parse(input)
    assert result == {"a": {"dupe": "first", "unique": "test"}, "b": {"dupe": "second"}}


def test_non_mapping_node_raises_yaml_error():
    input = "!!map 'hello'"
    with pytest.raises(yaml.constructor.ConstructorError) as error:
        loader.parse(input)
    assert "expected a mapping node" in str(error.value)
