"""Acces et preparation des donnees MovieLens.

Les donnees brutes situees dans `data/movie/` ne doivent jamais etre modifiees.
Les donnees derivees devront etre ecrites dans `data/processed/`.
"""

from .loader import MovieLensLoader
from .movie_repository import MovieRepository
from .preprocessor import MovieLensPreprocessor
from .schemas import LinkRecord, MovieFeatures, MovieRecord, RatingRecord, TagRecord

__all__ = [
    "LinkRecord",
    "MovieFeatures",
    "MovieLensLoader",
    "MovieLensPreprocessor",
    "MovieRecord",
    "MovieRepository",
    "RatingRecord",
    "TagRecord",
]
