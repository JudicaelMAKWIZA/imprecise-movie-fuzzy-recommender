"""Helpers pour activer le défilement par molette / geste (cross-platform).

Le touchpad à deux doigts envoie généralement des événements équivalents
à la molette (`<MouseWheel>` sur Windows/macOS, `<Button-4/5>` sur X11). Ce
helper lie ces événements à la méthode `yview_scroll` du widget cible tant que
le curseur est au-dessus du widget.
"""

from __future__ import annotations

import typing

import tkinter as tk


def enable_mousewheel_scroll(widget: tk.Widget) -> None:
    """Enable vertical scrolling from mousewheel / touchpad on *widget*.

    The widget must implement `yview_scroll(units, what)` (Canvas, Text,
    ttk.Treeview...). The binding is active only while the pointer is over the
    widget (bind on <Enter> / unbind on <Leave>) to avoid interfering with
    other scrollable areas.
    """

    def _on_mousewheel(event: tk.Event) -> None:
        # X11: Button-4 (up) / Button-5 (down)
        if getattr(event, "num", None) in (4, 5):
            if event.num == 4:
                widget.yview_scroll(-1, "units")
            else:
                widget.yview_scroll(1, "units")
            return

        # Windows / macOS: event.delta is non-zero. On Windows it's a multiple
        # of 120 per notch. On macOS / touchpads it can be smaller/fractional.
        delta = getattr(event, "delta", 0)
        if delta:
            try:
                step = int(-1 * (delta / 120))
            except Exception:
                step = -1 if delta > 0 else 1
            if step == 0:
                step = -1 if delta > 0 else 1
            widget.yview_scroll(step, "units")

    def _on_enter(_event: tk.Event) -> None:
        # Bind globally while pointer is above the widget
        widget.bind_all("<MouseWheel>", _on_mousewheel)
        widget.bind_all("<Button-4>", _on_mousewheel)
        widget.bind_all("<Button-5>", _on_mousewheel)

    def _on_leave(_event: tk.Event) -> None:
        try:
            widget.unbind_all("<MouseWheel>")
            widget.unbind_all("<Button-4>")
            widget.unbind_all("<Button-5>")
        except Exception:
            # Some Tk implementations may raise if unbinding non-existent
            # handlers — ignore safely.
            pass

    widget.bind("<Enter>", _on_enter)
    widget.bind("<Leave>", _on_leave)
