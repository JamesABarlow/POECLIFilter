from builders import (
    make_band,
    make_banded_items,
    make_display,
    make_display_variables,
    make_minimap_icon,
    make_play_effect,
)

from poeclifilter import blocks
from poeclifilter.blocks import ResolvedDisplay
from poeclifilter.filters import BandNames


# TODO: Add correct full testing
def test_no_bands_produces_no_blocks():
    result = blocks.build_banded_items_blocks(make_banded_items(), make_display_variables())

    assert result == []


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
            item_class="Stackable Currency",
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
