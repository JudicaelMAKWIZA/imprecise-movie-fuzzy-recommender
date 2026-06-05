"""Couche recommandation et explicabilite."""

from .explanation_engine import ExplanationEngine, RecommendationExplanation
from .fuzzy_recommender import FuzzyRecommender, Recommendation
from .pipeline_factory import (
    RecommenderContext,
    build_profile,
    build_recommender_from_features,
    load_recommender_context,
    parse_genre_preferences,
)
from .user_profile import GenrePreference, IntervalGenrePreference, LinguisticGenrePreference, UserProfile

__all__ = [
    "ExplanationEngine",
    "FuzzyRecommender",
    "GenrePreference",
    "IntervalGenrePreference",
    "LinguisticGenrePreference",
    "Recommendation",
    "RecommendationExplanation",
    "RecommenderContext",
    "UserProfile",
    "build_profile",
    "build_recommender_from_features",
    "load_recommender_context",
    "parse_genre_preferences",
]
