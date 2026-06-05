"""Vue Tkinter des courbes d'appartenance floues."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Mapping

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
        self.figures = {}
        self.highlight_values: dict[str, float] = {}
        self.output_memberships: Mapping[str, float] = {}

    def render(self) -> ttk.Frame:
        """Afficher le notebook des variables."""

        self.notebook.grid(row=0, column=0, sticky="nsew")
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.refresh()
        return self.frame

    def refresh(self) -> None:
        """Reconstruire les figures depuis les valeurs courantes."""

        for tab_id in self.notebook.tabs():
            self.notebook.forget(tab_id)
        self.canvases.clear()
        self.figures.clear()

        for variable_name, variable in self.variables.items():
            figure = self.plotter.plot_variable(
                variable,
                highlight_value=self.highlight_values.get(variable_name),
            )
            if variable_name == "recommendation_score" and self.output_memberships:
                self._plot_output_surface(figure, variable, self.output_memberships)
            tab = ttk.Frame(self.notebook)
            canvas = FigureCanvasTkAgg(figure, master=tab)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            self.notebook.add(tab, text=variable_name)
            self.canvases[variable_name] = canvas
            self.figures[variable_name] = figure

    def update_highlight(self, variable_name: str, value: float | None) -> None:
        """Mettre a jour la valeur surlignee d'une variable."""

        if value is None:
            self.highlight_values.pop(variable_name, None)
        else:
            self.highlight_values[variable_name] = float(value)
        self.refresh()

    def update_output_memberships(self, output_memberships: Mapping[str, float]) -> None:
        """Tracer la surface Mamdani agregee de sortie."""

        self.output_memberships = dict(output_memberships)
        self.refresh()

    @staticmethod
    def _plot_output_surface(
        figure,
        variable: LinguisticVariable,
        output_memberships: Mapping[str, float],
    ) -> None:
        axis = figure.axes[0]
        x_values = np.linspace(variable.universe_min, variable.universe_max, 500)
        surfaces = []
        for term, degree in output_memberships.items():
            if term not in variable.fuzzy_sets:
                continue
            y_values = np.asarray([variable.fuzzy_sets[term].membership(float(value)) for value in x_values])
            surfaces.append(np.minimum(float(degree), y_values))
        if surfaces:
            aggregated = np.maximum.reduce(surfaces)
            axis.fill_between(x_values, aggregated, alpha=0.25, color="black", label="sortie agregee")
            axis.legend()
            figure.tight_layout()
