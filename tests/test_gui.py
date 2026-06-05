"""Tests headless pour la GUI Tkinter."""

from pathlib import Path
import tkinter as tk

import matplotlib
import pytest

matplotlib.use("Agg")

from data_manager.movie_repository import MovieRepository
from data_manager.schemas import MovieFeatures
from fuzzy.fuzzifier import Fuzzifier
from fuzzy.inference_engine import MamdaniInferenceEngine
from fuzzy.rule_base import RuleBase
from recommender.fuzzy_recommender import FuzzyRecommender, Recommendation
from recommender.user_profile import IntervalGenrePreference, LinguisticGenrePreference
from test_cli import _write_cli_movielens_dataset
from ui.gui.main_window import MainWindow
from ui.gui.membership_view import MembershipView
from ui.gui.preferences_editor import PreferencesEditor
from ui.gui.recommendations_view import RecommendationsView


pytestmark = pytest.mark.gui


def test_main_window_initialises_without_opening_tk(tmp_path: Path) -> None:
    """L'instanciation ne cree pas de fenetre avant `show`."""

    window = MainWindow(raw_dir=tmp_path)

    assert window.raw_dir == tmp_path
    assert window.root is None
    assert window.context is None
    assert MainWindow._value(None, "10") == "10"


def test_preferences_editor_returns_preference_dict() -> None:
    """PreferencesEditor convertit les curseurs en GenrePreferenceValue."""

    root = _tk_root()
    try:
        editor = PreferencesEditor(root)
        editor.render()
        editor.set_genres(["Sci-Fi", "Action", "Drama"])
        editor.value_vars["Drama"].set(0.85)
        editor.mode_vars["Drama"].set("linguistique")
        editor._on_scale_changed("Drama", "0.85")

        preferences = editor.get_preferences()

        assert isinstance(preferences["Sci-Fi"], LinguisticGenrePreference)
        assert preferences["Sci-Fi"].term == "forte"
        assert isinstance(preferences["Action"], LinguisticGenrePreference)
        assert preferences["Action"].term == "moyenne"
        assert isinstance(preferences["Drama"], LinguisticGenrePreference)
        assert preferences["Drama"].term == "forte"
    finally:
        root.destroy()


def test_preferences_editor_interval_mode_uses_custom_upper_bound() -> None:
    """Le mode intervalle utilise la borne haute reglee par l'utilisateur."""

    root = _tk_root()
    try:
        editor = PreferencesEditor(root)
        editor.render()
        editor.set_genres(["Drama"])
        editor.value_vars["Drama"].set(0.25)
        editor.upper_vars["Drama"].set(0.75)
        editor.mode_vars["Drama"].set("intervalle")
        editor._on_mode_changed("Drama")

        preferences = editor.get_preferences()

        assert isinstance(preferences["Drama"], IntervalGenrePreference)
        assert preferences["Drama"].lower == pytest.approx(0.25)
        assert preferences["Drama"].upper == pytest.approx(0.75)
    finally:
        root.destroy()


def test_preferences_editor_updates_genres_after_catalog_load(tmp_path: Path) -> None:
    """La liste des genres est reconstruite apres chargement du catalogue."""

    _write_cli_movielens_dataset(tmp_path)
    root = _tk_root()
    try:
        window = MainWindow(raw_dir=tmp_path)
        window.root = root
        window._build_widgets(root)
        window.load_catalog()

        assert window.dataset_path_var is not None
        assert window.dataset_path_var.get() == str(tmp_path)
        assert window.preferences_editor is not None
        assert "Comedy" in window.preferences_editor.value_vars
        assert "Sci-Fi" in window.preferences_editor.value_vars
    finally:
        root.destroy()


