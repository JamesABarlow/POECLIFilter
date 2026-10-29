from builders import make_block, make_resolved_display

from poeclifilter import renderer
from poeclifilter.filters import FilterRef, GameVersion

filter_ref = FilterRef(game_version=GameVersion.POE1, name="test")


# TODO: Add correct full testing
def test_render_block_emits_every_display_line():
    block = make_block(
        base_types=["Mirror of Kalandra"],
        display=make_resolved_display(
            play_effect="Purple",
            minimap_icon="1 Purple Circle",
            text_color="79 0 122 255",
            background_color="237 233 222 230",
            border_color="79 0 122 255",
            font_size="36",
            sound_alert="6 300",
        ),
    )

    result = renderer.render_block(block)

    assert result == (
        "Show\n"
        '  Class == "Stackable Currency"\n'
        '  BaseType == "Mirror of Kalandra"\n'
        "  PlayEffect Purple\n"
        "  MinimapIcon 1 Purple Circle\n"
        "  SetTextColor 79 0 122 255\n"
        "  SetBackgroundColor 237 233 222 230\n"
        "  SetBorderColor 79 0 122 255\n"
        "  SetFontSize 36\n"
        "  PlayAlertSound 6 300"
    )


def test_empty_display():
    block = make_block(display={})  # empty block

    result = renderer.render_block(block)

    assert result == ("Show")


def test_write_to_filter_writes_under_filter_name(tmp_path, monkeypatch):
    monkeypatch.setattr(renderer.resources, "game_filter_dir", lambda game_version: tmp_path)

    renderer.write_to_filter(filter_ref, "some text")

    assert (tmp_path / "test.filter").read_text() == "some text"


def test_render_filter_joins_blocks_with_blank_lines(tmp_path, monkeypatch):
    monkeypatch.setattr(renderer.resources, "game_filter_dir", lambda game_version: tmp_path)
    blocks = [make_block(base_types=["Mirror of Kalandra"]), make_block(hide=True)]

    renderer.render_filter(filter_ref, blocks)

    written = (tmp_path / "test.filter").read_text()
    assert written == "\n\n".join(renderer.render_block(b) for b in blocks)
