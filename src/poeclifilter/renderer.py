from poeclifilter import resources
from poeclifilter.blocks import Block, ResolvedDisplay
from poeclifilter.filters import FilterRef
from poeclifilter.models.rule import Range, RarityCondition


def write_to_filter(filter_ref: FilterRef, text: str):
    dest = resources.built_filter_path(filter_ref)
    dest.write_text(text)


def render_filter(filter_ref: FilterRef, blocks: list[Block]):

    sections = [render_block(block) for block in blocks]

    write_to_filter(filter_ref, "\n\n".join(sections))


# TODO: Work out what actual options can exist here
def render_block(block: Block):
    lines = ["Hide" if block.hide else "Show"]
    if block.item_classes:
        items_classes = " ".join(f'"{item_class}"' for item_class in sorted(block.item_classes))
        lines.append(f"  Class == {items_classes}")
    if block.base_types:
        base_types = " ".join(f'"{item}"' for item in sorted(block.base_types))
        lines.append(f"  BaseType == {base_types}")
    if block.sockets:
        lines.append(f"  Sockets {render_range(block.sockets)}")
    if block.rarity:
        lines.append(f"  Rarity {render_rarity(block.rarity)}")
    lines.extend(render_display(block.display))

    return "\n".join(lines)


def render_display(display: ResolvedDisplay | None):
    if not display:
        return []
    lines = []

    if display.play_effect:
        lines.append(f"  PlayEffect {display.play_effect}")
    if display.minimap_icon:
        lines.append(f"  MinimapIcon {display.minimap_icon}")
    if display.text_color:
        lines.append(f"  SetTextColor {get_color({}, display.text_color)}")
    if display.background_color:
        lines.append(f"  SetBackgroundColor {display.background_color}")
    if display.border_color:
        lines.append(f"  SetBorderColor {display.border_color}")
    if display.font_size:
        lines.append(f"  SetFontSize {display.font_size}")
    # TODO: sound alert type needs fixing
    if display.sound_alert:
        lines.append(f"  PlayAlertSound {display.sound_alert}")
    return lines


def get_color(display_variables, str):
    # handle $purple to rgb here
    return str


def render_range(range: Range | None):
    if not range:
        return None

    if range.min is not None:
        return f">= {str(range.min)}"
    elif range.max is not None:
        return f"<= {str(range.max)}"
    raise ValueError(f"Invalid range {range}")


def render_rarity(rarity_cond: RarityCondition):
    if not rarity_cond:
        return None

    return f"{rarity_cond.operator} {rarity_cond.rarity}"
