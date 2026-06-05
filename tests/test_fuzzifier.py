"""Tests du mecanisme de fuzzification."""

import pytest

from fuzzy.fuzzifier import Fuzzifier


def test_fuzzifier_default_v1_fuzzifies_one_value() -> None:
    """Le fuzzifier V1 expose les variables officielles."""

    fuzzifier = Fuzzifier.default_v1()
    degrees = fuzzifier.fuzzify_value("average_rating", 4.75)

    assert degrees["excellente"] == 1.0


def test_fuzzifier_fuzzifies_user_and_movie_inputs() -> None:
    """Les entrees utilisateur et film sont converties ensemble."""

    fuzzifier = Fuzzifier.default_v1()
    result = fuzzifier.fuzzify_inputs(
        user_inputs={"genre_preference": 0.85},
        movie_inputs={"average_rating": 4.75, "popularity": 300.0},
    )

    assert result["genre_preference"]["forte"] == 1.0
    assert result["average_rating"]["excellente"] == 1.0
    assert result["popularity"]["tres_populaire"] == 1.0


def test_fuzzifier_rejects_unknown_variable_for_direct_call() -> None:
    """Une variable inconnue explicite doit produire une erreur claire."""

    fuzzifier = Fuzzifier.default_v1()

    with pytest.raises(KeyError):
        fuzzifier.fuzzify_value("unknown", 1.0)
