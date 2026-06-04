"""Tests de squelette pour l'explicabilite."""

import pytest

from data.schemas import MovieFeatures
from fuzzy.inference_engine import InferenceResult
from recommender.explanation_engine import ExplanationEngine
from recommender.user_profile import UserProfile


def test_explanation_engine_contract_exists() -> None:
    """Le moteur d'explications expose son seuil de filtrage."""

    engine = ExplanationEngine(activation_threshold=0.1)
    assert engine.activation_threshold == 0.1


def test_explanation_engine_is_not_implemented_yet() -> None:
    """Le squelette ne doit pas encore generer d'explications."""

    engine = ExplanationEngine()
    movie = MovieFeatures(movie_id=1, title="Example (2000)")
    with pytest.raises(NotImplementedError):
        engine.explain(UserProfile(user_id=1), movie, InferenceResult())
