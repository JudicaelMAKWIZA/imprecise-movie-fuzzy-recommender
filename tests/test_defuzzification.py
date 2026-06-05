"""Tests de defuzzification Mamdani."""

import pytest

from fuzzy.defuzzification import Defuzzifier


def test_centroid_on_simple_triangle_samples() -> None:
    """Le centroide discret d'un triangle symetrique est au centre."""

    defuzzifier = Defuzzifier()

    assert defuzzifier.centroid([0.0, 0.5, 1.0], [0.0, 1.0, 0.0]) == pytest.approx(0.5)


def test_centroid_returns_empty_output_value_for_zero_area() -> None:
    """Une surface nulle retourne la valeur de sortie vide."""

    defuzzifier = Defuzzifier(empty_output_value=0.0)

    assert defuzzifier.centroid([0.0, 1.0], [0.0, 0.0]) == 0.0


def test_defuzzify_recommendation_score_terms() -> None:
    """Un terme tres fort produit un score crisp eleve dans [0, 1]."""

    score = Defuzzifier(resolution=501).defuzzify({"tres_fort": 1.0})

    assert 0.85 <= score <= 0.95


def test_defuzzify_rejects_unknown_output_term() -> None:
    """Les termes de sortie doivent appartenir a recommendation_score."""

    with pytest.raises(ValueError):
        Defuzzifier().defuzzify({"parfait": 0.8})


def test_defuzzify_rejects_unknown_method() -> None:
    """La V1 supporte uniquement le centroide."""

    with pytest.raises(ValueError):
        Defuzzifier(method="bisector").defuzzify({"fort": 0.5})
