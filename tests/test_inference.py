"""Tests de squelette pour le moteur d'inference."""

import pytest

from fuzzy.inference_engine import MamdaniInferenceEngine
from fuzzy.rule_base import RuleBase


def test_mamdani_engine_contract_exists() -> None:
    """Le moteur Mamdani est instanciable avec une base de regles vide."""

    engine = MamdaniInferenceEngine(rule_base=RuleBase(name="empty"))
    assert engine.rule_base.name == "empty"


def test_mamdani_engine_is_not_implemented_yet() -> None:
    """Le squelette ne doit pas encore inferer de score."""

    engine = MamdaniInferenceEngine(rule_base=RuleBase(name="empty"))
    with pytest.raises(NotImplementedError):
        engine.infer({})
