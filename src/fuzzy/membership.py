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
