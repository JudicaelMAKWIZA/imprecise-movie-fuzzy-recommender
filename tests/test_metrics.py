"""Tests des metriques simples d'evaluation."""

import pytest

from evaluation.evaluator import Evaluator
from evaluation.metrics import coverage, diversity_score, precision_at_n, recall_at_n
from data_manager.movie_repository import MovieRepository
from data_manager.schemas import MovieFeatures
from fuzzy.fuzzifier import Fuzzifier
from fuzzy.inference_engine import MamdaniInferenceEngine
from fuzzy.rule_base import RuleBase
from recommender.fuzzy_recommender import FuzzyRecommender


def test_precision_recall_and_coverage() -> None:
    """Les metriques de base suivent leurs definitions standard."""

    recommended = [1, 2, 3]
    relevant = [2, 4]

    assert precision_at_n(recommended, relevant, 3) == pytest.approx(1 / 3)
    assert recall_at_n(recommended, relevant, 3) == pytest.approx(1 / 2)
    assert coverage(recommended, [1, 2, 3, 4, 5]) == pytest.approx(3 / 5)


def test_diversity_score_with_genres() -> None:
    """La diversite utilise la distance de Jaccard moyenne entre genres."""

    genres = {
        1: {"Sci-Fi", "Drama"},
        2: {"Comedy"},
        3: {"Sci-Fi"},
    }

    assert diversity_score([1, 2], genres) == 1.0
    assert diversity_score([1, 3], genres) == pytest.approx(0.5)


def test_evaluator_evaluate_lists() -> None:
    """L'evaluateur agrege les metriques simples dans un rapport."""

    report = Evaluator(top_n=2).evaluate_lists(
        recommended=[1, 2, 3],
        relevant=[2, 4],
        full_catalog=[1, 2, 3, 4],
        genres_by_movie={1: {"A"}, 2: {"B"}},
    )

    assert report.metrics["precision_at_n"] == pytest.approx(0.5)
    assert report.metrics["recall_at_n"] == pytest.approx(0.5)
    assert report.metrics["coverage"] == pytest.approx(0.75)
    assert report.metrics["diversity"] == pytest.approx(1.0)


def test_evaluator_evaluate_user_temporal_split() -> None:
    """Le profil est derive du train et la pertinence du test temporel."""

    pd = pytest.importorskip("pandas")
    raw_data = {
        "ratings": pd.DataFrame(
            [
                {"userId": 1, "movieId": 1, "rating": 5.0, "timestamp": 1},
                {"userId": 1, "movieId": 2, "rating": 5.0, "timestamp": 2},
                {"userId": 2, "movieId": 1, "rating": 5.0, "timestamp": 3},
            ]
        ),
        "movies": pd.DataFrame(
            [
                {"movieId": 1, "title": "Train Sci-Fi", "genres": "Sci-Fi"},
                {"movieId": 2, "title": "Heldout Sci-Fi", "genres": "Sci-Fi"},
            ]
        ),
        "tags": pd.DataFrame(columns=["userId", "movieId", "tag", "timestamp"]),
        "links": pd.DataFrame(columns=["movieId", "imdbId", "tmdbId"]),
    }
    recommender = FuzzyRecommender(
        repository=MovieRepository(
            [
                MovieFeatures(1, "Train Sci-Fi", ["Sci-Fi"], 4.8, 300),
                MovieFeatures(2, "Heldout Sci-Fi", ["Sci-Fi"], 4.8, 300),
            ]
        ),
        fuzzifier=Fuzzifier.default_v1(),
        inference_engine=MamdaniInferenceEngine(RuleBase.load_minimal_v1()),
    )

    report = Evaluator(top_n=2).evaluate_user(user_id=1, raw_data=raw_data, recommender=recommender, test_ratio=0.5)

    assert report.metrics["recall_at_n"] == pytest.approx(1.0)
    assert any("train=1, test=1" in note for note in report.notes)


def test_evaluator_rebuilds_features_from_train_split() -> None:
    """Une moyenne issue uniquement du test ne doit pas favoriser un candidat."""

    pd = pytest.importorskip("pandas")
    raw_data = {
        "ratings": pd.DataFrame(
            [
                {"userId": 1, "movieId": 1, "rating": 5.0, "timestamp": 1},
                {"userId": 1, "movieId": 2, "rating": 5.0, "timestamp": 2},
            ]
        ),
        "movies": pd.DataFrame(
            [
                {"movieId": 1, "title": "Train Sci-Fi", "genres": "Sci-Fi"},
                {"movieId": 2, "title": "Heldout Sci-Fi", "genres": "Sci-Fi"},
            ]
        ),
        "tags": pd.DataFrame(columns=["userId", "movieId", "tag", "timestamp"]),
        "links": pd.DataFrame(columns=["movieId", "imdbId", "tmdbId"]),
    }
    recommender_with_leaky_features = FuzzyRecommender(
        repository=MovieRepository(
            [
                MovieFeatures(1, "Train Sci-Fi", ["Sci-Fi"], 3.0, 1),
                MovieFeatures(2, "Heldout Sci-Fi", ["Sci-Fi"], 5.0, 1),
            ]
        ),
        fuzzifier=Fuzzifier.default_v1(),
        inference_engine=MamdaniInferenceEngine(RuleBase.load_minimal_v1()),
    )

    report = Evaluator(top_n=1).evaluate_user(
        user_id=1,
        raw_data=raw_data,
        recommender=recommender_with_leaky_features,
        test_ratio=0.5,
    )

    assert report.metrics["recall_at_n"] == pytest.approx(0.0)
