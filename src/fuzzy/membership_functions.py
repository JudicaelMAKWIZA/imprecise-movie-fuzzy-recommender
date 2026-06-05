"""Fonctions d'appartenance floues implementees from scratch.

Les fonctions triangulaire et trapezoidale sont les deux formes retenues pour la
Version 1 du projet. Aucune dependance floue externe n'est utilisee : chaque
degre d'appartenance est calcule explicitement en Python.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence

logger = logging.getLogger(__name__)


class MembershipFunction(ABC):
    """Contrat commun a toutes les fonctions d'appartenance."""

    @abstractmethod
    def __call__(self, value: float) -> float:
        """Return the membership degree of `value` in `[0, 1]`."""

    @property
    @abstractmethod
    def parameters(self) -> tuple[float, ...]:
        """Return the ordered numeric parameters defining the function."""


@dataclass(frozen=True)
class TriangularMembershipFunction(MembershipFunction):
    """Fonction d'appartenance triangulaire.

    Args:
        a: Borne gauche ou le degre vaut 0.
        b: Sommet du triangle ou le degre vaut 1.
        c: Borne droite ou le degre vaut 0.

    The parameters must satisfy `a < b < c`. The implementation follows the
    standard piecewise-linear triangular function and clips tiny floating-point
    artefacts to `[0, 1]`.
    """

    a: float
    b: float
    c: float

    def __post_init__(self) -> None:
        if not self.a < self.b < self.c:
            raise ValueError("Une fonction triangulaire exige a < b < c.")

    @property
    def parameters(self) -> tuple[float, ...]:
        return (self.a, self.b, self.c)

    def __call__(self, value: float) -> float:
        x = float(value)
        if x <= self.a or x >= self.c:
            return 0.0
        if x == self.b:
            return 1.0
        if x < self.b:
            return _clip01((x - self.a) / (self.b - self.a))
        return _clip01((self.c - x) / (self.c - self.b))


@dataclass(frozen=True)
class TrapezoidalMembershipFunction(MembershipFunction):
    """Fonction d'appartenance trapezoidale.

    Args:
        a: Debut de la rampe montante.
        b: Debut du plateau.
        c: Fin du plateau.
        d: Fin de la rampe descendante.

    The parameters must satisfy `a <= b <= c <= d` and `a < d`. Shoulder sets
    such as `(0, 0, 0.2, 0.45)` and `(0.55, 0.8, 1, 1)` are supported.
    """

    a: float
    b: float
    c: float
    d: float

    def __post_init__(self) -> None:
        if not self.a <= self.b <= self.c <= self.d:
            raise ValueError("Une fonction trapezoidale exige a <= b <= c <= d.")
        if self.a == self.d:
            raise ValueError("Une fonction trapezoidale exige a < d.")

    @property
    def parameters(self) -> tuple[float, ...]:
        return (self.a, self.b, self.c, self.d)

    def __call__(self, value: float) -> float:
        x = float(value)
        if x < self.a or x > self.d:
            return 0.0
        if self.b <= x <= self.c:
            return 1.0
        if self.a <= x < self.b:
            if self.a == self.b:
                return 1.0
            return _clip01((x - self.a) / (self.b - self.a))
        if self.c < x <= self.d:
            if self.c == self.d:
                return 1.0
            return _clip01((self.d - x) / (self.d - self.c))
        return 0.0


def triangular(value: float, a: float, b: float, c: float) -> float:
    """Evaluate a triangular membership function."""

    return TriangularMembershipFunction(a=a, b=b, c=c)(value)


def trapezoidal(value: float, a: float, b: float, c: float, d: float) -> float:
    """Evaluate a trapezoidal membership function."""

    return TrapezoidalMembershipFunction(a=a, b=b, c=c, d=d)(value)


def evaluate_membership(function: MembershipFunction, values: Sequence[float]) -> list[float]:
    """Evaluate one membership function over several crisp values."""

    return [function(float(value)) for value in values]


def _clip01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
