"""Fenetre principale Tkinter du demonstrateur FuzzyRec."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from data_manager.preprocessor import MovieLensPreprocessor
from recommender.explanation_engine import ExplanationEngine
from recommender.fuzzy_recommender import PrefilterEmptyError
from recommender.pipeline_factory import RecommenderContext, build_profile, load_recommender_context

from .explanation_view import ExplanationView
from .membership_view import MembershipView
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
        self.dataset_path_var: tk.StringVar | None = None
        self.status_var: tk.StringVar | None = None
        self._logo_image: tk.PhotoImage | None = None
        self.preferences_editor: PreferencesEditor | None = None
        self.membership_view: MembershipView | None = None
        self.recommendations_view: RecommendationsView | None = None
        self.explanation_view: ExplanationView | None = None
        self.controls_to_lock: list[tk.Widget] = []
        self.load_button: ttk.Button | None = None
        self.dataset_button: ttk.Button | None = None

    def show(self) -> None:
        """Afficher la fenetre principale et lancer la boucle Tkinter."""

        self.root = tk.Tk()
        self.root.title("FuzzyRec - Mamdani V1")
        self.root.geometry("1040x760")
        self.root.minsize(760, 560)
        self._configure_style()
        self._build_widgets(self.root)
        self.root.after(0, self.load_catalog)
        self.root.mainloop()

    def _build_widgets(self, root: tk.Tk) -> None:
        self.user_id_var = tk.StringVar(value="1")
        self.top_n_var = tk.StringVar(value="10")
        self.dataset_path_var = tk.StringVar(value=str(self.raw_dir))
        self.status_var = tk.StringVar(value="Catalogue non charge")

        self._configure_style()
        container = ttk.Frame(root, padding=10, style="App.TFrame")
        container.grid(row=0, column=0, sticky="nsew")
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        header = ttk.Frame(container, style="App.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        # Reserve three columns: 0=logo, 1=title, 2=subtitle (subtitle expands)
        header.columnconfigure(2, weight=1)

        # Charger le logo si present (à gauche) et supprimer tout encadrement visible
        try:
            logo_path = Path(__file__).resolve().parents[3] / "Brummel_TPGAMA" / "images.png"
            if logo_path.exists():
                img = tk.PhotoImage(file=str(logo_path))
                desired_height = 36
                if img.height() > desired_height:
                    factor = max(1, int(round(img.height() / desired_height)))
                    img = img.subsample(factor, factor)
                self._logo_image = img
                # Utiliser tk.Label pour controler bordures et fond et eviter toute ombre
                tk.Label(
                    header,
                    image=self._logo_image,
                    bg="#f6f7f9",
                    bd=0,
                    highlightthickness=0,
                    relief=tk.FLAT,
                ).grid(row=0, column=0, sticky="w", padx=(0, 8))
            else:
                tk.Label(header, text="", bg="#f6f7f9", bd=0, highlightthickness=0).grid(row=0, column=0, sticky="w")
        except Exception:
            # En cas d'erreur d'affichage, laisser un emplacement vide sans bordure
            tk.Label(header, text="", bg="#f6f7f9", bd=0, highlightthickness=0).grid(row=0, column=0, sticky="w")

        # Titres à droite du logo
        ttk.Label(header, text="FuzzyRec", style="Title.TLabel").grid(row=0, column=1, sticky="w")
        ttk.Label(
            header,
            text="Recommandation Mamdani avec preferences imprecises",
            style="Muted.TLabel",
        ).grid(row=0, column=2, sticky="w", padx=(12, 0))

        controls = ttk.Frame(container, style="Panel.TFrame", padding=8)
        controls.grid(row=1, column=0, sticky="ew")
        controls.columnconfigure(7, weight=1)

        self.load_button = ttk.Button(controls, text="Charger catalogue", command=self.load_catalog)
        self.load_button.grid(row=0, column=0, padx=(0, 8), pady=(0, 6))
        self.dataset_button = ttk.Button(controls, text="Changer dossier", command=self.choose_dataset)
        self.dataset_button.grid(row=0, column=1, padx=(0, 12), pady=(0, 6))
        ttk.Label(controls, text="User ID").grid(row=0, column=2, sticky="w")
        user_entry = ttk.Entry(controls, textvariable=self.user_id_var, width=8)
        user_entry.grid(row=0, column=3, padx=(4, 12), pady=(0, 6))
        ttk.Label(controls, text="Top-N").grid(row=0, column=4, sticky="w")
        top_n_entry = ttk.Entry(controls, textvariable=self.top_n_var, width=6)
        top_n_entry.grid(row=0, column=5, padx=(4, 12), pady=(0, 6))
        recommend_button = ttk.Button(controls, text="Recommander", command=self.run_recommendations)
        recommend_button.grid(row=0, column=6, sticky="w", pady=(0, 6))
        ttk.Label(controls, text="Dataset").grid(row=1, column=0, sticky="w")
        dataset_entry = ttk.Entry(controls, textvariable=self.dataset_path_var)
        dataset_entry.grid(row=1, column=1, columnspan=7, sticky="ew")
        self.controls_to_lock = [user_entry, top_n_entry, recommend_button]

        body = ttk.PanedWindow(container, orient=tk.VERTICAL)
        body.grid(row=2, column=0, sticky="nsew", pady=(8, 8))

        notebook = ttk.Notebook(body)
        preferences_tab = ttk.Frame(notebook)
        membership_tab = ttk.Frame(notebook)
        notebook.add(preferences_tab, text="Preferences")
        notebook.add(membership_tab, text="Courbes")
        body.add(notebook, weight=1)

        self.preferences_editor = PreferencesEditor(preferences_tab, on_change=self._on_preference_changed)
        self.preferences_editor.render().grid(row=0, column=0, sticky="nsew")
        preferences_tab.rowconfigure(0, weight=1)
        preferences_tab.columnconfigure(0, weight=1)

        results_pane = ttk.PanedWindow(body, orient=tk.VERTICAL)
        # Faire occuper results_pane 50% de la fenetre (notebook 50%)
        body.add(results_pane, weight=1)

        recommendations_section = ttk.LabelFrame(results_pane, text="Films recommandes", padding=6)
        self.recommendations_view = RecommendationsView(recommendations_section)
        self.recommendations_view.render().grid(row=0, column=0, sticky="nsew")
        recommendations_section.rowconfigure(0, weight=1)
        recommendations_section.columnconfigure(0, weight=1)
        results_pane.add(recommendations_section, weight=1)
        self.recommendations_view.tree.bind("<<TreeviewSelect>>", self._on_recommendation_selected)

        explanation_section = ttk.LabelFrame(results_pane, text="Trace d'explication", padding=6)
        self.explanation_view = ExplanationView(explanation_section)
        self.explanation_view.render().grid(row=0, column=0, sticky="nsew")
        explanation_section.rowconfigure(0, weight=1)
        explanation_section.columnconfigure(0, weight=1)
        results_pane.add(explanation_section, weight=1)

        ttk.Label(container, textvariable=self.status_var, style="Status.TLabel").grid(row=3, column=0, sticky="ew")
        self._membership_tab = membership_tab
        container.rowconfigure(2, weight=1)
        container.columnconfigure(0, weight=1)
        self._set_controls_enabled(False)

    def load_catalog(self) -> None:
        """Charger les donnees MovieLens et construire le pipeline."""

        if self.dataset_path_var is not None and self.dataset_path_var.get().strip():
            self.raw_dir = Path(self.dataset_path_var.get().strip()).expanduser()
            self.dataset_path_var.set(str(self.raw_dir))
        self._set_status("Chargement du catalogue...")
        self._set_controls_enabled(False)
        try:
            self.context = load_recommender_context(self.raw_dir)
        except Exception as exc:  # pragma: no cover - branche dependante du poste
            messagebox.showerror("Chargement impossible", str(exc))
            self._set_status(f"Erreur de chargement: {exc}")
            return
        if self.preferences_editor is not None:
            genres = MovieLensPreprocessor().build_genre_vocabulary(self.context.features["genre_list"])
            self.preferences_editor.set_genres(genres)
        self._build_membership_view()
        self._set_controls_enabled(True)
        self._set_status(f"Catalogue charge: {len(self.context.recommender.repository.movies)} films")

    def choose_dataset(self) -> None:
        """Selectionner un dossier MovieLens et recharger le catalogue."""

        selected = filedialog.askdirectory(
            title="Choisir un dossier MovieLens",
            initialdir=str(self.raw_dir if self.raw_dir.exists() else Path.cwd()),
        )
        if not selected:
            return
        self.raw_dir = Path(selected)
        if self.dataset_path_var is not None:
            self.dataset_path_var.set(str(self.raw_dir))
        self.load_catalog()

    def run_recommendations(self) -> None:
        """Produire le Top-N et afficher la premiere explication."""

        if self.context is None:
            self.load_catalog()
        if self.context is None:
            return

        try:
            user_id = int(self._value(self.user_id_var, "1"))
            top_n = int(self._value(self.top_n_var, "10"))
            explicit_preferences = self.preferences_editor.get_preferences() if self.preferences_editor else None
            self.profile = build_profile(
                user_id=user_id,
                raw_data=self.context.raw_data,
                explicit_preferences=explicit_preferences,
            )
            recommendations = self.context.recommender.recommend(self.profile, top_n=top_n)
        except PrefilterEmptyError as exc:
            messagebox.showwarning("Aucun candidat", str(exc))
            self._set_status(str(exc))
            return
        except Exception as exc:
            messagebox.showerror("Recommandation impossible", str(exc))
            self._set_status(f"Erreur de recommandation: {exc}")
            return

        if self.recommendations_view is not None:
            self.recommendations_view.set_recommendations(recommendations)
        self._set_status(f"{len(recommendations)} recommandations produites")
        if recommendations:
            self._show_explanation(recommendations[0])
            if self.membership_view is not None and recommendations[0].inference is not None:
                self.membership_view.update_output_memberships(recommendations[0].inference.output_memberships)

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

    def _set_controls_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for widget in self.controls_to_lock:
            try:
                widget.configure(state=state)
            except tk.TclError:
                pass
        if self.preferences_editor is not None:
            self.preferences_editor.set_enabled(enabled)

    def _build_membership_view(self) -> None:
        if self.context is None or not hasattr(self, "_membership_tab"):
            return
        for child in self._membership_tab.winfo_children():
            child.destroy()
        variables = {
            **self.context.recommender.fuzzifier.variables,
            "recommendation_score": self.context.recommender.output_variable,
        }
        self.membership_view = MembershipView(self._membership_tab, variables)
        self.membership_view.render().grid(row=0, column=0, sticky="nsew")
        self._membership_tab.rowconfigure(0, weight=1)
        self._membership_tab.columnconfigure(0, weight=1)

    def _on_preference_changed(self, genre: str, value: float) -> None:
        if self.membership_view is not None:
            self.membership_view.update_highlight("genre_preference", value, label=genre)

    @staticmethod
    def _value(variable: tk.StringVar | None, default: str) -> str:
        return variable.get().strip() if variable is not None and variable.get().strip() else default

    def _configure_style(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("App.TFrame", background="#f6f7f9")
        style.configure("Panel.TFrame", background="#ffffff", relief="flat")
        style.configure("Title.TLabel", background="#f6f7f9", foreground="#1f2937", font=("TkDefaultFont", 16, "bold"))
        style.configure("Muted.TLabel", background="#f6f7f9", foreground="#667085")
        style.configure("Status.TLabel", background="#eef2f7", foreground="#344054", padding=(8, 5))
        style.configure("Treeview", rowheight=24)
        style.configure("TNotebook", padding=2)
