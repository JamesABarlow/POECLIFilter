from typing import Protocol

from poeclifilter.models.rule import Rule


class SectionFilterData[BandsT](Protocol):
    @property
    def rules(self) -> list[Rule[BandsT]]: ...
    def resolve_bands(self, target_bands: BandsT) -> list[str]: ...
