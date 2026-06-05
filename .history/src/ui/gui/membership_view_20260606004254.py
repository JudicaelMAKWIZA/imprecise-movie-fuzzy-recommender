"""Vue Tkinter des courbes d'appartenance floues."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Mapping

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.axes import Axes
from matplotlib.collections import PolyCollection
from matplotlib.lines import Line2D
from matplotlib.figure import Figure

from fuzzy.linguistic_variables import LinguisticVariable
from visualization.membership_plots import MembershipPlotter


class MembershipView:
    """Composant embarquant les courbes d'appartenance Matplotlib."""

    def __init__(self, parent: tk.Widget, variables: Mapping[str, LinguisticVariable]) -> None:
        self.parent = parent
        self.variables = dict(variables)
        self.frame = ttk.Frame(parent)
        self.notebook = ttk.Notebook(self.frame)
        self.plotter = MembershipPlotter()
        self.canvases: dict[str, FigureCanvasTkAgg] = {}
        self.figures: dict[str, Figure] = {}
        self.axes: dict[str, Axes] = {}
        # highlight_lines stores a list of matplotlib artists (Line2D, Patch, ...)
        self.highlight_lines: dict[tuple[str, str | None], list] = {}
        # highlight_values stores the raw value used to render the highlight
        self.highlight_values: dict[tuple[str, str | None], object] = {}
        self.output_surface: PolyCollection | None = None
        self.output_memberships: Mapping[str, float] = {}
        self._rendered = False

    def render(self) -> ttk.Frame:
        """Afficher le notebook des variables."""

        if self._rendered:
            return self.frame
        self.notebook.grid(row=0, column=0, sticky="nsew")
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        for variable_name, variable in self.variables.items():
            figure = self.plotter.plot_variable(variable)
            axis = figure.axes[0]
            tab = ttk.Frame(self.notebook)
            canvas = FigureCanvasTkAgg(figure, master=tab)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            self.notebook.add(tab, text=variable_name)
            self.canvases[variable_name] = canvas
            self.figures[variable_name] = figure
            self.axes[variable_name] = axis
        self._rendered = True
        return self.frame

    def refresh(self) -> None:
        """Compatibilite: dessiner les figures si le composant n'est pas rendu."""

        self.render()

    def update_highlight(self, variable_name: str, value: float | None, *, label: str | None = None) -> None:
        """Mettre a jour la valeur surlignee d'une variable."""

        if variable_name not in self.variables:
            return
        self.render()
        key = (variable_name, label)
        axis = self.axes[variable_name]
        # remove existing highlight for this key
        old_artists = self.highlight_lines.pop(key, None)
        if old_artists:
            for art in old_artists:
                try:
                    art.remove()
                except Exception:
                    pass
        self.highlight_values.pop(key, None)

        if value is None:
            self._sync_legend(variable_name, axis)
            self._redraw(variable_name)
            return

        variable = self.variables[variable_name]
        # Support three kinds of inputs: numeric crisp, interval tuple, or linguistic term
        artists: list = []
        try:
            # Numeric (crisp) value
            if isinstance(value, (int, float)) or (isinstance(value, str) and value.replace('.', '', 1).isdigit()):
                val = float(value)
                try:
                    variable.validate_value(val)
                except ValueError:
                    return
                line_label = label or "valeur courante"
                line = axis.axvline(val, linestyle="--", linewidth=1.2, color="black", label=line_label)
                artists.append(line)

            elif isinstance(value, (tuple, list)) and len(value) == 2:
                lower = float(value[0])
                upper = float(value[1])
                try:
                    variable.validate_value(lower)
                    variable.validate_value(upper)
                except ValueError:
                    return
                # ensure lower <= upper
                lower, upper = (lower, upper) if lower <= upper else (upper, lower)
                l1 = axis.axvline(lower, linestyle="--", linewidth=1.0, color="black")
                l2 = axis.axvline(upper, linestyle="--", linewidth=1.0, color="black")
                span = axis.axvspan(lower, upper, alpha=0.15, color="gray", label=label or "intervalle")
                artists.extend([l1, l2, span])

            else:
                # treat as linguistic term (string)
                term = str(value)
                term_normalised = term.casefold().strip().replace(" ", "_").replace("-", "_")
                if term_normalised not in variable.fuzzy_sets:
                    # try raw term as-is
                    if term not in variable.fuzzy_sets:
                        return
                    term_normalised = term
                universe = np.linspace(variable.universe_min, variable.universe_max, 501)
                alpha_values = variable.fuzzy_sets[term_normalised].alpha_cut(universe, alpha=0.5)
                if not alpha_values:
                    return
                lower, upper = min(alpha_values), max(alpha_values)
                span = axis.axvspan(lower, upper, alpha=0.18, color="orange", label=label or term)
                artists.append(span)

        finally:
            if artists:
                self.highlight_lines[key] = artists
                self.highlight_values[key] = value
                self._sync_legend(variable_name, axis)
                self._redraw(variable_name)

    def update_output_memberships(self, output_memberships: Mapping[str, float]) -> None:
        """Tracer la surface Mamdani agregee de sortie."""

        self.output_memberships = dict(output_memberships)
        self.render()
        variable_name = "recommendation_score"
        if variable_name not in self.variables:
            return
        if self.output_surface is not None:
            self.output_surface.remove()
            self.output_surface = None
        axis = self.axes[variable_name]
        variable = self.variables[variable_name]
        x_values, aggregated = self._aggregate_output_surface(variable, self.output_memberships)
        if x_values is not None and aggregated is not None:
            self.output_surface = axis.fill_between(
                x_values,
                aggregated,
                alpha=0.25,
                color="black",
                label="sortie agregee",
            )
            axis.legend()
            self.figures[variable_name].tight_layout()
        self._redraw(variable_name)

    @staticmethod
    def _aggregate_output_surface(
        variable: LinguisticVariable,
        output_memberships: Mapping[str, float],
    ) -> tuple[np.ndarray | None, np.ndarray | None]:
        x_values = np.linspace(variable.universe_min, variable.universe_max, 500)
        surfaces = []
        for term, degree in output_memberships.items():
            if term not in variable.fuzzy_sets:
                continue
            y_values = np.asarray([variable.fuzzy_sets[term].membership(float(value)) for value in x_values])
            surfaces.append(np.minimum(float(degree), y_values))
        if surfaces:
            return x_values, np.maximum.reduce(surfaces)
        return None, None

    def _redraw(self, variable_name: str) -> None:
        canvas = self.canvases.get(variable_name)
        if canvas is not None:
            canvas.draw_idle()

    def _sync_legend(self, variable_name: str, axis: Axes) -> None:
        handles = []
        labels = []
        for (key_variable, label), artists in self.highlight_lines.items():
            if key_variable != variable_name:
                continue
            # artists may be a single artist or a list of artists
            if not isinstance(artists, (list, tuple)):
                artists = [artists]
            # prefer an artist that is attached to this axis and has a label
            chosen = None
            for art in artists:
                try:
                    if getattr(art, "axes", None) is axis:
                        chosen = art
                        break
                except Exception:
                    continue
            if chosen is not None:
                handles.append(chosen)
                labels.append(label or "valeur courante")
        if handles:
            axis.legend(handles, labels)
            return
        legend = axis.get_legend()
        if legend is not None:
            legend.remove()
