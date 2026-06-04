"""Visualisation des fonctions d'appartenance.

Les graphes de fonctions d'appartenance sont necessaires pour la validation du
comportement flou et pour le support de demonstration. Ce module reserve le
contrat de visualisation sans generer encore de figures.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fuzzy.linguistic_vars import LinguisticVariable


@dataclass
class MembershipPlotter:
    """Generateur de figures pour variables linguistiques.

    TODO:
        - Tracer chaque terme d'une variable.
        - Afficher la valeur crisp courante si fournie.
        - Sauvegarder les figures pour le rapport.
    """

    output_dir: Path = Path("reports/figures")

    def plot_variable(self, variable: LinguisticVariable) -> object:
        """Construire une figure pour une variable linguistique."""

        raise NotImplementedError("TODO: tracer une variable linguistique.")

    def save_variable_plot(self, variable: LinguisticVariable, filename: str) -> Path:
        """Sauvegarder une figure de variable linguistique."""

        raise NotImplementedError("TODO: sauvegarder la visualisation.")
