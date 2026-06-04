"""Evaluation scientifique du systeme de recommandation."""

from .evaluator import Evaluator, EvaluationReport
from .metrics import coverage, diversity_score, precision_at_n, recall_at_n

__all__ = [
    "EvaluationReport",
    "Evaluator",
    "coverage",
    "diversity_score",
    "precision_at_n",
    "recall_at_n",
]
