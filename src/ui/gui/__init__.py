"""Squelette de l'interface graphique.

La GUI reste volontairement non implementee. Les classes de ce paquet servent a
reserver les composants prevus par les specifications.
"""

from .explanation_view import ExplanationView
from .main_window import MainWindow
from .preferences_editor import PreferencesEditor
from .recommendations_view import RecommendationsView

__all__ = [
    "ExplanationView",
    "MainWindow",
    "PreferencesEditor",
    "RecommendationsView",
]
