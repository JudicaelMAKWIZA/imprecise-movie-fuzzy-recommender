"""Couche recommandation et explicabilite."""

from .explanation_engine import ExplanationEngine, RecommendationExplanation
from .fuzzy_recommender import FuzzyRecommender, Recommendation
from .user_profile import GenrePreference, UserProfile

__all__ = [
    "ExplanationEngine",
    "FuzzyRecommender",
    "GenrePreference",
    "Recommendation",
    "RecommendationExplanation",
    "UserProfile",
]
