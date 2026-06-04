"""Tests de squelette pour les fonctions d'appartenance."""

import pytest

from fuzzy import membership


def test_membership_functions_are_declared() -> None:
    """Les fonctions attendues existent mais ne sont pas encore implementees."""

    assert callable(membership.triangular)
    assert callable(membership.trapezoidal)
    assert callable(membership.gaussian)
    assert callable(membership.sigmoid)


def test_triangular_is_explicitly_todo() -> None:
    """Le squelette ne doit pas encore contenir la formule triangulaire."""

    with pytest.raises(NotImplementedError):
        membership.triangular(0.5, 0.0, 0.5, 1.0)
