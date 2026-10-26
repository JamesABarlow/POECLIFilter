from builders import make_block, make_resolved_display

from poeclifilter import renderer


# TODO: Add correct full testing
def test_render_block_emits_every_display_line():
    block = make_block(
        base_type=["Mirror of Kalandra"],
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
