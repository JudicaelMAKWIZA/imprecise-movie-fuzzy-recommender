"""Compatibilite pour les fonctions d'appartenance.

Le module officiel est `fuzzy.membership_functions`. Ce fichier conserve les
anciens noms `triangular` et `trapezoidal` utilises par les premiers tests et
par quelques modules du squelette.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .membership_functions import (
    MembershipFunction,
    TrapezoidalMembershipFunction,
    TriangularMembershipFunction,
    trapezoidal,
    triangular,
)


@dataclass(frozen=True)
class MembershipDefinition:
    """Description declarative d'une fonction d'appartenance.

    Attributes:
        name: Nom lisible du terme linguistique, par exemple `forte`.
        kind: Type de courbe attendu, par exemple `triangular` ou
            `trapezoidal`.
        parameters: Parametres numeriques de la courbe. Leur interpretation
            depend de `kind` et sera validee lors de l'implementation.

    TODO:
        - Ajouter la validation des parametres selon le type de fonction.
        - Ajouter un adaptateur vers les fonctions numeriques du module.
    """

    name: str
    kind: str
    parameters: Sequence[float]

    def build(self) -> MembershipFunction:
        """Construire la fonction d'appartenance concrete."""

        if self.kind == "triangular":
            return TriangularMembershipFunction(*self.parameters)
        if self.kind == "trapezoidal":
            return TrapezoidalMembershipFunction(*self.parameters)
        raise ValueError(f"Type de fonction d'appartenance non supporte: {self.kind}")


def gaussian(x: float, mean: float, sigma: float) -> float:
    """Evaluer une fonction d'appartenance gaussienne.

    Cette forme est prevue pour experimentation ou comparaison, mais elle n'est
    pas prioritaire pour la Version 1 de l'architecture retenue.

    TODO:
        Implementer uniquement si les variables linguistiques futures en ont
        besoin ou si la validation scientifique l'exige.
    """

    raise NotImplementedError("La fonction gaussienne est hors perimetre V1.")


def sigmoid(x: float, center: float, slope: float) -> float:
    """Evaluer une fonction d'appartenance sigmoide.

    Cette fonction pourra representer des transitions progressives. Elle reste
    hors du coeur V1 tant que les termes triangulaires et trapezoidaux suffisent.

    TODO:
        Implementer apres stabilisation de la V1 minimale.
    """

    raise NotImplementedError("La fonction sigmoide est hors perimetre V1.")
