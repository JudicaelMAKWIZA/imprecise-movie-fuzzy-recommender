"""Tests de squelette pour la couche recommandation."""

import pytest

from data.movie_repository import MovieRepository
from fuzzy.fuzzification import Fuzzifier
from fuzzy.inference_engine import MamdaniInferenceEngine
from fuzzy.rule_base import RuleBase
from recommender.fuzzy_recommender import FuzzyRecommender
from recommender.user_profile import UserProfile


def test_recommender_contract_exists() -> None:
    """La facade de recommandation assemble les dependances principales."""

    recommender = FuzzyRecommender(
        repository=MovieRepository(movies=[]),
        fuzzifier=Fuzzifier(variables={}),
        inference_engine=MamdaniInferenceEngine(rule_base=RuleBase(name="empty")),
    )
    assert recommender.repository is not None


def test_recommender_is_not_implemented_yet() -> None:
    """Le squelette ne doit pas encore recommander de films."""

    recommender = FuzzyRecommender(
        repository=MovieRepository(movies=[]),
        fuzzifier=Fuzzifier(variables={}),
        inference_engine=MamdaniInferenceEngine(rule_base=RuleBase(name="empty")),
    )
    with pytest.raises(NotImplementedError):
        recommender.recommend(UserProfile(user_id=1))
