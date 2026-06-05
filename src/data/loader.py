"""Compatibilite avec l'ancien paquet `data`.

Le paquet officiel de gestion des donnees est `data_manager`.
"""

from data_manager.loader import DataLoadingError, DataValidationError, MovieLensLoader

__all__ = ["DataLoadingError", "DataValidationError", "MovieLensLoader"]
