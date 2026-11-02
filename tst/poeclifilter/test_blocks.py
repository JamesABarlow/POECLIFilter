import pytest
from builders import (
    make_band,
    make_display,
    make_display_variables,
    make_flat_bands_filter_data,
    make_grouped_bands_filter_data,
    make_minimap_icon,
    make_play_effect,
    make_range,
    make_rarity_condition,
    make_rule,
)

from poeclifilter import blocks
from poeclifilter.blocks import ResolvedDisplay
from poeclifilter.filter_operations import bootstrap_new_filter
from poeclifilter.filters import BandNames, FilterRef, GameVersion, GearGroup
from poeclifilter.game import CurrencyClass, Operator, Rarity
from poeclifilter.models.rule import RarityCondition
from poeclifilter.section_list import SECTIONS


def test_gear_rule_carried_to_block():
    gear_filter_data = make_grouped_bands_filter_data(
        rules=[
            make_rule(
                hide=False,
                sockets=make_range(max=6),
                rarity=make_rarity_condition(Operator.EQUAL, Rarity.RARE),
            )
        ]
    )

    result = blocks.build_rule_blocks(gear_filter_data, make_display_variables())

    assert result[0].sockets == make_range(max=6)
    assert result[0].rarity == RarityCondition(Operator.EQUAL, Rarity.RARE)


def test_gear_rule_without_optionals():
    gear_filter_data = make_grouped_bands_filter_data(rules=[make_rule(hide=False)])

    result = blocks.build_rule_blocks(gear_filter_data, make_display_variables())

    assert result[0].sockets is None
    assert result[0].rarity is None


def test_gear_rule_with_bands_uses_the_bands_base_types():
    gear_filter_data = make_grouped_bands_filter_data(
        bands={GearGroup.STR: {BandNames.A: make_band(base_types=["Astral Plate"])}},
        rules=[make_rule(hide=False, bands={GearGroup.STR: [BandNames.A]})],
    )

    result = blocks.build_rule_blocks(gear_filter_data, make_display_variables())

    assert result[0].base_types == ["Astral Plate"]


def test_gear_rule_with_only_empty_bands_produces_no_block():
    gear_filter_data = make_grouped_bands_filter_data(
        bands={
            GearGroup.STR: {
                BandNames.A: make_band(base_types=["Astral Plate"]),
                BandNames.B: make_band(),
            }
        },
        rules=[
            make_rule(id="empty", hide=True, bands={GearGroup.STR: [BandNames.B]}),
            make_rule(id="filled", hide=False, bands={GearGroup.STR: [BandNames.A]}),
        ],
    )

    result = blocks.build_rule_blocks(gear_filter_data, make_display_variables())

    assert len(result) == 1
    assert result[0].base_types == ["Astral Plate"]


def test_gear_rule_with_unset_hide_is_shown():
    gear_filter_data = make_grouped_bands_filter_data(rules=[make_rule(hide=None)])

    result = blocks.build_rule_blocks(gear_filter_data, make_display_variables())

    assert result[0].hide is False


def test_gear_rule_with_hide_true_is_hidden():
    gear_filter_data = make_grouped_bands_filter_data(rules=[make_rule(hide=True)])

    result = blocks.build_rule_blocks(gear_filter_data, make_display_variables())

    assert result[0].hide is True


def test_gear_rule_with_bands_uses_armour_and_weapon_base_types():
    gear_filter_data = make_grouped_bands_filter_data(
        bands={
            GearGroup.STR: {BandNames.A: make_band(base_types=["Astral Plate"])},
            GearGroup.BOWS: {BandNames.A: make_band(base_types=["Thicket Bow"])},
        },
        rules=[
            make_rule(
                hide=False, bands={GearGroup.STR: [BandNames.A], GearGroup.BOWS: [BandNames.A]}
            )
        ],
    )

    result = blocks.build_rule_blocks(gear_filter_data, make_display_variables())

    assert result[0].base_types == ["Astral Plate", "Thicket Bow"]


