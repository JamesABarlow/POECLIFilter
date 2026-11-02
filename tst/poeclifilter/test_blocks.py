import pytest
from builders import (
    make_band,
    make_color_map,
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
from poeclifilter.section_list import CURRENCY, GEAR


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


def make_mirror_filter_data(rules):
    return make_flat_bands_filter_data(
        bands={BandNames.S: make_band(base_types=["Mirror of Kalandra"])}, rules=rules
    )


def test_child_rule_block_comes_before_its_parents():
    filter_data = make_mirror_filter_data(
        [
            make_rule(
                id="parent",
                comment="parent",
                bands=[BandNames.S],
                rules=[make_rule(id="child", comment="child")],
            )
        ]
    )

    result = blocks.build_rule_blocks(filter_data, make_display_variables())

    assert [block.comment for block in result] == ["child", "parent"]


def test_child_rule_inherits_its_parents_conditions():
    filter_data = make_mirror_filter_data(
        [
            make_rule(
                bands=[BandNames.S],
                item_classes=[CurrencyClass.STACKABLE_CURRENCY],
                rarity=make_rarity_condition(),
                sockets=make_range(min=6),
                rules=[make_rule(comment="child", item_level=make_range(min=86))],
            )
        ]
    )

    result = blocks.build_rule_blocks(filter_data, make_display_variables())

    assert result[0] == blocks.Block(
        comment="child",
        hide=False,
        item_classes=[CurrencyClass.STACKABLE_CURRENCY],
        base_types=["Mirror of Kalandra"],
        rarity=make_rarity_condition(),
        sockets=make_range(min=6),
        item_level=make_range(min=86),
    )


def test_child_rule_condition_overrides_its_parents():
    filter_data = make_mirror_filter_data(
        [
            make_rule(
                bands=[BandNames.S],
                sockets=make_range(min=5),
                rules=[make_rule(sockets=make_range(min=6))],
            )
        ]
    )

    result = blocks.build_rule_blocks(filter_data, make_display_variables())

    assert result[0].sockets == make_range(min=6)
    assert result[1].sockets == make_range(min=5)


def test_child_rule_keeps_its_own_comment_and_hide():
    filter_data = make_mirror_filter_data(
        [
            make_rule(
                comment="parent",
                hide=True,
                bands=[BandNames.S],
                rules=[make_rule(comment="child", hide=False)],
            )
        ]
    )

    result = blocks.build_rule_blocks(filter_data, make_display_variables())

    assert (result[0].comment, result[0].hide) == ("child", False)
    assert (result[1].comment, result[1].hide) == ("parent", True)


def test_child_rule_with_unset_hide_is_shown_under_a_hidden_parent():
    # hide is not inherited (Appendix D)
    filter_data = make_mirror_filter_data(
        [make_rule(hide=True, bands=[BandNames.S], rules=[make_rule(hide=None)])]
    )

    result = blocks.build_rule_blocks(filter_data, make_display_variables())

    assert result[0].hide is False


def test_child_rule_display_merges_over_its_parents_field_by_field():
    filter_data = make_mirror_filter_data(
        [
            make_rule(
                bands=[BandNames.S],
                display=make_display(border_color="$purple", font_size="$normal"),
                rules=[make_rule(display=make_display(text_color="$purple", font_size=None))],
            )
        ]
    )

    result = blocks.build_rule_blocks(filter_data, make_display_variables())

    assert result[0].display == ResolvedDisplay(
        text_color="79 0 122 255", border_color="79 0 122 255", font_size="36"
    )


def test_child_rule_display_overrides_a_field_its_parent_sets():
    filter_data = make_mirror_filter_data(
        [
            make_rule(
                bands=[BandNames.S],
                display=make_display(background_color="$white", border_color="$purple"),
                rules=[make_rule(display=make_display(background_color="$purple"))],
            )
        ]
    )
    display_variables = make_display_variables(
        colors=make_color_map(
            background={"white": (237, 233, 222, 230), "purple": (79, 0, 122, 240)}
        )
    )

    result = blocks.build_rule_blocks(filter_data, display_variables)

    assert result[0].display == ResolvedDisplay(
        background_color="79 0 122 240", border_color="79 0 122 255"
    )


def test_child_rule_without_display_inherits_its_parents():
    filter_data = make_mirror_filter_data(
        [
            make_rule(
                bands=[BandNames.S],
                display="$loud",
                rules=[make_rule()],
            )
        ]
    )

    result = blocks.build_rule_blocks(filter_data, make_display_variables())

    assert (
        result[0].display
        == result[1].display
        == ResolvedDisplay(border_color="79 0 122 255", font_size="36")
    )


def test_grandchild_rule_inherits_from_the_merged_child():
    filter_data = make_mirror_filter_data(
        [
            make_rule(
                bands=[BandNames.S],
                rarity=make_rarity_condition(),
                rules=[
                    make_rule(
                        item_level=make_range(min=86),
                        rules=[make_rule(comment="grandchild", sockets=make_range(min=6))],
                    )
                ],
            )
        ]
    )

    result = blocks.build_rule_blocks(filter_data, make_display_variables())

    assert result[0].comment == "grandchild"
    assert result[0].base_types == ["Mirror of Kalandra"]
    assert result[0].rarity == make_rarity_condition()
    assert result[0].item_level == make_range(min=86)
    assert result[0].sockets == make_range(min=6)


def test_sibling_child_rules_keep_file_order():
    filter_data = make_mirror_filter_data(
        [
            make_rule(
                comment="parent",
                bands=[BandNames.S],
                rules=[make_rule(comment="first"), make_rule(comment="second")],
            )
        ]
    )

    result = blocks.build_rule_blocks(filter_data, make_display_variables())

    assert [block.comment for block in result] == ["first", "second", "parent"]


def test_excluded_rule_drops_its_children():
    filter_data = make_mirror_filter_data(
        [
            make_rule(
                include=False,
                bands=[BandNames.S],
                rules=[make_rule(comment="child")],
            )
        ]
    )

    result = blocks.build_rule_blocks(filter_data, make_display_variables())

    assert result == []


def test_excluded_child_rule_is_dropped_and_its_parent_kept():
    filter_data = make_mirror_filter_data(
        [
            make_rule(
                comment="parent",
                bands=[BandNames.S],
                rules=[make_rule(comment="child", include=False)],
            )
        ]
    )

    result = blocks.build_rule_blocks(filter_data, make_display_variables())

    assert [block.comment for block in result] == ["parent"]


def test_children_of_a_rule_with_empty_bands_produce_no_blocks():
    # A child only narrows, so it must not render with no BaseType (plan §5.1)
    filter_data = make_flat_bands_filter_data(
        bands={BandNames.C: make_band()},
        rules=[make_rule(bands=[BandNames.C], rules=[make_rule(comment="child")])],
    )

    result = blocks.build_rule_blocks(filter_data, make_display_variables())

    assert result == []


def make_two_band_filter_data(rules):
    return make_flat_bands_filter_data(
        bands={
            BandNames.S: make_band(base_types=["Mirror of Kalandra"]),
            BandNames.A: make_band(base_types=["Divine Orb", "Exalted Orb"]),
        },
        rules=rules,
    )


def test_child_rule_base_types_narrow_its_parents_bands():
    filter_data = make_two_band_filter_data(
        [
            make_rule(
                bands=[BandNames.S, BandNames.A],
                rules=[make_rule(base_types=["Divine Orb"])],
            )
        ]
    )

    result = blocks.build_rule_blocks(filter_data, make_display_variables())

    assert result[0].base_types == ["Divine Orb"]
    assert sorted(result[1].base_types or []) == [
        "Divine Orb",
        "Exalted Orb",
        "Mirror of Kalandra",
    ]


def test_child_rule_bands_narrow_its_parents_bands():
    filter_data = make_two_band_filter_data(
        [
            make_rule(
                bands=[BandNames.S, BandNames.A],
                rules=[make_rule(bands=[BandNames.S])],
            )
        ]
    )

    result = blocks.build_rule_blocks(filter_data, make_display_variables())

    assert result[0].base_types == ["Mirror of Kalandra"]


def test_child_rule_cannot_select_bases_outside_its_parents():
    filter_data = make_two_band_filter_data(
        [
            make_rule(
                bands=[BandNames.S],
                rules=[make_rule(base_types=["Mirror of Kalandra", "Divine Orb"])],
            )
        ]
    )

    result = blocks.build_rule_blocks(filter_data, make_display_variables())

    assert result[0].base_types == ["Mirror of Kalandra"]


def test_child_rule_with_no_overlap_with_its_parent_produces_no_block():
    # Would otherwise render with no BaseType and match every item (plan §5.1)
    filter_data = make_two_band_filter_data(
        [
            make_rule(
                comment="parent",
                bands=[BandNames.S],
                rules=[make_rule(comment="child", base_types=["Divine Orb"])],
            )
        ]
    )

    result = blocks.build_rule_blocks(filter_data, make_display_variables())

    assert [block.comment for block in result] == ["parent"]


def test_children_of_a_child_with_no_overlap_produce_no_blocks():
    filter_data = make_two_band_filter_data(
        [
            make_rule(
                comment="parent",
                bands=[BandNames.S],
                rules=[
                    make_rule(
                        base_types=["Divine Orb"],
                        rules=[make_rule(comment="grandchild")],
                    )
                ],
            )
        ]
    )

    result = blocks.build_rule_blocks(filter_data, make_display_variables())

    assert [block.comment for block in result] == ["parent"]


def test_child_rule_selection_applies_under_a_parent_without_one():
    filter_data = make_two_band_filter_data(
        [
            make_rule(
                sockets=make_range(min=6),
                rules=[make_rule(base_types=["Divine Orb"])],
            )
        ]
    )

    result = blocks.build_rule_blocks(filter_data, make_display_variables())

    assert result[0].base_types == ["Divine Orb"]
    assert result[1].base_types is None


def test_intersect_base_types_keeps_only_the_overlap():
    result = blocks.intersect_base_types(
        ["Divine Orb", "Exalted Orb"], ["Exalted Orb", "Chaos Orb"]
    )

    assert result == ["Exalted Orb"]


def test_intersect_base_types_without_overlap_is_empty():
    assert blocks.intersect_base_types(["Divine Orb"], ["Chaos Orb"]) == []


def test_intersect_base_types_without_child_selection_keeps_parents():
    assert blocks.intersect_base_types(["Divine Orb"], None) == ["Divine Orb"]


def test_intersect_base_types_without_parent_selection_uses_childs():
    assert blocks.intersect_base_types(None, ["Divine Orb"]) == ["Divine Orb"]


def test_intersect_base_types_without_either_selection_is_none():
    assert blocks.intersect_base_types(None, None) is None


def test_set_fields_keeps_set_fields_including_false_and_zero():
    block = blocks.Block(comment="", hide=False, sockets=make_range(min=0))

    result = blocks.set_fields(block)

    assert result == {"comment": "", "hide": False, "sockets": make_range(min=0)}


def test_set_fields_leaves_out_skipped_fields():
    block = blocks.Block(comment="kept", hide=False, rarity=make_rarity_condition())

    result = blocks.set_fields(block, skip={"rarity", "hide"})

    assert result == {"comment": "kept"}


def test_merge_display_without_child_display_keeps_parents():
    parent = ResolvedDisplay(font_size="36")

    assert blocks.merge_display(parent, None) == parent


def test_merge_display_without_parent_display_uses_childs():
    child = ResolvedDisplay(font_size="36")

    assert blocks.merge_display(None, child) == child


def test_merge_display_without_either_display_is_none():
    assert blocks.merge_display(None, None) is None


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


def test_rule_with_empty_named_display_has_no_display():
    currency_filter_data = make_flat_bands_filter_data(
        bands={BandNames.S: make_band(base_types=["Mirror of Kalandra"])},
        rules=[make_rule(hide=False, bands=[BandNames.S], display="$default")],
    )
    display_variables = make_display_variables(displays={"default": None})

    result = blocks.build_rule_blocks(currency_filter_data, display_variables)

    assert result[0].display is None


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


# These two use a list of just currency and gear, so every block is one or the other.
# The real list's order is checked in test_section_list.py.
def test_build_blocks_builds_sections_in_list_order(in_tmp_config_home, monkeypatch):
    monkeypatch.setattr(blocks, "SECTIONS", [CURRENCY, GEAR])

    result = build_test_filter_blocks()[:-1]

    currency_indexes = [i for i, block in enumerate(result) if is_currency_block(block)]
    gear_indexes = [i for i, block in enumerate(result) if not is_currency_block(block)]
    assert currency_indexes and gear_indexes
    assert max(currency_indexes) < min(gear_indexes)


def test_build_blocks_follows_a_reordered_list(in_tmp_config_home, monkeypatch):
    # Proves the order comes from the list, not from anything hard coded in build_blocks
    monkeypatch.setattr(blocks, "SECTIONS", [GEAR, CURRENCY])

    result = build_test_filter_blocks()[:-1]

    currency_indexes = [i for i, block in enumerate(result) if is_currency_block(block)]
    gear_indexes = [i for i, block in enumerate(result) if not is_currency_block(block)]
    assert max(gear_indexes) < min(currency_indexes)


def test_build_blocks_ends_with_the_catch_all(in_tmp_config_home):
    catch_all = build_test_filter_blocks()[-1]

    assert catch_all.hide is False
    assert not catch_all.item_classes
    assert not catch_all.base_types
