from dataclasses import asdict

import yaml

from poeclifilter.models.display_variables import DisplayVariables


def write(string: DisplayVariables):
    print(yaml.safe_dump(asdict(string), sort_keys=False, default_flow_style=None))
