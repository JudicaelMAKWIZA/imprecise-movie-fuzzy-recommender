"""Compatibilite avec l'ancien paquet `data`.

Le paquet officiel de pretraitement est `data_manager`.
"""

from data_manager.preprocessor import MovieLensPreprocessor

__all__ = ["MovieLensPreprocessor"]
