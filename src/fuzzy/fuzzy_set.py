"""Ensemble flou de base.

Un ensemble flou associe un nom linguistique a une fonction d'appartenance. Il
constitue la brique centrale des variables linguistiques du projet.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable

from .membership_functions import MembershipFunction

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FuzzySet:
    """Represent a fuzzy set over a numeric universe.

    Attributes:
        name: Technical identifier of the set, for example `forte`.
        membership_function: Function used to compute membership degrees.
        label: Optional display label for CLI, reports or GUI.

    The class is deliberately small: it owns no inference logic and only answers
    the foundational question `to which degree does x belong to this set?`.
    """

    name: str
    membership_function: MembershipFunction
    label: str | None = None

    def membership(self, value: float) -> float:
        """Return the membership degree of `value` in this fuzzy set."""

        degree = self.membership_function(value)
        logger.debug("Degre d'appartenance: set=%s value=%s degree=%s", self.name, value, degree)
        return degree

    def __call__(self, value: float) -> float:
        """Shortcut for `membership(value)`."""

        return self.membership(value)

    def sample(self, universe: Iterable[float]) -> list[tuple[float, float]]:
        """Evaluate the fuzzy set over a sequence of universe values."""

        return [(float(value), self.membership(float(value))) for value in universe]

    def alpha_cut(self, universe: Iterable[float], alpha: float) -> list[float]:
        """Return sampled values whose membership degree is at least `alpha`."""

        if not 0.0 <= alpha <= 1.0:
            raise ValueError("alpha doit appartenir a [0, 1].")
        return [float(value) for value in universe if self.membership(float(value)) >= alpha]
