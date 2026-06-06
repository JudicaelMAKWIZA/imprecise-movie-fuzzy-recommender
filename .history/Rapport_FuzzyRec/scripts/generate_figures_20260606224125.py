"""Generate report figures for Rapport_FuzzyRec."""

from __future__ import annotations

import subprocess
import sys
import tkinter as tk
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "Rapport_FuzzyRec"
FIGURES = REPORT / "figures"
sys.path.insert(0, str(ROOT / "src"))

from recommender.pipeline_factory import build_profile, load_recommender_context  # noqa: E402
from ui.gui.main_window import MainWindow  # noqa: E402
from visualization.membership_plots import MembershipPlotter  # noqa: E402


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    context = load_recommender_context(ROOT / "data/movie", config_path=ROOT / "config/fuzzy_config.yaml")
    generate_memberships(context)
    recommendation = generate_mamdani_example(context)
    generate_cli_capture()
    generate_gui_captures(recommendation is not None)


def generate_memberships(context) -> None:
    plotter = MembershipPlotter(output_dir=FIGURES)
    variables = {
        **context.recommender.fuzzifier.variables,
        "recommendation_score": context.recommender.output_variable,
    }
    for name, variable in variables.items():
        figure = plotter.plot_variable(variable)
        figure.axes[0].set_title(_french_title(name))
        figure.savefig(FIGURES / f"membership_{name}.png", dpi=180, bbox_inches="tight")
        plt.close(figure)


def generate_mamdani_example(context):
    profile = build_profile(
        user_id=1,
        raw_data=context.raw_data,
        explicit_preferences="Sci-Fi=forte,Action=moyenne",
    )
    recommendations = context.recommender.recommend(profile, top_n=5)
    if not recommendations:
        return None
    recommendation = recommendations[0]
    variable = context.recommender.output_variable
    output_memberships = recommendation.inference.output_memberships if recommendation.inference else {}

    x_values = np.linspace(variable.universe_min, variable.universe_max, 600)
    figure, axis = plt.subplots(figsize=(8.5, 4.6))
    surfaces = []
    for term, fuzzy_set in variable.fuzzy_sets.items():
        y_values = np.asarray([fuzzy_set.membership(float(value)) for value in x_values])
        axis.plot(x_values, y_values, linewidth=1.3, label=term.replace("_", " "))
        degree = float(output_memberships.get(term, 0.0))
        if degree > 0:
            clipped = np.minimum(degree, y_values)
            surfaces.append(clipped)
            axis.fill_between(x_values, clipped, alpha=0.28)
    if surfaces:
        aggregated = np.maximum.reduce(surfaces)
        axis.plot(x_values, aggregated, color="black", linewidth=2.0, label="agregation max")
    if recommendation.score is not None:
        axis.axvline(recommendation.score, color="red", linestyle="--", linewidth=1.6, label="centroide")
    axis.set_title("Inference Mamdani pour la premiere recommandation")
    axis.set_xlabel("Score de recommandation")
    axis.set_ylabel("Degre d'appartenance")
    axis.set_ylim(-0.04, 1.04)
    axis.grid(True, alpha=0.25)
    axis.legend(loc="upper left", fontsize=8)
    figure.tight_layout()
    figure.savefig(FIGURES / "exemple_inference_mamdani2.png", dpi=180, bbox_inches="tight")
    plt.close(figure)
    return recommendation


def generate_cli_capture() -> None:
    command = [
        sys.executable,
        str(ROOT / "main.py"),
        "recommend",
        "--user-id",
        "1",
        "--top-n",
        "10",
        "--set-genre",
        "Sci-Fi=forte,Action=moyenne",
        "--explain",
        "--data-dir",
        str(ROOT / "data/movie"),
    ]
    output = subprocess.check_output(command, cwd=ROOT, text=True)
    (FIGURES / "cli_output.txt").write_text(output, encoding="utf-8")
    visible_lines = output.splitlines()[:34]
    rendered = "\n".join(visible_lines)
    figure = plt.figure(figsize=(10.5, 7.2))
    figure.patch.set_facecolor("#111827")
    figure.text(
        0.03,
        0.97,
        rendered,
        va="top",
        ha="left",
        color="#f9fafb",
        family="monospace",
        fontsize=9,
    )
    figure.savefig(FIGURES / "cli_recommend2.png", dpi=180, bbox_inches="tight", facecolor=figure.get_facecolor())
    plt.close(figure)


def generate_gui_captures(_has_recommendation: bool) -> None:
    root = tk.Tk()
    root.geometry("1040x760")
    window = MainWindow(raw_dir=ROOT / "data/movie")
    window.root = root
    window._configure_style()
    window._build_widgets(root)
    root.update()
    window.load_catalog()
    root.update()
    _capture(root, FIGURES / "gui_preferences2.png")

    notebook = _find_notebook(root)
    if notebook is not None and len(notebook.tabs()) > 1:
        notebook.select(notebook.tabs()[1])
    root.update()
    _capture(root, FIGURES / "gui_courbes2.png")

    if notebook is not None:
        notebook.select(notebook.tabs()[0])
    window.run_recommendations()
    root.update()
    _capture(root, FIGURES / "gui_resultats2.png")
    root.destroy()


def _capture(root: tk.Tk, output: Path) -> None:
    root.update()
    xwd_path = output.with_suffix(".xwd")
    try:
        subprocess.run(["xwd", "-silent", "-id", str(root.winfo_id()), "-out", str(xwd_path)], check=True)
        subprocess.run(["convert", str(xwd_path), str(output)], check=True)
    finally:
        if xwd_path.exists():
            xwd_path.unlink()


def _find_notebook(widget):
    from tkinter import ttk

    if isinstance(widget, ttk.Notebook):
        return widget
    for child in widget.winfo_children():
        found = _find_notebook(child)
        if found is not None:
            return found
    return None


def _french_title(name: str) -> str:
    titles = {
        "genre_preference": "Preference de genre",
        "average_rating": "Note moyenne",
        "popularity": "Popularite",
        "recommendation_score": "Score de recommandation",
    }
    return titles.get(name, name)


if __name__ == "__main__":
    main()
