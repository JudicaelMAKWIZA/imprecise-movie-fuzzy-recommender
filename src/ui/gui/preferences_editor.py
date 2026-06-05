"""Editeur graphique des preferences floues utilisateur."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from recommender.pipeline_factory import parse_genre_preferences
from recommender.user_profile import GenrePreferenceValue


class PreferencesEditor:
    """Composant Tkinter pour saisir les preferences de genres.

    La V1 utilise une zone texte compacte au format deja supporte par la CLI :
    `Sci-Fi=forte,Action=0.7`. Cela suffit pour une demonstration de soutenance
    sans ajouter de dependance graphique lourde.
    """

    def __init__(self, parent: tk.Widget, default_text: str = "Sci-Fi=forte,Action=0.7") -> None:
        self.parent = parent
        self.preference_text = tk.StringVar(value=default_text)
        self.frame = ttk.Frame(parent)

    def render(self) -> ttk.Frame:
        """Afficher les controles de preferences et retourner le conteneur."""

        ttk.Label(self.frame, text="Preferences genres").grid(row=0, column=0, sticky="w")
        entry = ttk.Entry(self.frame, textvariable=self.preference_text, width=42)
        entry.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        self.frame.columnconfigure(0, weight=1)
        return self.frame

    def get_preferences_text(self) -> str:
        """Retourner la saisie brute des preferences."""

        return self.preference_text.get().strip()

    def get_preferences(self) -> dict[str, GenrePreferenceValue]:
        """Parser la saisie en preferences crisp ou linguistiques."""

        return parse_genre_preferences(self.get_preferences_text())
