"""Couche recommandation et explicabilite."""

from .explanation_engine import ExplanationEngine, RecommendationExplanation
from .fuzzy_recommender import FuzzyRecommender, Recommendation
from .pipeline_factory import (
    RecommenderContext,
    build_profile,
    build_recommender_from_features,
    linguistic_level_to_value,
    load_recommender_context,
    parse_genre_preferences,
)
from .user_profile import GenrePreference, UserProfile

__all__ = [
    "ExplanationEngine",
    "FuzzyRecommender",
    "GenrePreference",
    "Recommendation",
    "RecommendationExplanation",
    "RecommenderContext",
    "UserProfile",
    "build_profile",
    "build_recommender_from_features",
    "linguistic_level_to_value",
    "load_recommender_context",
    "parse_genre_preferences",
]
