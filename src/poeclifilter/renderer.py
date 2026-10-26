from pathlib import Path

from poeclifilter.blocks import Block
from poeclifilter.models.display import Display, PlayEffect, ResolvedDisplay

FILTER_DIR = Path(
    "~/.steam/steam/steamapps/compatdata/238960/pfx/drive_c/users/steamuser"
).expanduser()


def write_to_filter(text: str):
    Path("poeclifilter.filter").write_text(text)


# TODO: This needs to be written to a file
def render_filter(blocks: list[Block]):

    sections = [render_block(block) for block in blocks]
    sections.append(f"Show\n  SetBackgroundColor  237 233 222 230")

    write_to_filter("\n\n".join(sections))


def render_block(block: Block):
    lines = ["Hide" if block.hide else "Show"]
    if block.base_type:
        base_type = " ".join(f'"{item}"' for item in sorted(block.base_type))
        lines.append(f"  BaseType == {base_type}")
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
