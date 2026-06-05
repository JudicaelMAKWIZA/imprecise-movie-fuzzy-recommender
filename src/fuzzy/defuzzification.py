"""Defuzzification des sorties floues.

La decision officielle retient la methode du centroide pour produire un score
crisp de recommandation dans `[0, 1]`. L'implementation reste from scratch :
elle reconstruit une surface Mamdani agregee a partir des termes linguistiques
de sortie, puis calcule son centre de gravite discret.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .linguistic_variables import LinguisticVariable, build_recommendation_score_variable


@dataclass
class Defuzzifier:
    """Convertisseur d'une sortie floue agregee en score crisp.

    Attributes:
        method: Methode de defuzzification. La V1 supporte `centroid`.
        empty_output_value: Valeur retournee lorsqu'aucune regle n'active la
            sortie floue.
        resolution: Nombre de points utilises pour discretiser l'univers de
            sortie lors de `defuzzify`.
    """

    method: str = "centroid"
    empty_output_value: float = 0.0
    resolution: int = 1001

    def centroid(self, universe: Sequence[float], memberships: Sequence[float]) -> float:
        """Calculer le centre de gravite d'une sortie floue.

        Args:
            universe: Points de discretisation de l'univers de sortie.
            memberships: Degres agregees associees a chaque point.

        Returns:
            Score crisp defuzzifie.
        """

        if len(universe) != len(memberships):
            raise ValueError("universe et memberships doivent avoir la meme longueur.")
        if len(universe) == 0:
            raise ValueError("universe ne peut pas etre vide.")

        numerator = 0.0
        denominator = 0.0
        for x_value, membership in zip(universe, memberships):
            degree = float(membership)
            if not 0.0 <= degree <= 1.0:
                raise ValueError("Les degres d'appartenance doivent rester dans [0, 1].")
            numerator += float(x_value) * degree
            denominator += degree

        if denominator == 0.0:
            return self.empty_output_value
        return numerator / denominator

    def defuzzify(
        self,
        output_memberships: dict[str, float],
        variable: LinguisticVariable | None = None,
    ) -> float:
        """Defuzzifier une sortie Mamdani agregee.

        Args:
            output_memberships: Degres agreges par terme de sortie, par exemple
                `{"fort": 0.6, "tres_fort": 0.3}`.
            variable: Variable linguistique de sortie. Par defaut, la variable
                officielle V1 `recommendation_score` est utilisee.

        Returns:
            Score crisp normalise dans l'univers de la variable, donc `[0, 1]`
            pour `recommendation_score`.
        """

        if self.method != "centroid":
            raise ValueError(f"Methode de defuzzification non supportee en V1: {self.method}")
        if self.resolution < 2:
            raise ValueError("La resolution doit etre superieure ou egale a 2.")
        if not output_memberships:
            return self.empty_output_value

        output_variable = variable or build_recommendation_score_variable()
        universe = np.linspace(output_variable.universe_min, output_variable.universe_max, self.resolution)
        aggregated_memberships: list[float] = []

        for x_value in universe:
            clipped_degrees: list[float] = []
            for term, activation_degree in output_memberships.items():
                if term not in output_variable.fuzzy_sets:
                    raise ValueError(f"Terme de sortie inconnu pour {output_variable.name}: {term}")
                numeric_activation = float(activation_degree)
                if not 0.0 <= numeric_activation <= 1.0:
                    raise ValueError(f"Degre de sortie invalide pour {term}: {activation_degree}")
                term_degree = output_variable.fuzzy_sets[term].membership(float(x_value))
                clipped_degrees.append(min(numeric_activation, term_degree))
            aggregated_memberships.append(max(clipped_degrees, default=0.0))

        score = self.centroid([float(value) for value in universe], aggregated_memberships)
        return max(output_variable.universe_min, min(output_variable.universe_max, score))

    def bisector(self, universe: Sequence[float], memberships: Sequence[float]) -> float:
        """Calculer le bisecteur de surface d'une sortie floue.

        Cette methode est prevue comme option de comparaison, pas comme choix
        principal de la Version 1.

        Cette methode reste hors du coeur V1.
        """

        raise NotImplementedError("La defuzzification par bisecteur est hors perimetre V1.")
