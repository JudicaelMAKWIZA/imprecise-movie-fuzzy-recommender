"""Tests des ensembles flous."""

import pytest

from fuzzy.fuzzy_set import FuzzySet
from fuzzy.membership_functions import TriangularMembershipFunction


def test_fuzzy_set_membership_and_call_shortcut() -> None:
    """Un FuzzySet delegue correctement a sa fonction d'appartenance."""

    fuzzy_set = FuzzySet("moyenne", TriangularMembershipFunction(0.0, 0.5, 1.0))

    assert fuzzy_set.membership(0.5) == 1.0
    assert fuzzy_set(0.25) == pytest.approx(0.5)


def test_fuzzy_set_sampling_and_alpha_cut() -> None:
    """L'echantillonnage et l'alpha-cut s'appuient sur les degres calcules."""

    fuzzy_set = FuzzySet("moyenne", TriangularMembershipFunction(0.0, 0.5, 1.0))
    universe = [0.0, 0.25, 0.5, 0.75, 1.0]

    assert fuzzy_set.sample(universe) == [
        (0.0, 0.0),
        (0.25, 0.5),
        (0.5, 1.0),
        (0.75, 0.5),
        (1.0, 0.0),
    ]
    assert fuzzy_set.alpha_cut(universe, 0.5) == [0.25, 0.5, 0.75]


def test_alpha_cut_rejects_invalid_alpha() -> None:
    """Le seuil alpha doit rester dans [0, 1]."""

    fuzzy_set = FuzzySet("moyenne", TriangularMembershipFunction(0.0, 0.5, 1.0))
    with pytest.raises(ValueError):
        fuzzy_set.alpha_cut([0.5], 1.5)
