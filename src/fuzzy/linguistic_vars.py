"""Compatibilite pour les variables linguistiques.

Le module officiel est `fuzzy.linguistic_variables`. Les anciens imports restent
valides pour ne pas casser le reste du squelette.
"""

from .linguistic_variables import (
    LinguisticTerm,
    LinguisticVariable,
    build_average_rating_variable,
    build_default_v1_variables,
    build_genre_preference_variable,
    build_popularity_variable,
)

__all__ = [
    "LinguisticTerm",
    "LinguisticVariable",
    "build_average_rating_variable",
    "build_default_v1_variables",
    "build_genre_preference_variable",
    "build_popularity_variable",
]
