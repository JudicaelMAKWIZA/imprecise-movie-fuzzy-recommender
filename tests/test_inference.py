"""Tests du moteur d'inference Mamdani."""

import pytest

from fuzzy.aggregation import ConsequentAggregator
from fuzzy.inference_engine import MamdaniInferenceEngine, RuleActivation
from fuzzy.rule_base import RuleBase


def test_mamdani_engine_contract_exists() -> None:
    """Le moteur Mamdani est instanciable avec une base de regles vide."""

    engine = MamdaniInferenceEngine(rule_base=RuleBase(name="empty"))
    assert engine.rule_base.name == "empty"


def test_mamdani_engine_activates_rule_with_min_and() -> None:
    """L'activation d'une regle utilise l'operateur AND par minimum."""

    engine = MamdaniInferenceEngine(rule_base=RuleBase.load_minimal_v1())
    rule = engine.rule_base.get_rule("R1")

    activation = engine.activate_rule(
        rule,
        {
            "genre_preference": {"forte": 0.7},
            "average_rating": {"excellente": 0.9},
            "popularity": {"tres_populaire": 0.8},
        },
    )

    assert activation.degree == pytest.approx(0.7)
    assert activation.antecedent_degrees == {
        "genre_preference": 0.7,
        "average_rating": 0.9,
        "popularity": 0.8,
    }
    assert activation.is_active is True
    assert activation.consequent_term == "tres_fort"


def test_mamdani_engine_generates_inference_result() -> None:
    """L'inference produit les regles activees et la sortie agregee."""

    engine = MamdaniInferenceEngine(rule_base=RuleBase.load_minimal_v1())

    result = engine.infer(
        {
            "genre_preference": {"forte": 0.7},
            "average_rating": {"excellente": 0.9},
            "popularity": {"tres_populaire": 0.8},
        }
    )

    assert result.crisp_score is None
    assert result.output_variable == "recommendation_score"
    assert result.output_memberships == {"tres_fort": pytest.approx(0.7)}
    assert [activation.rule.identifier for activation in result.activated_rules] == ["R1"]
    assert len(result.evaluated_rules) == 8


def test_mamdani_engine_aggregates_same_consequent_by_max() -> None:
    """Deux regles activant le meme terme de sortie sont agregees par max."""

    engine = MamdaniInferenceEngine(rule_base=RuleBase.load_minimal_v1())

    result = engine.infer(
        {
            "genre_preference": {"forte": 0.8},
            "average_rating": {"excellente": 0.7, "bonne": 0.4},
            "popularity": {"confidentiel": 0.6, "populaire": 0.5},
        }
    )

    assert [activation.rule.identifier for activation in result.activated_rules] == ["R2", "R3"]
    assert result.output_memberships == {"fort": pytest.approx(0.6)}


def test_mamdani_engine_returns_empty_output_when_no_rule_is_active() -> None:
    """Des entrees manquantes donnent des activations nulles tracees."""

    engine = MamdaniInferenceEngine(rule_base=RuleBase.load_minimal_v1())
    result = engine.infer({})

    assert result.output_memberships == {}
    assert result.activated_rules == []
    assert len(result.evaluated_rules) == 8
    assert all(activation.degree == 0.0 for activation in result.evaluated_rules)


def test_mamdani_engine_rejects_invalid_membership_degree() -> None:
    """Les degres d'appartenance doivent rester dans [0, 1]."""

    engine = MamdaniInferenceEngine(rule_base=RuleBase.load_minimal_v1())

    with pytest.raises(ValueError):
        engine.infer({"genre_preference": {"forte": 1.2}})


def test_mamdani_implication_clips_consequent_at_activation_degree() -> None:
    """L'implication Mamdani conserve le terme consequent coupe au degre actif."""

    engine = MamdaniInferenceEngine(rule_base=RuleBase.load_minimal_v1())
    activation = RuleActivation(rule=engine.rule_base.get_rule("R8"), degree=0.35)

    assert engine.imply_consequent(activation) == {"tres_faible": pytest.approx(0.35)}


def test_consequent_aggregator_uses_max() -> None:
    """Le service d'agregation dedie applique aussi l'agregation par maximum."""

    rule_base = RuleBase.load_minimal_v1()
    activations = [
        RuleActivation(rule=rule_base.get_rule("R2"), degree=0.4),
        RuleActivation(rule=rule_base.get_rule("R3"), degree=0.7),
        RuleActivation(rule=rule_base.get_rule("R1"), degree=0.5),
    ]

    assert ConsequentAggregator().aggregate(activations) == {
        "fort": pytest.approx(0.7),
        "tres_fort": pytest.approx(0.5),
    }


def test_consequent_aggregator_rejects_unknown_method() -> None:
    """La V1 supporte uniquement l'agregation max."""

    with pytest.raises(ValueError):
        ConsequentAggregator(method="sum").aggregate([])
