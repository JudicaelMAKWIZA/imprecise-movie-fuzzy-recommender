"""Interface graphique Tkinter de demonstration du systeme FuzzyRec."""

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
