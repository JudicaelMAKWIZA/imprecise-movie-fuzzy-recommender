"""Gestion des donnees MovieLens pour le projet FuzzyRec.

Le paquet `data_manager` est la couche officielle de chargement et de
pretraitement des fichiers bruts `ml-latest-small`. Les fichiers dans
`data/movie/` sont consideres comme immuables ; toute donnee derivee doit etre
produite dans `data/processed/`.
"""

from .loader import DataLoadingError, DataValidationError, MovieLensLoader
from .preprocessor import MovieLensPreprocessor

__all__ = [
    "DataLoadingError",
    "DataValidationError",
    "MovieLensLoader",
    "MovieLensPreprocessor",
]
