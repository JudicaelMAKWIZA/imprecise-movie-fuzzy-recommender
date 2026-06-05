"""Defuzzification des sorties floues.

La decision officielle retient la methode du centroide pour produire un score
crisp de recommandation dans `[0, 1]`. L'implementation reste from scratch :
elle reconstruit une surface Mamdani agregee a partir des termes linguistiques
de sortie, puis calcule son centre de gravite discret.
"""

from __future__ import annotations

from dataclasses import dataclass, field
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
    _surface_cache: dict[tuple[object, ...], tuple[np.ndarray, dict[str, np.ndarray]]] = field(
        default_factory=dict,
        init=False,
        repr=False,
    )

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

        membership_array = np.asarray(memberships, dtype=float)
        if np.any((membership_array < 0.0) | (membership_array > 1.0)):
            raise ValueError("Les degres d'appartenance doivent rester dans [0, 1].")
        universe_array = np.asarray(universe, dtype=float)
        numerator = float(np.dot(universe_array, membership_array))
        denominator = float(np.sum(membership_array))

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
        universe, term_surfaces = self._term_surfaces(output_variable)
        clipped_surfaces = []
        for term, activation_degree in output_memberships.items():
            if term not in term_surfaces:
                raise ValueError(f"Terme de sortie inconnu pour {output_variable.name}: {term}")
            numeric_activation = float(activation_degree)
            if not 0.0 <= numeric_activation <= 1.0:
                raise ValueError(f"Degre de sortie invalide pour {term}: {activation_degree}")
            clipped_surfaces.append(np.minimum(numeric_activation, term_surfaces[term]))
        aggregated_memberships = np.maximum.reduce(clipped_surfaces) if clipped_surfaces else np.zeros_like(universe)

        score = self.centroid(universe, aggregated_memberships)
        return max(output_variable.universe_min, min(output_variable.universe_max, score))

    def _term_surfaces(self, variable: LinguisticVariable) -> tuple[np.ndarray, dict[str, np.ndarray]]:
        key = (
            variable.name,
            variable.universe_min,
            variable.universe_max,
            self.resolution,
            tuple(
                (term, fuzzy_set.membership_function.parameters)
                for term, fuzzy_set in variable.fuzzy_sets.items()
            ),
        )
        if key not in self._surface_cache:
            universe = np.linspace(variable.universe_min, variable.universe_max, self.resolution)
            self._surface_cache[key] = (
                universe,
                {
                    term: np.asarray([fuzzy_set.membership(float(point)) for point in universe], dtype=float)
                    for term, fuzzy_set in variable.fuzzy_sets.items()
                },
            )
        return self._surface_cache[key]

    def bisector(self, universe: Sequence[float], memberships: Sequence[float]) -> float:
        """Calculer le bisecteur de surface d'une sortie floue.

        Cette methode est prevue comme option de comparaison, pas comme choix
        principal de la Version 1.

        Cette methode reste hors du coeur V1.
        """

        raise NotImplementedError("La defuzzification par bisecteur est hors perimetre V1.")
