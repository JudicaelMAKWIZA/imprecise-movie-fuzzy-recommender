"""Tests des metriques simples d'evaluation."""

import pytest

from evaluation.evaluator import Evaluator
from evaluation.metrics import coverage, diversity_score, precision_at_n, recall_at_n
from data_manager.movie_repository import MovieRepository
from data_manager.preprocessor import MovieLensPreprocessor
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
    """Le profil et les features de scoring sont derives du train temporel."""

    pd = pytest.importorskip("pandas")
    raw_data = {
        "ratings": pd.DataFrame(
            [
                {"userId": 1, "movieId": 1, "rating": 5.0, "timestamp": 1},
                {"userId": 2, "movieId": 1, "rating": 5.0, "timestamp": 2},
                {"userId": 2, "movieId": 2, "rating": 1.0, "timestamp": 3},
                {"userId": 1, "movieId": 2, "rating": 5.0, "timestamp": 4},
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
    class SpyRecommender(FuzzyRecommender):
        cloned_repository: MovieRepository | None = None

        def with_repository(self, repository: MovieRepository) -> FuzzyRecommender:
            self.cloned_repository = repository
            return super().with_repository(repository)

    recommender = SpyRecommender(
        repository=MovieRepository.from_dataframe(MovieLensPreprocessor().build_movie_features(raw_data)),
        fuzzifier=Fuzzifier.default_v1(),
        inference_engine=MamdaniInferenceEngine(RuleBase.load_minimal_v1()),
    )

    report = Evaluator(top_n=2).evaluate_user(user_id=1, raw_data=raw_data, recommender=recommender, test_ratio=0.5)

    assert recommender.cloned_repository is not None
    assert recommender.cloned_repository.get_by_id(2).average_rating == pytest.approx(1.0)
    assert recommender.repository.get_by_id(2).average_rating == pytest.approx(3.0)
    assert "recall_at_n" in report.metrics
    assert any("train=1, test=1" in note for note in report.notes)


def test_evaluator_uses_passed_recommender() -> None:
    """evaluate_user reutilise le recommender fourni."""

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
    class CountingRecommender:
        def __init__(self) -> None:
            self.calls = 0
            self.repository = MovieRepository(
                [
                    MovieFeatures(1, "Train Sci-Fi", ["Sci-Fi"], 3.0, 1),
                    MovieFeatures(2, "Heldout Sci-Fi", ["Sci-Fi"], 5.0, 1),
                ]
            )

        def recommend(self, profile, top_n: int):
            self.calls += 1
            return [
                type(
                    "RecommendationStub",
                    (),
                    {"movie": self.repository.get_by_id(2), "score": 0.9},
                )()
            ][:top_n]

        def with_repository(self, repository):
            self.repository = repository
            return self

    recommender = CountingRecommender()

    report = Evaluator(top_n=1).evaluate_user(
        user_id=1,
        raw_data=raw_data,
        recommender=recommender,
        test_ratio=0.5,
    )

    assert recommender.calls == 1
    assert report.metrics["recall_at_n"] == pytest.approx(1.0)
