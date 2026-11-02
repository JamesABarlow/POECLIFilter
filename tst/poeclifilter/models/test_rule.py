import pytest
from builders import make_range, make_rarity_condition, make_rule

from poeclifilter.filters import BandNames, GearGroup
from poeclifilter.game import ArmourClass, IconColor, Operator, Rarity, WeaponClass
from poeclifilter.models import rule
from poeclifilter.models.display import Display, PlayEffect


def raw_rule(**fields):
    return {"id": "good_rares", "comment": "Rares worth picking up"} | fields


def test_parse_keeps_id_and_comment():
    result = rule.parse(raw_rule())
    assert result.id == "good_rares"
    assert result.comment == "Rares worth picking up"


def test_parse_minimal_rule_leaves_optional_fields_unset():
    result = rule.parse(raw_rule())
    assert result == make_rule(id="good_rares", comment="Rares worth picking up")


def test_parse_rejects_missing_id():
    with pytest.raises(KeyError):
        rule.parse({"comment": "No id"})


def test_parse_include_defaults_to_true():
    result = rule.parse(raw_rule())
    assert result.include is True


def test_parse_keeps_include_false():
    result = rule.parse(raw_rule(include=False))
    assert result.include is False


def test_parse_keeps_hide_false():
    result = rule.parse(raw_rule(hide=False))
    assert result.hide is False


def test_parse_converts_bands_to_enums():
    result = rule.parse(raw_rule(bands={"str": ["A"], "str_int": ["B"]}))
    assert result.bands is not None
    assert result.bands == {
        GearGroup.STR: [BandNames.A],
        GearGroup.STR_INT: [BandNames.B],
    }
    assert all(type(group) is GearGroup for group in result.bands)
    assert all(type(band) is BandNames for bands in result.bands.values() for band in bands)


def test_parse_accepts_weapon_and_armour_groups_in_one_rule():
    result = rule.parse(raw_rule(bands={"str": ["A"], "bows": ["S"]}))
    assert result.bands == {
        GearGroup.STR: [BandNames.A],
        GearGroup.BOWS: [BandNames.S],
    }


def test_parse_rejects_unknown_gear_group():
    with pytest.raises(ValueError):
        rule.parse(raw_rule(bands={"str_itn": "A"}))


def test_parse_rejects_unknown_band():
    with pytest.raises(ValueError):
        rule.parse(raw_rule(bands={"str": "Z"}))


def test_parse_keeps_base_types():
    result = rule.parse(raw_rule(base_types=["Astral Plate", "Glorious Plate"]))
    assert result.base_types == ["Astral Plate", "Glorious Plate"]


def test_parse_converts_armour_classes_to_enum():
    result = rule.parse(raw_rule(item_classes=["Helmets", "Body Armours"]))
    assert result.item_classes == [ArmourClass.HELMETS, ArmourClass.BODY_ARMOURS]
    assert result.item_classes is not None
    assert all(type(item_class) is ArmourClass for item_class in result.item_classes)


def test_parse_converts_weapon_classes_to_enum():
    result = rule.parse(raw_rule(item_classes=["Bows", "Thrusting One Hand Swords"]))
    assert result.item_classes == [WeaponClass.BOWS, WeaponClass.THRUSTING_ONE_HAND_SWORDS]
    assert result.item_classes is not None
    assert all(type(item_class) is WeaponClass for item_class in result.item_classes)


def test_parse_keeps_armour_and_weapon_classes_in_one_rule():
    result = rule.parse(raw_rule(item_classes=["Shields", "Wands"]))
    assert result.item_classes == [ArmourClass.SHIELDS, WeaponClass.WANDS]


def test_parse_rejects_unknown_item_class():
    with pytest.raises(ValueError, match="Unknown item class 'Body Armour'"):
        rule.parse(raw_rule(item_classes=["Body Armour"]))


def test_parse_converts_rarity_condition_to_enums():
    result = rule.parse(raw_rule(rarity={"operator": "<=", "rarity": "Rare"}))
    assert result.rarity == make_rarity_condition(operator=Operator.LESS_EQUAL, rarity=Rarity.RARE)
    assert result.rarity is not None
    assert type(result.rarity.operator) is Operator
    assert type(result.rarity.rarity) is Rarity


def test_parse_rejects_unknown_rarity():
    with pytest.raises(ValueError):
        rule.parse(raw_rule(rarity={"operator": "==", "rarity": "rare"}))


def test_parse_rejects_unknown_rarity_operator():
    with pytest.raises(ValueError):
        rule.parse(raw_rule(rarity={"operator": "=<", "rarity": "Rare"}))


def test_parse_rejects_rarity_without_operator():
    with pytest.raises(KeyError):
        rule.parse(raw_rule(rarity={"rarity": "Rare"}))


def test_parse_rejects_bare_rarity_string():
    with pytest.raises(TypeError):
        rule.parse(raw_rule(rarity="Rare"))


def test_parse_keeps_range_with_min_and_max():
    result = rule.parse(raw_rule(item_level={"min": 75, "max": 85}))
    assert result.item_level == make_range(min=75, max=85)


def test_parse_keeps_range_with_only_min():
    result = rule.parse(raw_rule(linked_sockets={"min": 5}))
    assert result.linked_sockets == make_range(min=5)


def test_parse_keeps_range_min_of_zero():
    result = rule.parse(raw_rule(item_level={"min": 0}))
    assert result.item_level == make_range(min=0)


def test_parse_keeps_sockets_range():
    result = rule.parse(raw_rule(sockets={"max": 6}))
    assert result.sockets == make_range(max=6)


def test_parse_keeps_display_reference():
    result = rule.parse(raw_rule(display="$good_rare"))
    assert result.display == "$good_rare"


def test_parse_parses_inline_display():
    result = rule.parse(raw_rule(display={"play_effect": {"color": "Orange"}}))
    assert isinstance(result.display, Display)
    assert result.display.play_effect == PlayEffect(color=IconColor.ORANGE, temp=None)


def test_parse_parses_child_rules():
    raw = raw_rule(
        rules=[
            {"id": "high_ilvl", "comment": "Endgame", "item_level": {"min": 86}},
            {"id": "helmets", "comment": "Helmets", "item_classes": ["Helmets"]},
        ]
    )
    result = rule.parse(raw)
    assert result.rules == [
        make_rule(id="high_ilvl", comment="Endgame", item_level=make_range(min=86)),
        make_rule(id="helmets", comment="Helmets", item_classes=[ArmourClass.HELMETS]),
    ]


def test_parse_parses_nested_child_rules():
    raw = raw_rule(
        rules=[
            {
                "id": "child",
                "comment": "Child",
                "rules": [{"id": "grandchild", "comment": "Grandchild"}],
            }
        ]
    )
    result = rule.parse(raw)
    assert result.rules is not None
    assert result.rules[0].rules == [make_rule(id="grandchild", comment="Grandchild")]


def test_parse_child_rule_values_are_not_inherited_at_parse():
    raw = raw_rule(
        hide=True,
        rarity={"operator": "==", "rarity": "Rare"},
        rules=[{"id": "child", "comment": "Child"}],
    )
    result = rule.parse(raw)
    assert result.rules is not None
    assert result.rules[0].hide is None
    assert result.rules[0].rarity is None
