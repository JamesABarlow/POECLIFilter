from dataclasses import asdict
from enum import Enum

import yaml


def _represent_enum(dumper: yaml.SafeDumper, data: Enum):
    return dumper.represent_data(data.value)


yaml.SafeDumper.add_multi_representer(Enum, _represent_enum)


# None means "not set", and every parser reads a missing key back as None, so
# writing it out would only add noise.
def _without_none(pairs):
    return {key: value for key, value in pairs if value is not None}


def dump(string):
    return yaml.safe_dump(
        asdict(string, dict_factory=_without_none), sort_keys=False, default_flow_style=None
    )
