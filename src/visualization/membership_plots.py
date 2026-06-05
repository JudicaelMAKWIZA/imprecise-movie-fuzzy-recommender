"""Visualisation matplotlib des fonctions d'appartenance."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from matplotlib.figure import Figure

from fuzzy.linguistic_variables import LinguisticVariable


@dataclass
class MembershipPlotter:
    """Generateur de figures pour variables linguistiques.

    The plotter returns matplotlib figures so tests, CLI commands and future GUI
    code can decide whether to save, display or embed the output.
    """

    output_dir: Path = Path("reports/figures")

    def plot_variable(
        self,
        variable: LinguisticVariable,
        points: int = 500,
        highlight_value: float | None = None,
    ) -> Figure:
        """Build a matplotlib figure for all fuzzy sets in `variable`."""

        if points < 2:
            raise ValueError("points doit etre superieur ou egal a 2.")

        x_values = np.linspace(variable.universe_min, variable.universe_max, points)
        figure = Figure()
        axis = figure.subplots()
        for fuzzy_set in variable.fuzzy_sets.values():
            y_values = [fuzzy_set.membership(float(value)) for value in x_values]
            axis.plot(x_values, y_values, label=fuzzy_set.label or fuzzy_set.name)

        if highlight_value is not None:
            variable.validate_value(highlight_value)
            axis.axvline(highlight_value, color="black", linestyle="--", linewidth=1)

        axis.set_title(variable.label or variable.name)
        axis.set_xlabel("Valeur")
        axis.set_ylabel("Degre d'appartenance")
        axis.set_ylim(-0.05, 1.05)
        axis.legend()
        axis.grid(True, alpha=0.25)
        figure.tight_layout()
        return figure

    def save_variable_plot(
        self,
        variable: LinguisticVariable,
        filename: str,
        points: int = 500,
        highlight_value: float | None = None,
    ) -> Path:
        """Save a membership plot and return the generated path."""

        import matplotlib.pyplot as plt

        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / filename
        figure = self.plot_variable(variable, points=points, highlight_value=highlight_value)
        figure.savefig(path)
        plt.close(figure)
        return path
