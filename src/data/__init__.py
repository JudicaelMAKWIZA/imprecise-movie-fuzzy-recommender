"""Acces et preparation des donnees MovieLens.

`data_manager` est le paquet officiel pour le chargement et le pretraitement.
Ce paquet garde les exports historiques du squelette.
"""

from .loader import DataLoadingError, DataValidationError, MovieLensLoader
from .movie_repository import MovieRepository
from .preprocessor import MovieLensPreprocessor
from .schemas import LinkRecord, MovieFeatures, MovieRecord, RatingRecord, TagRecord

__all__ = [
    "LinkRecord",
    "DataLoadingError",
    "DataValidationError",
    "MovieFeatures",
    "MovieLensLoader",
    "MovieLensPreprocessor",
    "MovieRecord",
    "MovieRepository",
    "RatingRecord",
    "TagRecord",
]
