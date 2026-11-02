# Convert the filter settings to ordered block list that can be used to write the filter

from collections.abc import Collection, Sequence
from dataclasses import dataclass, fields, replace

from poeclifilter.filters import FilterRef
from poeclifilter.models.display import Display
from poeclifilter.models.filter_data import display_variables, files
from poeclifilter.models.filter_data.display_variables import (
    Color,
    DisplayVariablesFilterData,
    SoundAlert,
)
from poeclifilter.models.filter_data.sections import SectionFilterData
from poeclifilter.models.rule import Range, RarityCondition, Rule
from poeclifilter.resources import filter_dir
from poeclifilter.section_list import SECTIONS


# TODO: Not sure if I like this design, can I get something better here
@dataclass(frozen=True)
class ResolvedDisplay:
    play_effect: str | None = None
    minimap_icon: str | None = None
    text_color: str | None = None
    background_color: str | None = None
    border_color: str | None = None
    font_size: str | None = None
    sound_alert: str | None = None


@dataclass(frozen=True)
class Block:
    comment: str
    hide: bool
    item_level: Range | None = None
    item_classes: Sequence[str] | None = None
    base_types: list[str] | None = None
    display: ResolvedDisplay | None = None
    sockets: Range | None = None
    stack_size: Range | None = None
    rarity: RarityCondition | None = None


def build_blocks(filter_ref: FilterRef):
    display_variables_filter_data = display_variables.get_filter_data(filter_dir(filter_ref))
    blocks = []
    for section in SECTIONS:
        section_filter_data = files.read_filter_data(
            filter_dir(filter_ref), section.file_name, section.parse
        )
        blocks.extend(build_rule_blocks(section_filter_data, display_variables_filter_data))

    # Add misc filter blocks including the final catch all here
    # TODO: This needs to be built better but here for now
    blocks.extend(
        [
            Block(
                comment="",
                hide=False,
                item_classes=None,
                base_types=None,
                display=ResolvedDisplay(background_color="237 233 222 230"),
            )
        ]
    )

    return blocks


def build_rule_blocks[BandsT](section_filter_data, display_variables):
    blocks = []
    for rule in section_filter_data.rules:
        blocks.extend(build_block_tree(rule, None, section_filter_data, display_variables))
    return blocks


def build_block_tree[BandsT](
    rule: Rule[BandsT],
    parent_block: Block | None,
    section_filter_data: SectionFilterData[BandsT],
    display_variables: DisplayVariablesFilterData,
):
    if not rule.include:
        return []

    block = build_rule_block(rule, section_filter_data, display_variables)
    if block is not None and parent_block is not None:
        block = merge_block(block, parent_block)
    if block is None:
        return []

    blocks = []
    for child in rule.rules or []:
        # Pass the merged block, so a grandchild narrows the child, not the top rule
        blocks.extend(build_block_tree(child, block, section_filter_data, display_variables))
    blocks.append(block)
    return blocks


def build_rule_block[BandsT](
    rule: Rule[BandsT],
    section_filter_data: SectionFilterData[BandsT],
    display_variables: DisplayVariablesFilterData,
):
    display = build_display(rule.display, display_variables)

    if rule.base_types:
        base_types = rule.base_types
    elif rule.bands:
        base_types = section_filter_data.resolve_bands(rule.bands)
        # Empty bands would render with no BaseType and match every item (plan §5.1)
        if not base_types:
            return
    else:
        base_types = None

    return Block(
        comment=rule.comment,
        hide=rule.hide is True,
        display=display,
        base_types=base_types,
        item_classes=rule.item_classes,
        sockets=rule.sockets,
        stack_size=rule.stack_size,
        rarity=rule.rarity,
        item_level=rule.item_level,
    )


def merge_block(child_block: Block, parent_block: Block):
    base_types = intersect_base_types(parent_block.base_types, child_block.base_types)
    # No overlap would render with no BaseType and match every item (plan §5.1)
    if base_types == []:
        return None

    return replace(
        parent_block,
        **set_fields(child_block, skip={"display", "base_types"}),
        base_types=base_types,
        display=merge_display(parent_block.display, child_block.display),
    )


# A child only narrows (Appendix D), so its selection is the overlap with its parent's.
# None means no selection, which is inherited, unlike an empty list
def intersect_base_types(parent: list[str] | None, child: list[str] | None):
    if parent is None:
        return child
    if child is None:
        return parent
    return [base_type for base_type in child if base_type in parent]


def set_fields(record, skip: Collection[str] = frozenset()):
    return {
        field.name: getattr(record, field.name)
        for field in fields(record)
        if field.name not in skip and getattr(record, field.name) is not None
    }


def merge_display(parent: ResolvedDisplay | None, child: ResolvedDisplay | None):
    if parent is None or child is None:
        return child or parent
    return replace(parent, **set_fields(child))


# Handle color substitions
def build_display(
    unresolved_display: Display | str | None, display_variables: DisplayVariablesFilterData
):
    if unresolved_display is None:
        return None

    if isinstance(unresolved_display, str):
        display_name = unresolved_display.removeprefix("$")
        if display_name not in display_variables.displays:
            raise ValueError(f"Unknown display {unresolved_display!r}")
        display = display_variables.displays[display_name]
        if not display:
            return None
    else:
        display = unresolved_display

    resolved_text_color = resolve_color(display.text_color, display_variables.colors.text)
    resolved_border_color = resolve_color(display.border_color, display_variables.colors.border)
    resolved_background_color = resolve_color(
        display.background_color, display_variables.colors.background
    )

    resolved_font_size = resolve_font_size(display.font_size, display_variables.font_size)
    resolved_sound_alert = resolve_sound_alert(display.sound_alert, display_variables.sound_alert)
    resolved_play_effect = None
    resolved_minimap_icon = None
    if display.play_effect:
        temp = " Temp" if display.play_effect.temp else ""
        resolved_play_effect = f"{display.play_effect.color}{temp}"
    if display.minimap_icon:
        resolved_minimap_icon = (
            f"{display.minimap_icon.size} {display.minimap_icon.color} {display.minimap_icon.shape}"
        )

    return ResolvedDisplay(
        play_effect=resolved_play_effect,
        minimap_icon=resolved_minimap_icon,
        text_color=resolved_text_color,
        background_color=resolved_background_color,
        border_color=resolved_border_color,
        font_size=resolved_font_size,
        sound_alert=resolved_sound_alert,
    )


def resolve_color(color_str: str | None, color_map: dict[str, Color]):
    if color_str and color_str.startswith("$"):
        color = color_str.removeprefix("$")
        # TODO: add warning if not found
        color_tuple = color_map.get(color)
        if color_tuple:
            return " ".join(str(c) for c in color_tuple)
        else:
            return None


def resolve_font_size(font_str: str | None, font_size_map: dict[str, int]):
    if font_str and font_str.startswith("$"):
        size = font_str.removeprefix("$")
        # TODO: add warning if not found
        return str(font_size_map.get(size))


def resolve_sound_alert(sound_str: str | None, sound_alert_map: dict[str, SoundAlert]):
    if sound_str and sound_str.startswith("$"):
        alert = sound_str.removeprefix("$")
        sound_alert = sound_alert_map.get(alert)
        # TODO: add warning if not found
        if sound_alert:
            return f"{sound_alert.id} {sound_alert.volume}"
        else:
            return None
