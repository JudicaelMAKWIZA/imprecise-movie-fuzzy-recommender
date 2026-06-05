"""Tests du moteur d'explications."""

import pytest

from data.movie_repository import MovieRepository
from data.schemas import MovieFeatures
from fuzzy.fuzzification import Fuzzifier
from fuzzy.inference_engine import MamdaniInferenceEngine
from fuzzy.rule_base import RuleBase
from recommender.explanation_engine import ExplanationEngine
from recommender.fuzzy_recommender import FuzzyRecommender
from recommender.user_profile import GenrePreference, UserProfile


def test_explanation_engine_generates_structured_and_text_explanation() -> None:
    """L'explication expose criteres, regles, consequent et score."""

    recommender = FuzzyRecommender(
        repository=MovieRepository(
            [
                MovieFeatures(
                    movie_id=1,
                    title="Interstellar (2014)",
                    genre_list=["Sci-Fi"],
                    average_rating=4.8,
                    number_of_ratings=300,
                )
            ]
        ),
        fuzzifier=Fuzzifier.default_v1(),
        inference_engine=MamdaniInferenceEngine(RuleBase.load_minimal_v1()),
    )
    profile = UserProfile(user_id=1)
    profile.set_genre_preference(GenrePreference("Sci-Fi", 0.9))

    recommendation = recommender.score_movie(profile, recommender.repository.get_by_id(1))
    explanation = ExplanationEngine().explain_recommendation(profile, recommendation)

    assert explanation.score == pytest.approx(recommendation.score)
    assert explanation.dominant_output_term == "tres_fort"
    assert [criterion.name for criterion in explanation.criteria] == [
        "genre_preference",
        "average_rating",
        "popularity",
    ]
    assert [activation.rule.identifier for activation in explanation.activated_rules] == ["R1"]
    assert "Interstellar (2014)" in explanation.text
    assert "R1" in explanation.text
    assert "Defuzzification centroide" in explanation.text


def test_explanation_engine_filters_low_activation_rules() -> None:
    """Le seuil d'affichage conserve uniquement les regles assez actives."""

    recommender = FuzzyRecommender(
        repository=MovieRepository([MovieFeatures(1, "Niche Sci-Fi", ["Sci-Fi"], 4.8, 2)]),
        fuzzifier=Fuzzifier.default_v1(),
        inference_engine=MamdaniInferenceEngine(RuleBase.load_minimal_v1()),
    )
    profile = UserProfile(user_id=1)
    profile.set_genre_preference(GenrePreference("Sci-Fi", 0.57))

    recommendation = recommender.score_movie(profile, recommender.repository.get_by_id(1))
    explanation = ExplanationEngine(activation_threshold=0.2).explain_recommendation(profile, recommendation)

    assert recommendation.inference.activated_rules
    assert explanation.activated_rules == []
    assert "Aucune regle ne depasse le seuil" in explanation.text


def test_explanation_engine_rejects_invalid_threshold() -> None:
    """Le seuil d'activation doit rester dans [0, 1]."""

    with pytest.raises(ValueError):
        ExplanationEngine(activation_threshold=1.5)
