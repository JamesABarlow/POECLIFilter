from dataclasses import dataclass
from typing import Never

from poeclifilter.models import rule
from poeclifilter.models.rule import Rule


# For sections matched by game conditions alone, such as quest items by Class. Rule[Never]
# means a rule's bands can only be None.
@dataclass(frozen=True)
class NoBandsFilterData:
    schema: int
    rules: list[Rule[Never]]

    # Only here to satisfy SectionFilterData: no rule can have bands to resolve
    def resolve_bands(self, target_bands: Never) -> list[str]:
        raise TypeError("This section has no bands")


def parse(raw):
    rules = [rule.parse(rule_data, parse_rule_bands) for rule_data in raw["rules"]]

    return NoBandsFilterData(schema=raw["schema"], rules=rules)


# Dropping a stray bands key would leave a rule with no BaseType, matching every item (plan §5.1)
def parse_rule_bands(raw_rule_bands) -> Never:
    raise ValueError(f"This section has no bands, so a rule can't use bands {raw_rule_bands!r}")
