from dataclasses import dataclass

import pytest

from poeclifilter.models.filter_data import files


@dataclass(frozen=True)
class Example:
    schema: int
    names: list[str]


def parse_example(raw):
    return Example(schema=raw["schema"], names=raw["names"])


def test_read_passes_loaded_yaml_to_parse(tmp_path):
    (tmp_path / "example.yaml").write_text("schema: 1\nnames: [a, b]\n")

    result = files.read_filter_data(tmp_path, "example.yaml", parse_example)

    assert result == Example(schema=1, names=["a", "b"])


def test_read_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        files.read_filter_data(tmp_path, "missing.yaml", parse_example)


def test_write_creates_named_file(tmp_path):
    files.write_filter_data(Example(schema=1, names=["a"]), tmp_path, "example.yaml")

    assert (tmp_path / "example.yaml").is_file()


def test_write_round_trips(tmp_path):
    original = Example(schema=1, names=["a", "b"])

    files.write_filter_data(original, tmp_path, "example.yaml")

    assert files.read_filter_data(tmp_path, "example.yaml", parse_example) == original
