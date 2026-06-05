"""Tests non graphiques pour la GUI Tkinter."""

from pathlib import Path

from ui.gui.main_window import MainWindow


def test_main_window_initialises_without_opening_tk(tmp_path: Path) -> None:
    """L'instanciation ne cree pas de fenetre avant `show`."""

    window = MainWindow(raw_dir=tmp_path)

    assert window.raw_dir == tmp_path
    assert window.root is None
    assert window.context is None
    assert MainWindow._value(None, "10") == "10"
