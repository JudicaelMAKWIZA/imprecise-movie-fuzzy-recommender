"""Agregation des consequents flous.

Dans le modele Mamdani retenu, plusieurs regles peuvent activer le meme terme
de sortie. L'agregation devra combiner ces consequents, typiquement avec un
maximum, avant la defuzzification.
"""

from __future__ import annotations

from dataclasses import dataclass

from .inference_engine import RuleActivation


@dataclass
class ConsequentAggregator:
    """Service responsable de l'agregation des sorties de regles.

    TODO:
        - Implementer l'agregation max recommandee par les specifications.
        - Prevoir un point d'extension pour comparer d'autres t-conormes.
        - Retourner une forme exploitable par la defuzzification.
    """

    method: str = "max"

    def aggregate(self, activations: list[RuleActivation]) -> dict[str, float]:
        """Agreger les consequents des regles activees.

        Args:
            activations: Liste des regles activees par le moteur d'inference.

        Returns:
            Degres agregees par terme de sortie.

        TODO:
            Implementer l'agregation apres la base de regles V1.
        """

        raise NotImplementedError("TODO: implementer l'agregation des consequents.")