def test_currency_rule_builds_block_with_resolved_display():
    currency_filter_data = make_flat_bands_filter_data(
        bands={BandNames.S: make_band(base_types=["Mirror of Kalandra"])},
        rules=[
            make_rule(
                comment="Currency band S",
                hide=False,
                bands=[BandNames.S],
                item_classes=[CurrencyClass.STACKABLE_CURRENCY],
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
        ],
    )

    result = blocks.build_rule_blocks(currency_filter_data, make_display_variables())

    assert result == [
        blocks.Block(
            comment="Currency band S",
            hide=False,
            item_classes=[CurrencyClass.STACKABLE_CURRENCY],
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


def test_rule_with_named_display_resolves_it():
    currency_filter_data = make_flat_bands_filter_data(
        bands={BandNames.S: make_band(base_types=["Mirror of Kalandra"])},
        rules=[make_rule(hide=False, bands=[BandNames.S], display="$loud")],
    )
    display_variables = make_display_variables(
        displays={"loud": make_display(border_color="$purple", font_size="$normal")}
    )

    result = blocks.build_rule_blocks(currency_filter_data, display_variables)

    assert result[0].display == ResolvedDisplay(border_color="79 0 122 255", font_size="36")


def test_rule_with_unknown_named_display_raises():
    currency_filter_data = make_flat_bands_filter_data(
        bands={BandNames.S: make_band(base_types=["Mirror of Kalandra"])},
        rules=[make_rule(hide=False, bands=[BandNames.S], display="$lowd")],
    )

    with pytest.raises(ValueError, match="Unknown display '\\$lowd'"):
        blocks.build_rule_blocks(currency_filter_data, make_display_variables(displays={}))


def test_currency_rule_without_display_has_no_display():
    currency_filter_data = make_flat_bands_filter_data(
        bands={BandNames.B: make_band(base_types=["Orb of Alteration"])},
        rules=[make_rule(hide=False, bands=[BandNames.B])],
    )

    result = blocks.build_rule_blocks(currency_filter_data, make_display_variables())

    assert result[0].display is None


def test_currency_rule_with_empty_band_produces_no_block():
    currency_filter_data = make_flat_bands_filter_data(
        bands={BandNames.C: make_band()},
        rules=[make_rule(hide=False, bands=[BandNames.C])],
    )

    result = blocks.build_rule_blocks(currency_filter_data, make_display_variables())

    assert result == []


def is_currency_block(block):
    return bool(block.item_classes) and all(
        isinstance(item_class, CurrencyClass) for item_class in block.item_classes
    )


def build_test_filter_blocks():
    filter_ref = FilterRef(game_version=GameVersion.POE1, name="test")
    bootstrap_new_filter(filter_ref)
    return blocks.build_blocks(filter_ref)


def test_build_blocks_builds_sections_in_list_order(in_tmp_config_home):
    result = build_test_filter_blocks()[:-1]

    currency_indexes = [i for i, block in enumerate(result) if is_currency_block(block)]
    gear_indexes = [i for i, block in enumerate(result) if not is_currency_block(block)]
    assert currency_indexes and gear_indexes
    assert max(currency_indexes) < min(gear_indexes)


def test_build_blocks_follows_a_reordered_list(in_tmp_config_home, monkeypatch):
    # Proves the order comes from the list, not from anything hard coded in build_blocks
    monkeypatch.setattr(blocks, "SECTIONS", list(reversed(SECTIONS)))

    result = build_test_filter_blocks()[:-1]

    currency_indexes = [i for i, block in enumerate(result) if is_currency_block(block)]
    gear_indexes = [i for i, block in enumerate(result) if not is_currency_block(block)]
    assert max(gear_indexes) < min(currency_indexes)


def test_build_blocks_ends_with_the_catch_all(in_tmp_config_home):
    catch_all = build_test_filter_blocks()[-1]

    assert catch_all.hide is False
    assert not catch_all.item_classes
    assert not catch_all.base_types
