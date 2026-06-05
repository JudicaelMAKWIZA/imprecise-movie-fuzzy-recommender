"""Factories partagees pour construire le pipeline de recommandation V1.

Ce module evite de dupliquer dans la CLI et la GUI les memes operations :
chargement MovieLens, pretraitement, construction du repository, creation du
profil utilisateur et assemblage du moteur Mamdani.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pandas import DataFrame

from data_manager.loader import MovieLensLoader
from data_manager.movie_repository import MovieRepository
from data_manager.preprocessor import MovieLensPreprocessor
from fuzzy.config_loader import load_fuzzy_system_config
from fuzzy.defuzzification import Defuzzifier
from fuzzy.fuzzifier import Fuzzifier
from fuzzy.inference_engine import MamdaniInferenceEngine
from recommender.fuzzy_recommender import FuzzyRecommender
from recommender.user_profile import (
    GenrePreference,
    GenrePreferenceValue,
    IntervalGenrePreference,
    LinguisticGenrePreference,
    UserProfile,
)


@dataclass(frozen=True)
class RecommenderContext:
    """Contexte complet necessaire aux interfaces.

    Attributes:
        raw_data: Tables MovieLens brutes et validees.
        features: Table de caracteristiques derivees.
        recommender: Facade de recommandation floue assemblee.
    """

    raw_data: dict[str, DataFrame]
    features: DataFrame
    recommender: FuzzyRecommender


def load_recommender_context(
    raw_dir: Path | str = Path("data/movie"),
    config_path: Path | str = Path("config/fuzzy_config.yaml"),
) -> RecommenderContext:
    """Charger MovieLens et construire le pipeline V1 complet."""

    raw_data = MovieLensLoader(raw_dir=raw_dir).load_all()
    preprocessor = MovieLensPreprocessor()
    features = preprocessor.build_movie_features(raw_data)
    recommender = build_recommender_from_features(features, config_path=config_path)
    return RecommenderContext(raw_data=raw_data, features=features, recommender=recommender)


def build_recommender_from_features(
    features: DataFrame,
    config_path: Path | str = Path("config/fuzzy_config.yaml"),
) -> FuzzyRecommender:
    """Assembler la facade de recommandation depuis les features films."""

    fuzzy_config = load_fuzzy_system_config(config_path)
    repository = MovieRepository.from_dataframe(features)
    return FuzzyRecommender(
        repository=repository,
        fuzzifier=Fuzzifier(variables=fuzzy_config.input_variables),
        inference_engine=MamdaniInferenceEngine(fuzzy_config.rule_base),
        defuzzifier=Defuzzifier(method=fuzzy_config.defuzzification_method),
        output_variable=fuzzy_config.output_variables["recommendation_score"],
    )


def build_profile(
    *,
    user_id: int,
    raw_data: dict[str, DataFrame],
    explicit_preferences: str | None = None,
) -> UserProfile:
    """Construire un profil depuis une saisie explicite ou l'historique.

    Si `explicit_preferences` est fourni, il prime sur l'historique MovieLens.
    Sinon, la V1 derive une intensite de preference par genre depuis la note
    moyenne de l'utilisateur sur ce genre, normalisee dans `[0, 1]`.
    """

    profile = UserProfile(user_id=user_id)
    if explicit_preferences:
        for genre, value in parse_genre_preferences(explicit_preferences).items():
            profile.set_genre_preference(GenrePreference(genre=genre, value=value))
        return profile

    ratings = raw_data["ratings"]
    movies = raw_data["movies"]
    user_ratings = ratings.loc[ratings["userId"] == user_id, ["movieId", "rating"]]
    if user_ratings.empty:
        return profile

    merged = user_ratings.merge(movies[["movieId", "genres"]], on="movieId", how="left")
    by_genre: dict[str, list[tuple[float, float]]] = {}
    preprocessor = MovieLensPreprocessor()
    for row in merged.itertuples(index=False):
        genres = preprocessor.split_genres(row.genres)
        if not genres:
            continue
        weight = 1.0 / len(genres)
        for genre in genres:
            by_genre.setdefault(genre, []).append((float(row.rating), weight))

    for genre, weighted_ratings in by_genre.items():
        total_weight = sum(weight for _, weight in weighted_ratings)
        average_rating = sum(rating * weight for rating, weight in weighted_ratings) / total_weight
        value = max(0.0, min(1.0, (average_rating - 0.5) / 4.5))
        profile.set_genre_preference(GenrePreference(genre=genre, value=value))
    return profile


def parse_genre_preferences(raw_preferences: str) -> dict[str, GenrePreferenceValue]:
    """Parser `Genre=valeur`, `Genre=terme` ou `Genre=borne:borne`."""

    preferences: dict[str, GenrePreferenceValue] = {}
    for item in raw_preferences.split(","):
        stripped = item.strip()
        if not stripped:
            continue
        if "=" not in stripped:
            raise ValueError(f"Preference invalide: {stripped}. Format attendu: Genre=0.8 ou Genre=forte")
        genre, raw_value = stripped.split("=", 1)
        genre = genre.strip()
        if not genre:
            raise ValueError("Le genre ne peut pas etre vide.")
        value = _parse_preference_value(raw_value)
        if isinstance(value, float) and not 0.0 <= value <= 1.0:
            raise ValueError(f"La preference de {genre} doit etre dans [0, 1].")
        preferences[genre] = value
    if not preferences:
        raise ValueError("Aucune preference de genre valide n'a ete fournie.")
    return preferences


def _parse_preference_value(raw_value: str) -> GenrePreferenceValue:
    value = raw_value.strip()
    if ".." in value:
        lower, upper = value.split("..", 1)
        return IntervalGenrePreference(lower=float(lower), upper=float(upper))
    try:
        return float(value)
    except ValueError:
        return LinguisticGenrePreference(term=value.casefold().replace(" ", "_").replace("-", "_"))
