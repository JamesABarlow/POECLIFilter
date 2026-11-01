from dataclasses import replace

from builders import make_block, make_range, make_rarity_condition, make_resolved_display

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
        '  BaseType == "Mirror of Kalandra"\n'
        "  PlayEffect Purple\n"
        "  MinimapIcon 1 Purple Circle\n"
        "  SetTextColor 79 0 122 255\n"
        "  SetBackgroundColor 237 233 222 230\n"
        "  SetBorderColor 79 0 122 255\n"
        "  SetFontSize 36\n"
        "  PlayAlertSound 6 300"
    )


def test_render_block_without_display_emits_no_display_lines():
    # make_block treats display=None as "use the default", so set it afterwards
    block = replace(make_block(item_classes=None), display=None)

    result = renderer.render_block(block)

    assert result == "Show"


def test_render_block_with_empty_display_emits_no_display_lines():
    block = make_block(item_classes=None, display=make_resolved_display())

    result = renderer.render_block(block)

    assert result == "Show"


def test_render_block_emits_class_without_base_types():
    block = make_block(item_classes=["Helmets"])

    result = renderer.render_block(block)

    assert result == 'Show\n  Class == "Helmets"'


def test_render_block_sorts_item_classes():
    block = make_block(item_classes=["Helmets", "Body Armours"])

    result = renderer.render_block(block)

    assert result == 'Show\n  Class == "Body Armours" "Helmets"'


def test_render_block_emits_sockets_after_base_type():
    block = make_block(
        item_classes=None,
        base_types=["Astral Plate"],
        sockets=make_range(min=6),
    )

    result = renderer.render_block(block)

    assert result == 'Show\n  BaseType == "Astral Plate"\n  Sockets >= 6'


def test_render_block_without_sockets_emits_no_sockets_line():
    block = make_block(item_classes=None, sockets=None)

    result = renderer.render_block(block)

    assert "Sockets" not in result


def test_render_range_none_is_none():
    assert renderer.render_range(None) is None


def test_render_range_with_only_min():
    assert renderer.render_range(make_range(min=5)) == ">= 5"


def test_render_range_with_only_max():
    assert renderer.render_range(make_range(max=6)) == "<= 6"


def test_render_range_with_only_min_of_zero():
    assert renderer.render_range(make_range(min=0)) == ">= 0"


def test_render_with_rarity_condition():
    input_block = make_block(rarity=make_rarity_condition())
    assert renderer.render_block(input_block) == "Show\n  Rarity == Rare"


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
