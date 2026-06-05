"""Tests des variables linguistiques V1."""

import pytest

from fuzzy.linguistic_variables import (
    build_average_rating_variable,
    build_default_v1_variables,
    build_default_v1_system_variables,
    build_genre_preference_variable,
    build_popularity_variable,
    build_recommendation_score_variable,
)


def test_default_v1_variables_are_available() -> None:
    """Les trois variables officielles de la V1 sont construites."""

    variables = build_default_v1_variables()

    assert set(variables) == {"genre_preference", "average_rating", "popularity"}
    assert set(variables["genre_preference"].fuzzy_sets) == {"faible", "moyenne", "forte"}
    assert "excellente" in variables["average_rating"].fuzzy_sets
    assert "tres_populaire" in variables["popularity"].fuzzy_sets


def test_default_v1_system_variables_include_output() -> None:
    """Le registre systeme contient aussi la sortie recommendation_score."""

    variables = build_default_v1_system_variables()

    assert set(variables) == {"genre_preference", "average_rating", "popularity", "recommendation_score"}
    assert set(variables["recommendation_score"].fuzzy_sets) == {
        "tres_faible",
        "faible",
        "moyen",
        "fort",
        "tres_fort",
    }


def test_genre_preference_fuzzification() -> None:
    """Une preference forte active le terme `forte`."""

    variable = build_genre_preference_variable()
    degrees = variable.fuzzify(0.85)

    assert degrees["forte"] == 1.0
    assert degrees["faible"] == 0.0


def test_average_rating_fuzzification() -> None:
    """Une note moyenne elevee active le terme `excellente`."""

    variable = build_average_rating_variable()
    degrees = variable.fuzzify(4.75)

    assert degrees["excellente"] == 1.0
    assert degrees["mauvaise"] == 0.0


def test_popularity_fuzzification() -> None:
    """La popularite moyenne active correctement le terme modere."""

    variable = build_popularity_variable()
    degrees = variable.fuzzify(60.0)

    assert degrees["modere"] == 1.0
    assert degrees["confidentiel"] == 0.0


def test_recommendation_score_variable_fuzzification() -> None:
    """La sortie linguistique est disponible pour les futures etapes Mamdani."""

    variable = build_recommendation_score_variable()
    degrees = variable.fuzzify(0.95)

    assert degrees["tres_fort"] == 1.0
    assert degrees["tres_faible"] == 0.0


def test_linguistic_variable_rejects_values_outside_universe() -> None:
    """Les valeurs hors univers sont refusees pour eviter des entrees ambiguës."""

    variable = build_genre_preference_variable()

    with pytest.raises(ValueError):
        variable.fuzzify(1.2)
