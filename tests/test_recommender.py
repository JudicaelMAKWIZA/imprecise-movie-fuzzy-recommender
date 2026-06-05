"""Tests du pipeline de recommandation floue V1."""

import pytest

from data_manager.movie_repository import MovieRepository
from data_manager.schemas import MovieFeatures
from fuzzy.fuzzifier import Fuzzifier
from fuzzy.inference_engine import MamdaniInferenceEngine
from fuzzy.rule_base import RuleBase
from recommender.fuzzy_recommender import FuzzyRecommender
from recommender.user_profile import GenrePreference, LinguisticGenrePreference, UserProfile


def test_recommender_contract_exists() -> None:
    """La facade de recommandation assemble les dependances principales."""

    recommender = FuzzyRecommender(
        repository=MovieRepository(movies=[]),
        fuzzifier=Fuzzifier(variables={}),
        inference_engine=MamdaniInferenceEngine(rule_base=RuleBase(name="empty")),
    )
    assert recommender.repository is not None


def test_score_movie_runs_complete_fuzzy_pipeline() -> None:
    """Un film excellent dans un genre apprecie obtient un score eleve."""

    recommender = _build_recommender(
        [
            MovieFeatures(
                movie_id=1,
                title="Interstellar (2014)",
                genre_list=["Sci-Fi"],
                average_rating=4.8,
                number_of_ratings=300,
            )
        ]
    )
    profile = _profile({"Sci-Fi": 0.9})

    recommendation = recommender.score_movie(profile, recommender.repository.get_by_id(1))

    assert recommendation.score == pytest.approx(recommendation.inference.crisp_score)
    assert recommendation.score > 0.8
    assert recommendation.crisp_inputs == {
        "genre_preference": pytest.approx(0.9),
        "average_rating": pytest.approx(4.8),
        "popularity": pytest.approx(300.0),
    }
    assert recommendation.fuzzy_inputs["genre_preference"]["forte"] == 1.0
    assert [activation.rule.identifier for activation in recommendation.inference.activated_rules] == ["R1"]


def test_recommend_prefilters_ranks_and_returns_top_n() -> None:
    """Le pipeline prefiltre par genre, score les candidats et classe le Top-N."""

    recommender = _build_recommender(
        [
            MovieFeatures(1, "Excellent Sci-Fi", ["Sci-Fi"], 4.8, 300),
            MovieFeatures(2, "Weak Sci-Fi", ["Sci-Fi"], 1.0, 160),
            MovieFeatures(3, "Excellent Comedy", ["Comedy"], 4.8, 300),
        ]
    )
    profile = _profile({"Sci-Fi": 0.9, "Comedy": 0.2})

    recommendations = recommender.recommend(profile, top_n=2)

    assert [recommendation.movie.movie_id for recommendation in recommendations] == [1, 2]
    assert recommendations[0].score > recommendations[1].score
    assert all(recommendation.movie.movie_id != 3 for recommendation in recommendations)


def test_recommend_rejects_invalid_top_n() -> None:
    """top_n doit etre positif."""

    recommender = _build_recommender([])

    with pytest.raises(ValueError):
        recommender.recommend(_profile({"Sci-Fi": 0.9}), top_n=0)


def test_linguistic_genre_preference_is_fuzzified_without_crisp_value() -> None:
    """Un terme linguistique active directement le terme flou correspondant."""

    recommender = _build_recommender([MovieFeatures(1, "Linguistic Sci-Fi", ["Sci-Fi"], 4.8, 300)])
    profile = UserProfile(user_id=1)
    profile.set_genre_preference(GenrePreference("Sci-Fi", LinguisticGenrePreference("forte")))

    recommendation = recommender.score_movie(profile, recommender.repository.get_by_id(1))

    assert recommendation.crisp_inputs["genre_preference"] == LinguisticGenrePreference("forte")
    assert recommendation.fuzzy_inputs["genre_preference"]["forte"] == 1.0
    assert recommendation.score > 0.8


def test_missing_average_rating_uses_neutral_value() -> None:
    """L'absence de note moyenne n'est pas assimilee a une mauvaise note."""

    recommender = _build_recommender([MovieFeatures(1, "Unrated Sci-Fi", ["Sci-Fi"], None, 300)])
    recommendation = recommender.score_movie(_profile({"Sci-Fi": 0.9}), recommender.repository.get_by_id(1))

    assert recommendation.crisp_inputs["average_rating"] == pytest.approx(3.5)


def test_neutral_profile_does_not_prefilter_whole_catalog() -> None:
    """Sans genre au-dessus du seuil, l'Architecture B ne scanne pas tout."""

    recommender = _build_recommender([MovieFeatures(1, "Drama", ["Drama"], 4.0, 20)])
    assert recommender.prefilter_candidates(_profile({"Drama": 0.4})) == []


def test_score_movie_without_matching_rule_returns_zero_score() -> None:
    """Si aucune regle ne s'active, la defuzzification retourne 0.0."""

    recommender = _build_recommender(
        [MovieFeatures(1, "No Rule Case", ["Drama"], 3.0, 40)]
    )
    profile = _profile({"Drama": 0.1})

    recommendation = recommender.score_movie(profile, recommender.repository.get_by_id(1))

    assert recommendation.score == 0.0
    assert recommendation.inference.activated_rules == []


def _build_recommender(movies: list[MovieFeatures]) -> FuzzyRecommender:
    return FuzzyRecommender(
        repository=MovieRepository(movies=movies),
        fuzzifier=Fuzzifier.default_v1(),
        inference_engine=MamdaniInferenceEngine(rule_base=RuleBase.load_minimal_v1()),
    )


def _profile(preferences: dict[str, float]) -> UserProfile:
    profile = UserProfile(user_id=1)
    for genre, value in preferences.items():
        profile.set_genre_preference(GenrePreference(genre=genre, value=value))
    return profile
