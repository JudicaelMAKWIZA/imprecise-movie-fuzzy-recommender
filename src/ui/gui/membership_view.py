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
        self.highlight_lines: dict[tuple[str, str | None], Line2D] = {}
        self.highlight_values: dict[tuple[str, str | None], float] = {}
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
        if value is None:
            self.highlight_values.pop(key, None)
            line = self.highlight_lines.pop(key, None)
            if line is not None:
                line.remove()
                self._redraw(variable_name)
            return
        variable = self.variables[variable_name]
        variable.validate_value(float(value))
        self.highlight_values[key] = float(value)
        axis = self.axes[variable_name]
        line = self.highlight_lines.get(key)
        if line is None:
            line_label = label or "valeur courante"
            line = axis.axvline(float(value), linestyle="--", linewidth=1.2, label=line_label)
            self.highlight_lines[key] = line
            axis.legend()
        else:
            line.set_xdata([float(value), float(value)])
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
