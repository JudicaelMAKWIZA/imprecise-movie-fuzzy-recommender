"""Vue graphique des explications de recommandation."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from .scroll_bindings import enable_mousewheel_scroll


class ExplanationView:
    """Composant Tkinter affichant les regles activees et criteres dominants."""

    def __init__(self, parent: tk.Widget) -> None:
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.text = tk.Text(self.frame, height=16, wrap="word", state="disabled")

    def render(self) -> ttk.Frame:
        """Afficher la zone d'explication."""

        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        self.text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        # Activer le défilement par molette/touchpad sur la zone de texte
        try:
            enable_mousewheel_scroll(self.text)
        except Exception:
            pass
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        return self.frame

    def set_text(self, value: str) -> None:
        """Remplacer l'explication affichee."""

        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", value)
        self.text.configure(state="disabled")
