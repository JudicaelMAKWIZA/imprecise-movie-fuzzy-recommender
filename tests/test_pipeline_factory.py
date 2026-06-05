"""Tests des factories partagees du pipeline V1."""

import pandas as pd
import pytest

from recommender.pipeline_factory import build_profile, parse_genre_preferences
from recommender.user_profile import LinguisticGenrePreference


def test_parse_genre_preferences() -> None:
    """Les preferences CLI/GUI sont parsees dans un format commun."""

    assert parse_genre_preferences("Sci-Fi=0.9, Action=0.7") == {"Sci-Fi": 0.9, "Action": 0.7}
    parsed = parse_genre_preferences("Sci-Fi=forte")
    assert isinstance(parsed["Sci-Fi"], LinguisticGenrePreference)
    assert parsed["Sci-Fi"].term == "forte"

    with pytest.raises(ValueError):
        parse_genre_preferences("Sci-Fi=1.5")


def test_build_profile_derives_genre_preferences_from_user_history() -> None:
    """Le profil V1 peut etre derive depuis les notes MovieLens."""

    raw_data = {
        "ratings": pd.DataFrame(
            [
                {"userId": 1, "movieId": 1, "rating": 5.0},
                {"userId": 1, "movieId": 2, "rating": 3.0},
                {"userId": 2, "movieId": 3, "rating": 1.0},
            ]
        ),
        "movies": pd.DataFrame(
            [
                {"movieId": 1, "genres": "Sci-Fi|Action"},
                {"movieId": 2, "genres": "Drama"},
                {"movieId": 3, "genres": "Comedy"},
            ]
        ),
    }

    profile = build_profile(user_id=1, raw_data=raw_data)

    assert profile.genre_preferences["Sci-Fi"].value == pytest.approx(1.0)
    assert profile.genre_preferences["Action"].value == pytest.approx(1.0)
    assert profile.genre_preferences["Drama"].value == pytest.approx((3.0 - 0.5) / 4.5)


def test_build_profile_weights_multi_genre_contributions() -> None:
    """Un film multi-genres contribue partiellement a chaque genre."""

    raw_data = {
        "ratings": pd.DataFrame(
            [
                {"userId": 1, "movieId": 1, "rating": 5.0},
                {"userId": 1, "movieId": 2, "rating": 1.0},
            ]
        ),
        "movies": pd.DataFrame(
            [
                {"movieId": 1, "genres": "Sci-Fi|Action"},
                {"movieId": 2, "genres": "Sci-Fi"},
            ]
        ),
    }

    profile = build_profile(user_id=1, raw_data=raw_data)

    weighted_average = ((5.0 * 0.5) + (1.0 * 1.0)) / 1.5
    assert profile.genre_preferences["Sci-Fi"].value == pytest.approx((weighted_average - 0.5) / 4.5)
    assert profile.genre_preferences["Action"].value == pytest.approx(1.0)


def test_build_profile_explicit_preferences_override_history() -> None:
    """Une saisie explicite prime sur l'historique."""

    raw_data = {
        "ratings": pd.DataFrame([{"userId": 1, "movieId": 1, "rating": 1.0}]),
        "movies": pd.DataFrame([{"movieId": 1, "genres": "Comedy"}]),
    }

    profile = build_profile(user_id=1, raw_data=raw_data, explicit_preferences="Sci-Fi=forte")

    assert list(profile.genre_preferences) == ["Sci-Fi"]
    assert isinstance(profile.genre_preferences["Sci-Fi"].value, LinguisticGenrePreference)
