from typing import Any, ClassVar, Protocol

from poeclifilter.models.rule import Rule


class SectionFilterData[BandsT](Protocol):
    # Every dataclass has this, so it promises the data is a dataclass that can be written
    __dataclass_fields__: ClassVar[dict[str, Any]]

    @property
    def rules(self) -> list[Rule[BandsT]]: ...
    def resolve_bands(self, target_bands: BandsT) -> list[str]: ...
