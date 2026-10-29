from poeclifilter import resources
from poeclifilter.blocks import Block, ResolvedDisplay
from poeclifilter.filters import FilterRef


def write_to_filter(filter_ref: FilterRef, text: str):
    dest = resources.built_filter_path(filter_ref)
    dest.write_text(text)


def render_filter(filter_ref: FilterRef, blocks: list[Block]):

    sections = [render_block(block) for block in blocks]

    write_to_filter(filter_ref, "\n\n".join(sections))


# TODO: Work out what actual options can exist here
def render_block(block: Block):
    lines = ["Hide" if block.hide else "Show"]
    if block.base_type:
        if block.item_class:
            lines.append(f'  Class == "{block.item_class}"')
        base_types = " ".join(f'"{item}"' for item in sorted(block.base_type))
        lines.append(f"  BaseType == {base_types}")
        lines.extend(render_display(block.display))
    # Assume this is the catch all for now
    else:
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
