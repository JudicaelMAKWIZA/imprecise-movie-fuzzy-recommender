"""Vue graphique des recommandations Top-N."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from recommender.fuzzy_recommender import Recommendation
from .scroll_bindings import enable_mousewheel_scroll


class RecommendationsView:
    """Composant Tkinter pour afficher les films recommandes."""

    def __init__(self, parent: tk.Widget) -> None:
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.tree = ttk.Treeview(
            self.frame,
            columns=("rank", "movie_id", "score", "title"),
            show="headings",
            height=10,
        )
        self.recommendations: list[Recommendation] = []

    def render(self) -> ttk.Frame:
        """Afficher la table des recommandations."""

        headings = {
            "rank": "#",
            "movie_id": "MovieId",
            "score": "Score",
            "title": "Titre",
        }
        widths = {"rank": 48, "movie_id": 80, "score": 80, "title": 420}
        for column, label in headings.items():
            self.tree.heading(column, text=label)
            self.tree.column(column, width=widths[column], anchor="w", stretch=column == "title")

        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        horizontal_scrollbar = ttk.Scrollbar(self.frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar.set, xscrollcommand=horizontal_scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")
        # Activer le défilement par molette/touchpad sur la table
        try:
            enable_mousewheel_scroll(self.tree)
        except Exception:
            pass
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        return self.frame

    def set_recommendations(self, recommendations: list[Recommendation]) -> None:
        """Remplacer le contenu de la table."""

        self.recommendations = recommendations
        for item in self.tree.get_children():
            self.tree.delete(item)
        for rank, recommendation in enumerate(recommendations, start=1):
            score = "indetermine" if recommendation.score is None else f"{recommendation.score:.4f}"
            self.tree.insert(
                "",
                "end",
                iid=str(rank - 1),
                values=(rank, recommendation.movie.movie_id, score, recommendation.movie.title),
            )

    def selected_recommendation(self) -> Recommendation | None:
        """Retourner la recommandation selectionnee, si elle existe."""

        selection = self.tree.selection()
        if not selection:
            return None
        index = int(selection[0])
        if index < 0 or index >= len(self.recommendations):
            return None
        return self.recommendations[index]
