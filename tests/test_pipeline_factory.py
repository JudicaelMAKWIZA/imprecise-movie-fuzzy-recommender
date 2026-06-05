"""Tests des factories partagees du pipeline V1."""

import pandas as pd
import pytest

from recommender.pipeline_factory import build_profile, linguistic_level_to_value, parse_genre_preferences


def test_parse_genre_preferences() -> None:
    """Les preferences CLI/GUI sont parsees dans un format commun."""

    assert parse_genre_preferences("Sci-Fi=0.9, Action=0.7") == {"Sci-Fi": 0.9, "Action": 0.7}

    with pytest.raises(ValueError):
        parse_genre_preferences("Sci-Fi=1.5")


def test_linguistic_level_to_value() -> None:
    """Les niveaux linguistiques courants sont convertis en valeurs crisp."""

    assert linguistic_level_to_value("beaucoup") == pytest.approx(0.8)
    assert linguistic_level_to_value("forte") == pytest.approx(0.9)


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


def test_build_profile_explicit_preferences_override_history() -> None:
    """Une saisie explicite prime sur l'historique."""

    raw_data = {
        "ratings": pd.DataFrame([{"userId": 1, "movieId": 1, "rating": 1.0}]),
        "movies": pd.DataFrame([{"movieId": 1, "genres": "Comedy"}]),
    }

    profile = build_profile(user_id=1, raw_data=raw_data, explicit_preferences="Sci-Fi=0.9")

    assert list(profile.genre_preferences) == ["Sci-Fi"]
    assert profile.genre_preferences["Sci-Fi"].value == pytest.approx(0.9)
