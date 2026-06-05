"""Tests des outils de visualisation matplotlib."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from matplotlib.figure import Figure

from fuzzy.linguistic_variables import build_genre_preference_variable
from visualization.membership_plots import MembershipPlotter


def test_membership_plotter_builds_figure() -> None:
    """Le plotter produit une Figure matplotlib exploitable."""

    plotter = MembershipPlotter()
    figure = plotter.plot_variable(build_genre_preference_variable(), points=20, highlight_value=0.5)

    assert isinstance(figure, Figure)


def test_membership_plotter_saves_file(tmp_path: Path) -> None:
    """La visualisation peut etre sauvegardee pour la demonstration."""

    plotter = MembershipPlotter(output_dir=tmp_path)
    output_path = plotter.save_variable_plot(build_genre_preference_variable(), "genre.png", points=20)

    assert output_path.exists()
    assert output_path.stat().st_size > 0
