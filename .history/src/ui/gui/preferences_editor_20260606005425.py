"""Editeur graphique des preferences floues utilisateur."""

from __future__ import annotations

from collections.abc import Callable
import tkinter as tk
from tkinter import ttk

from fuzzy.fuzzifier import Fuzzifier
from .scroll_bindings import enable_mousewheel_scroll
from recommender.user_profile import GenrePreferenceValue, IntervalGenrePreference, LinguisticGenrePreference


DEFAULT_LINGUISTIC_PREFERENCES = {"Sci-Fi": "forte", "Action": "moyenne"}
TERM_TO_VALUE = {"faible": 0.2, "moyenne": 0.5, "forte": 0.85}
MODE_VALUES = ("linguistique", "crisp", "intervalle")


class PreferencesEditor:
    """Composant Tkinter pour saisir les preferences de genres par curseurs."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        default_preferences: dict[str, str] | None = None,
        on_change: Callable[[str, object], None] | None = None,
    ) -> None:
        self.parent = parent
        self.default_preferences = default_preferences or DEFAULT_LINGUISTIC_PREFERENCES
        self.on_change = on_change
        self.fuzzifier = Fuzzifier.default_v1()
        self.frame = ttk.Frame(parent)
        self.canvas: tk.Canvas | None = None
        self.scrollable_frame: ttk.Frame | None = None
        self.value_vars: dict[str, tk.DoubleVar] = {}
        self.upper_vars: dict[str, tk.DoubleVar] = {}
        self.label_vars: dict[str, tk.StringVar] = {}
        self.mode_vars: dict[str, tk.StringVar] = {}
        self.upper_scales: dict[str, ttk.Scale] = {}
        self.touched_genres: set[str] = set(self.default_preferences)
        self._rendered = False

    def render(self) -> ttk.Frame:
        """Afficher les controles de preferences et retourner le conteneur."""

        if self._rendered:
            return self.frame

        ttk.Label(self.frame, text="Preferences genres").grid(row=0, column=0, sticky="w")
        self.canvas = tk.Canvas(self.frame, height=135, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda _event: self.canvas.configure(scrollregion=self.canvas.bbox("all")) if self.canvas else None,
        )
        window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfigure(window_id, width=event.width) if self.canvas else None,
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(4, 0))
        # Activer le défilement par molette / geste (2 doigts) sur le canvas
        try:
            enable_mousewheel_scroll(self.canvas)
        except Exception:
            pass
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self._rendered = True
        self.set_genres(sorted(self.default_preferences))
        return self.frame

    def set_genres(self, genres: list[str]) -> None:
        """Reconstruire la liste de curseurs depuis le vocabulaire charge."""

        if self.scrollable_frame is None:
            self.render()
        assert self.scrollable_frame is not None
        for child in self.scrollable_frame.winfo_children():
            child.destroy()
        self.value_vars.clear()
        self.upper_vars.clear()
        self.label_vars.clear()
        self.mode_vars.clear()
        self.upper_scales.clear()

        all_genres = sorted(set(genres).union(self.default_preferences))
        for row, genre in enumerate(all_genres):
            default_term = self.default_preferences.get(genre)
            initial_value = TERM_TO_VALUE.get(default_term or "", 0.0)
            value_var = tk.DoubleVar(value=initial_value)
            upper_var = tk.DoubleVar(value=min(1.0, initial_value + 0.2))
            label_var = tk.StringVar(value=self._dominant_label(initial_value))
            mode_var = tk.StringVar(value="linguistique")
            self.value_vars[genre] = value_var
            self.upper_vars[genre] = upper_var
            self.label_vars[genre] = label_var
            self.mode_vars[genre] = mode_var

            ttk.Label(self.scrollable_frame, text=genre, width=14).grid(row=row, column=0, sticky="w", padx=(0, 6), pady=1)
            scale = ttk.Scale(
                self.scrollable_frame,
                from_=0.0,
                to=1.0,
                orient="horizontal",
                variable=value_var,
                command=lambda raw, selected=genre: self._on_scale_changed(selected, raw),
            )
            scale.grid(row=row, column=1, sticky="ew", padx=(0, 6), pady=1)
            ttk.Label(self.scrollable_frame, textvariable=label_var, width=9).grid(row=row, column=2, sticky="w", pady=1)
            upper_scale = ttk.Scale(
                self.scrollable_frame,
                from_=0.0,
                to=1.0,
                orient="horizontal",
                variable=upper_var,
                command=lambda _raw, selected=genre: self._on_interval_changed(selected),
            )
            upper_scale.grid(row=row, column=3, sticky="ew", padx=(0, 6), pady=1)
            upper_scale.grid_remove()
            self.upper_scales[genre] = upper_scale
            mode = ttk.Combobox(
                self.scrollable_frame,
                textvariable=mode_var,
                values=MODE_VALUES,
                width=11,
                state="readonly",
            )
            mode.grid(row=row, column=4, sticky="e", pady=1)
            mode.bind("<<ComboboxSelected>>", lambda _event, selected=genre: self._on_mode_changed(selected))
        self.scrollable_frame.columnconfigure(1, weight=1)
        self.scrollable_frame.columnconfigure(3, weight=1)

    def get_preferences(self) -> dict[str, GenrePreferenceValue]:
        """Retourner les preferences pretes pour `build_profile`."""

        preferences: dict[str, GenrePreferenceValue] = {}
        for genre in sorted(self.touched_genres):
            if genre not in self.value_vars:
                continue
            value = float(self.value_vars[genre].get())
            mode = self.mode_vars[genre].get()
            if mode == "crisp":
                preferences[genre] = max(0.0, min(1.0, value))
            elif mode == "intervalle":
                upper_value = float(self.upper_vars[genre].get())
                lower, upper = sorted((max(0.0, min(1.0, value)), max(0.0, min(1.0, upper_value))))
                preferences[genre] = IntervalGenrePreference(
                    lower=lower,
                    upper=upper,
                )
            else:
                preferences[genre] = LinguisticGenrePreference(self._dominant_term(value))
        return preferences

    def set_enabled(self, enabled: bool) -> None:
        """Activer ou desactiver les controles de saisie."""

        state = "normal" if enabled else "disabled"
        combo_state = "readonly" if enabled else "disabled"
        for child in self.frame.winfo_children():
            self._set_widget_state(child, state=state, combo_state=combo_state)

    def _on_scale_changed(self, genre: str, raw_value: str) -> None:
        value = float(raw_value)
        self.touched_genres.add(genre)
        # Update label (dominant linguistic label for the numeric value)
        self.label_vars[genre].set(self._dominant_label(value))
        # Send an appropriate representation depending on the selected mode
        mode = self.mode_vars[genre].get()
        if mode == "linguistique":
            term = self._dominant_term(value)
            if self.on_change is not None:
                self.on_change(genre, term)
        elif mode == "intervalle":
            upper = float(self.upper_vars[genre].get())
            lower = value
            if upper < lower:
                # keep upper at least equal to lower
                self.upper_vars[genre].set(lower)
                upper = lower
            if self.on_change is not None:
                self.on_change(genre, (lower, upper))
        else:  # crisp
            if self.on_change is not None:
                self.on_change(genre, value)

    def _on_interval_changed(self, genre: str) -> None:
        self.touched_genres.add(genre)
        # When the upper bound moves, notify with the interval
        lower = float(self.value_vars[genre].get())
        upper = float(self.upper_vars[genre].get())
        if upper < lower:
            self.upper_vars[genre].set(lower)
            upper = lower
        if self.on_change is not None:
            self.on_change(genre, (lower, upper))

    def _on_mode_changed(self, genre: str) -> None:
        self.touched_genres.add(genre)
        upper_scale = self.upper_scales.get(genre)
        if upper_scale is None:
            return
        mode = self.mode_vars[genre].get()
        if mode == "intervalle":
            upper_scale.grid()
            if float(self.upper_vars[genre].get()) < float(self.value_vars[genre].get()):
                self.upper_vars[genre].set(float(self.value_vars[genre].get()))
            # notify with the current interval
            if self.on_change is not None:
                lower = float(self.value_vars[genre].get())
                upper = float(self.upper_vars[genre].get())
                self.on_change(genre, (lower, upper))
        else:
            upper_scale.grid_remove()
            # notify with crisp or linguistic representation depending on mode
            if self.on_change is not None:
                if mode == "linguistique":
                    val = float(self.value_vars[genre].get())
                    self.on_change(genre, self._dominant_term(val))
                else:
                    self.on_change(genre, float(self.value_vars[genre].get()))

    def _dominant_label(self, value: float) -> str:
        term = self._dominant_term(value)
        return {"faible": "faible", "moyenne": "moyenne", "forte": "forte"}[term]

    def _dominant_term(self, value: float) -> str:
        degrees = self.fuzzifier.fuzzify_value("genre_preference", max(0.0, min(1.0, value)))
        return max(degrees, key=lambda term: (degrees[term], term))

    def _set_widget_state(self, widget: tk.Widget, *, state: str, combo_state: str) -> None:
        try:
            widget.configure(state=combo_state if isinstance(widget, ttk.Combobox) else state)
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            self._set_widget_state(child, state=state, combo_state=combo_state)
