"""Tests de la base de regles floues V1."""

import pytest

from fuzzy.rule_base import (
    FuzzyAntecedent,
    FuzzyConsequent,
    FuzzyRule,
    RuleBase,
    RuleValidationError,
    V1_INPUT_TERMS,
    V1_OUTPUT_TERMS,
)


def test_minimal_v1_rule_base_has_exactly_eight_rules() -> None:
    """La base officielle V1 contient exactement 8 regles ordonnees."""

    rule_base = RuleBase.load_minimal_v1()

    assert rule_base.name == "minimal_v1"
    assert len(rule_base.rules) == 8
    assert [rule.identifier for rule in rule_base.rules] == [f"R{index}" for index in range(1, 9)]


def test_minimal_v1_rules_use_required_variables_and_output() -> None:
    """Chaque regle utilise les trois variables V1 et la sortie officielle."""

    rule_base = RuleBase.load_minimal_v1()
    expected_variables = frozenset(V1_INPUT_TERMS)

    for rule in rule_base:
        assert rule.antecedent_variables == expected_variables
        assert rule.consequent.variable == "recommendation_score"
        assert rule.consequent.term in V1_OUTPUT_TERMS["recommendation_score"]
        assert rule.conjunction == "AND"
        assert rule.description


def test_minimal_v1_rules_are_interpretable_text() -> None:
    """Le rendu textuel expose une forme IF/THEN lisible."""

    rule = RuleBase.load_minimal_v1().get_rule("R1")

    assert rule.as_text() == (
        "R1: IF genre_preference IS forte AND average_rating IS excellente "
        "AND popularity IS tres_populaire THEN recommendation_score IS tres_fort"
    )


def test_minimal_v1_contains_expected_scientific_cases() -> None:
    """Les cas pedagogiques principaux sont bien representes."""

    rule_base = RuleBase.load_minimal_v1()

    assert rule_base.get_rule("R1").consequent.term == "tres_fort"
    assert rule_base.get_rule("R6").consequent.term == "moyen"
    assert rule_base.get_rule("R8").consequent.term == "tres_faible"


def test_rule_base_rejects_wrong_rule_count() -> None:
    """minimal_v1 doit refuser tout nombre different de 8 regles."""

    valid_rule = RuleBase.load_minimal_v1().get_rule("R1")
    rule_base = RuleBase(name="minimal_v1", rules=[valid_rule])

    with pytest.raises(RuleValidationError):
        rule_base.validate()


def test_rule_base_rejects_unknown_input_term() -> None:
    """La validation detecte les termes d'entree inconnus."""

    rule = FuzzyRule(
        identifier="R1",
        antecedents=(
            FuzzyAntecedent("genre_preference", "forte"),
            FuzzyAntecedent("average_rating", "incroyable"),
            FuzzyAntecedent("popularity", "populaire"),
        ),
        consequent=FuzzyConsequent("recommendation_score", "fort"),
        description="Regle invalide pour tester la validation.",
    )
    rule_base = RuleBase(name="custom", rules=[rule])

    with pytest.raises(RuleValidationError):
        rule_base.validate()


def test_rule_base_rejects_missing_popularity_variable() -> None:
    """Une regle V1 doit inclure la popularite."""

    rule = FuzzyRule(
        identifier="R1",
        antecedents=(
            FuzzyAntecedent("genre_preference", "forte"),
            FuzzyAntecedent("average_rating", "excellente"),
        ),
        consequent=FuzzyConsequent("recommendation_score", "fort"),
        description="Regle invalide sans popularite.",
    )
    rule_base = RuleBase(name="custom", rules=[rule])

    with pytest.raises(RuleValidationError):
        rule_base.validate()


def test_rule_base_rejects_unknown_output() -> None:
    """La sortie doit etre recommendation_score avec un terme connu."""

    rule = FuzzyRule(
        identifier="R1",
        antecedents=(
            FuzzyAntecedent("genre_preference", "forte"),
            FuzzyAntecedent("average_rating", "excellente"),
            FuzzyAntecedent("popularity", "populaire"),
        ),
        consequent=FuzzyConsequent("recommendation_score", "parfait"),
        description="Regle invalide pour tester la sortie.",
    )
    rule_base = RuleBase(name="custom", rules=[rule])

    with pytest.raises(RuleValidationError):
        rule_base.validate()
