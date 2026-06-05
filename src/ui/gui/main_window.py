"""Fenetre principale Tkinter du demonstrateur FuzzyRec."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from recommender.explanation_engine import ExplanationEngine
from recommender.pipeline_factory import RecommenderContext, build_profile, load_recommender_context

from .explanation_view import ExplanationView
from .preferences_editor import PreferencesEditor
from .recommendations_view import RecommendationsView


class MainWindow:
    """Conteneur principal de l'application graphique.

    La GUI reste volontairement legere : elle sert de support de demonstration
    pour charger MovieLens, saisir un profil, produire un Top-N et afficher les
    explications Mamdani associees.
    """

    def __init__(self, raw_dir: Path | str = Path("data/movie")) -> None:
        self.raw_dir = Path(raw_dir)
        self.context: RecommenderContext | None = None
        self.profile = None
        self.explanation_engine = ExplanationEngine()
        self.root: tk.Tk | None = None
        self.user_id_var: tk.StringVar | None = None
        self.top_n_var: tk.StringVar | None = None
        self.status_var: tk.StringVar | None = None
        self.preferences_editor: PreferencesEditor | None = None
        self.recommendations_view: RecommendationsView | None = None
        self.explanation_view: ExplanationView | None = None

    def show(self) -> None:
        """Afficher la fenetre principale et lancer la boucle Tkinter."""

        self.root = tk.Tk()
        self.root.title("FuzzyRec - Mamdani V1")
        self.root.geometry("920x720")
        self._build_widgets(self.root)
        self.root.mainloop()

    def _build_widgets(self, root: tk.Tk) -> None:
        self.user_id_var = tk.StringVar(value="1")
        self.top_n_var = tk.StringVar(value="10")
        self.status_var = tk.StringVar(value="Catalogue non charge")

        container = ttk.Frame(root, padding=12)
        container.grid(row=0, column=0, sticky="nsew")
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        controls = ttk.Frame(container)
        controls.grid(row=0, column=0, sticky="ew")
        controls.columnconfigure(5, weight=1)

        ttk.Button(controls, text="Charger catalogue", command=self.load_catalog).grid(row=0, column=0, padx=(0, 8))
        ttk.Label(controls, text="User ID").grid(row=0, column=1, sticky="w")
        ttk.Entry(controls, textvariable=self.user_id_var, width=8).grid(row=0, column=2, padx=(4, 12))
        ttk.Label(controls, text="Top-N").grid(row=0, column=3, sticky="w")
        ttk.Entry(controls, textvariable=self.top_n_var, width=6).grid(row=0, column=4, padx=(4, 12))
        ttk.Button(controls, text="Recommander", command=self.run_recommendations).grid(row=0, column=5, sticky="w")

        self.preferences_editor = PreferencesEditor(container)
        self.preferences_editor.render().grid(row=1, column=0, sticky="ew", pady=(12, 8))

        self.recommendations_view = RecommendationsView(container)
        self.recommendations_view.render().grid(row=2, column=0, sticky="nsew", pady=(4, 8))
        self.recommendations_view.tree.bind("<<TreeviewSelect>>", self._on_recommendation_selected)

        self.explanation_view = ExplanationView(container)
        self.explanation_view.render().grid(row=3, column=0, sticky="nsew")

        ttk.Label(container, textvariable=self.status_var).grid(row=4, column=0, sticky="w", pady=(8, 0))
        container.rowconfigure(2, weight=2)
        container.rowconfigure(3, weight=1)
        container.columnconfigure(0, weight=1)

    def load_catalog(self) -> None:
        """Charger les donnees MovieLens et construire le pipeline."""

        try:
            self.context = load_recommender_context(self.raw_dir)
        except Exception as exc:  # pragma: no cover - branche dependante du poste
            messagebox.showerror("Chargement impossible", str(exc))
            self._set_status(f"Erreur de chargement: {exc}")
            return
        self._set_status(f"Catalogue charge: {len(self.context.recommender.repository.movies)} films")

    def run_recommendations(self) -> None:
        """Produire le Top-N et afficher la premiere explication."""

        if self.context is None:
            self.load_catalog()
        if self.context is None:
            return

        try:
            user_id = int(self._value(self.user_id_var, "1"))
            top_n = int(self._value(self.top_n_var, "10"))
            preferences_text = self.preferences_editor.get_preferences_text() if self.preferences_editor else ""
            explicit_preferences = preferences_text or None
            self.profile = build_profile(
                user_id=user_id,
                raw_data=self.context.raw_data,
                explicit_preferences=explicit_preferences,
            )
            recommendations = self.context.recommender.recommend(self.profile, top_n=top_n)
        except Exception as exc:
            messagebox.showerror("Recommandation impossible", str(exc))
            self._set_status(f"Erreur de recommandation: {exc}")
            return

        if self.recommendations_view is not None:
            self.recommendations_view.set_recommendations(recommendations)
        self._set_status(f"{len(recommendations)} recommandations produites")
        if recommendations:
            self._show_explanation(recommendations[0])

    def _on_recommendation_selected(self, _event: tk.Event) -> None:
        if self.recommendations_view is None:
            return
        recommendation = self.recommendations_view.selected_recommendation()
        if recommendation is not None:
            self._show_explanation(recommendation)

    def _show_explanation(self, recommendation: object) -> None:
        if self.profile is None or self.explanation_view is None:
            return
        explanation = self.explanation_engine.explain_recommendation(self.profile, recommendation)
        self.explanation_view.set_text(explanation.text or "")

    def _set_status(self, message: str) -> None:
        if self.status_var is not None:
            self.status_var.set(message)

    @staticmethod
    def _value(variable: tk.StringVar | None, default: str) -> str:
        return variable.get().strip() if variable is not None and variable.get().strip() else default
