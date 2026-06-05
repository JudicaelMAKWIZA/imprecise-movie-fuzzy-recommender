"""Defuzzification des sorties floues.

La decision officielle retient la methode du centroide pour produire un score
crisp de recommandation dans `[0, 1]`. Le bisecteur pourra etre ajoute pour les
comparaisons, mais ne fait pas partie du coeur V1.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass
class Defuzzifier:
    """Convertisseur d'une sortie floue agregee en score crisp.

    TODO:
        - Implementer la methode du centroide.
        - Ajouter les controles pour eviter les divisions par zero.
        - Conserver assez d'informations pour expliquer le score final.
    """

    method: str = "centroid"

    def centroid(self, universe: Sequence[float], memberships: Sequence[float]) -> float:
        """Calculer le centre de gravite d'une sortie floue.

        Args:
            universe: Points de discretisation de l'univers de sortie.
            memberships: Degres agregees associees a chaque point.

        Returns:
            Score crisp defuzzifie.

        TODO:
            Implementer la formule du centroide sans bibliotheque floue externe.
        """

        raise NotImplementedError("TODO: implementer la defuzzification centroide.")

    def bisector(self, universe: Sequence[float], memberships: Sequence[float]) -> float:
        """Calculer le bisecteur de surface d'une sortie floue.

        Cette methode est prevue comme option de comparaison, pas comme choix
        principal de la Version 1.

        TODO:
            Implementer seulement apres le centroide.
        """

        raise NotImplementedError("TODO: implementer la defuzzification bisecteur.")
