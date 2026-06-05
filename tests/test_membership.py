"""Tests des fonctions d'appartenance from scratch."""

import pytest

from fuzzy import membership
from fuzzy.membership_functions import TrapezoidalMembershipFunction, TriangularMembershipFunction


def test_membership_functions_are_declared() -> None:
    """Les fonctions attendues existent dans le module de compatibilite."""

    assert callable(membership.triangular)
    assert callable(membership.trapezoidal)
    assert not hasattr(membership, "gaussian")
    assert not hasattr(membership, "sigmoid")


def test_triangular_membership_values() -> None:
    """La fonction triangulaire respecte les bornes, le sommet et les pentes."""

    triangle = TriangularMembershipFunction(0.0, 0.5, 1.0)

    assert triangle(0.0) == 0.0
    assert triangle(0.25) == pytest.approx(0.5)
    assert triangle(0.5) == 1.0
    assert triangle(0.75) == pytest.approx(0.5)
    assert triangle(1.0) == 0.0


def test_trapezoidal_membership_values_with_shoulders() -> None:
    """La fonction trapezoidale supporte les epaules gauche et droite."""

    left_shoulder = TrapezoidalMembershipFunction(0.0, 0.0, 10.0, 30.0)
    right_shoulder = TrapezoidalMembershipFunction(200.0, 280.0, 350.0, 350.0)

    assert left_shoulder(0.0) == 1.0
    assert left_shoulder(10.0) == 1.0
    assert left_shoulder(20.0) == pytest.approx(0.5)
    assert left_shoulder(31.0) == 0.0
    assert right_shoulder(240.0) == pytest.approx(0.5)
    assert right_shoulder(350.0) == 1.0


def test_function_helpers_delegate_to_classes() -> None:
    """Les helpers historiques retournent les memes valeurs que les classes."""

    assert membership.triangular(0.25, 0.0, 0.5, 1.0) == pytest.approx(0.5)
    assert membership.trapezoidal(20.0, 0.0, 0.0, 10.0, 30.0) == pytest.approx(0.5)


def test_invalid_membership_parameters_are_rejected() -> None:
    """Les parametres incoherents sont refuses explicitement."""

    with pytest.raises(ValueError):
        TriangularMembershipFunction(0.0, 0.0, 1.0)
    with pytest.raises(ValueError):
        TrapezoidalMembershipFunction(1.0, 0.0, 0.5, 2.0)
