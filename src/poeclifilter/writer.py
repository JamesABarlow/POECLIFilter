from dataclasses import asdict
from enum import Enum

import yaml


def _represent_enum(dumper: yaml.SafeDumper, data: Enum):
    return dumper.represent_data(data.value)


yaml.SafeDumper.add_multi_representer(Enum, _represent_enum)


def dump(string):
    return yaml.safe_dump(asdict(string), sort_keys=False, default_flow_style=None)