def test_main_window_choose_dataset_reloads_selected_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Le bouton de choix de dossier recharge le catalogue selectionne."""

    _write_cli_movielens_dataset(tmp_path)
    monkeypatch.setattr("ui.gui.main_window.filedialog.askdirectory", lambda **_kwargs: str(tmp_path))
    root = _tk_root()
    try:
        window = MainWindow(raw_dir=tmp_path / "missing")
        window.root = root
        window._build_widgets(root)

        window.choose_dataset()

        assert window.raw_dir == tmp_path
        assert window.dataset_path_var is not None
        assert window.dataset_path_var.get() == str(tmp_path)
        assert window.context is not None
    finally:
        root.destroy()


def test_recommendations_view_populates_tree() -> None:
    """RecommendationsView insere les recommandations dans le Treeview."""

    root = _tk_root()
    try:
        view = RecommendationsView(root)
        view.render()
        recommendations = [
            Recommendation(MovieFeatures(1, "A", ["Action"], 4.0, 20), 0.7),
            Recommendation(MovieFeatures(2, "B", ["Drama"], 4.5, 30), 0.8),
        ]

        view.set_recommendations(recommendations)

        assert view.tree.get_children() == ("0", "1")
    finally:
        root.destroy()


def test_membership_view_creates_figures() -> None:
    """MembershipView cree une figure Matplotlib par variable."""

    root = _tk_root()
    try:
        recommender = _build_gui_recommender()
        variables = {
            **recommender.fuzzifier.variables,
            "recommendation_score": recommender.output_variable,
        }
        view = MembershipView(root, variables)
        view.render()
        canvas_id = id(view.canvases["genre_preference"])

        assert "genre_preference" in view.figures
        assert "recommendation_score" in view.figures
        view.update_highlight("genre_preference", 0.2, label="Action")
        view.update_highlight("genre_preference", 0.7, label="Action")
        view.update_highlight("genre_preference", 0.8, label="Drama")
        assert id(view.canvases["genre_preference"]) == canvas_id
        assert view.highlight_values[("genre_preference", "Action")] == pytest.approx(0.7)
        assert view.highlight_values[("genre_preference", "Drama")] == pytest.approx(0.8)

        view.update_highlight("genre_preference", None, label="Action")

        assert set(view.highlight_lines) == {("genre_preference", "Drama")}
        legend = view.axes["genre_preference"].get_legend()
        assert legend is not None
        assert [text.get_text() for text in legend.get_texts()] == ["Drama"]
    finally:
        root.destroy()


def test_preferences_editor_highlights_each_changed_genre() -> None:
    """Deux sliders de genres produisent deux lignes de surlignage distinctes."""

    root = _tk_root()
    try:
        recommender = _build_gui_recommender()
        variables = {
            **recommender.fuzzifier.variables,
            "recommendation_score": recommender.output_variable,
        }
        view = MembershipView(root, variables)
        view.render()
        editor = PreferencesEditor(
            root,
            on_change=lambda genre, value: view.update_highlight("genre_preference", value, label=genre),
        )
        editor.render()
        editor.set_genres(["Action", "Drama"])

        editor._on_scale_changed("Action", "0.3")
        editor._on_scale_changed("Drama", "0.8")

        assert view.highlight_values[("genre_preference", "Action")] == pytest.approx(0.3)
        assert view.highlight_values[("genre_preference", "Drama")] == pytest.approx(0.8)
    finally:
        root.destroy()


def test_main_window_run_recommendations_updates_status(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """run_recommendations fonctionne sur un mini dataset avec messagebox patche."""

    _write_cli_movielens_dataset(tmp_path)
    monkeypatch.setattr("ui.gui.main_window.messagebox.showerror", lambda *args, **kwargs: None)
    monkeypatch.setattr("ui.gui.main_window.messagebox.showwarning", lambda *args, **kwargs: None)
    root = _tk_root()
    try:
        window = MainWindow(raw_dir=tmp_path)
        window.root = root
        window._build_widgets(root)
        window.load_catalog()
        window.run_recommendations()

        assert window.status_var is not None
        assert "recommandations produites" in window.status_var.get()
    finally:
        root.destroy()


def _tk_root() -> tk.Tk:
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk indisponible: {exc}")
    root.withdraw()
    return root


def _build_gui_recommender() -> FuzzyRecommender:
    return FuzzyRecommender(
        repository=MovieRepository([MovieFeatures(1, "Demo", ["Sci-Fi"], 4.8, 300)]),
        fuzzifier=Fuzzifier.default_v1(),
        inference_engine=MamdaniInferenceEngine(RuleBase.load_minimal_v1()),
    )
