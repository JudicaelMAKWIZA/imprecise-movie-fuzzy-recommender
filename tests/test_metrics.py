"""Tests des metriques simples d'evaluation."""

import pytest

from evaluation.evaluator import Evaluator
from evaluation.metrics import coverage, diversity_score, precision_at_n, recall_at_n


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
