"""Couche recommandation et explicabilite."""

from .explanation_engine import ExplanationEngine, RecommendationExplanation
from .fuzzy_recommender import FuzzyRecommender, PrefilterEmptyError, PrefilterResult, Recommendation
from .pipeline_factory import (
    RecommenderContext,
    build_profile,
    build_recommender_from_features,
    load_recommender_context,
    parse_genre_preferences,
    parse_value,
)
from .user_profile import GenrePreference, IntervalGenrePreference, LinguisticGenrePreference, UserProfile

__all__ = [
    "ExplanationEngine",
    "FuzzyRecommender",
    "GenrePreference",
    "IntervalGenrePreference",
    "LinguisticGenrePreference",
    "PrefilterEmptyError",
    "PrefilterResult",
    "Recommendation",
    "RecommendationExplanation",
    "RecommenderContext",
    "UserProfile",
    "build_profile",
    "build_recommender_from_features",
    "load_recommender_context",
    "parse_genre_preferences",
    "parse_value",
]
