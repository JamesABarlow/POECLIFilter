from builders import (
    make_armour_filter_data,
    make_band,
    make_banded_items,
    make_display,
    make_display_variables,
    make_minimap_icon,
    make_play_effect,
    make_range,
    make_rule,
)

from poeclifilter import blocks
from poeclifilter.blocks import ResolvedDisplay
from poeclifilter.filters import BandNames


# TODO: Add correct full testing
def test_no_bands_produces_no_blocks():
    result = blocks.build_banded_items_blocks(make_banded_items(), make_display_variables())

    assert result == []


def test_band_without_display_has_no_display():
    banded_items = make_banded_items(
        {BandNames.S: make_band(base_types=["Mirror of Kalandra"], display=None)}
    )

    result = blocks.build_banded_items_blocks(banded_items, make_display_variables())

    assert result[0].display is None


def test_basic_banded_blocks():
    banded_items = make_banded_items(
        {
            BandNames.S: make_band(
                base_types=["Mirror of Kalandra"],
                display=make_display(
                    play_effect=make_play_effect(),
                    minimap_icon=make_minimap_icon(),
                    text_color="$purple",
                    background_color="$white",
                    border_color="$purple",
                    font_size="$normal",
                    sound_alert="$major",
                ),
            )
        }
    )

    result = blocks.build_banded_items_blocks(banded_items, make_display_variables())

    assert result == [
        blocks.Block(
            comment="",
            hide=False,
            item_classes=["Stackable Currency"],
            base_types=["Mirror of Kalandra"],
            display=ResolvedDisplay(
                play_effect="Purple",
                minimap_icon="1 Purple Circle",
                text_color="79 0 122 255",
                background_color="237 233 222 230",
                border_color="79 0 122 255",
                font_size="36",
                sound_alert="6 300",
            ),
        )
    ]


def test_armour_rule_sockets_carried_to_block():
    armour_filter_data = make_armour_filter_data(
        rules=[make_rule(hide=False, sockets=make_range(max=6))]
    )

    result = blocks.build_armour_blocks(armour_filter_data, make_display_variables())

    assert result[0].sockets == make_range(max=6)


def test_armour_rule_without_sockets_has_no_sockets():
    armour_filter_data = make_armour_filter_data(rules=[make_rule(hide=False)])

    result = blocks.build_armour_blocks(armour_filter_data, make_display_variables())

    assert result[0].sockets is None
