"""Agregation des consequents flous.

Dans le modele Mamdani retenu, plusieurs regles peuvent activer le meme terme
de sortie. L'agregation V1 combine ces consequents par maximum.
"""

from __future__ import annotations

from dataclasses import dataclass

from .inference_engine import RuleActivation


@dataclass
class ConsequentAggregator:
    """Service responsable de l'agregation des sorties de regles."""

    method: str = "max"

    def aggregate(self, activations: list[RuleActivation]) -> dict[str, float]:
        """Agreger les consequents des regles activees.

        Args:
            activations: Liste des regles activees par le moteur d'inference.

        Returns:
            Degres agregees par terme de sortie.
        """

        if self.method != "max":
            raise ValueError(f"Methode d'agregation non supportee en V1: {self.method}")

        aggregated: dict[str, float] = {}
        for activation in activations:
            if not activation.is_active:
                continue
            term = activation.consequent_term
            aggregated[term] = max(aggregated.get(term, 0.0), activation.degree)
        return aggregated
