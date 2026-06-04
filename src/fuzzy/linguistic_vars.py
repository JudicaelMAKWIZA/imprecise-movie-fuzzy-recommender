"""Variables linguistiques du systeme flou.

Les variables V1 retenues par les decisions architecturales sont :

- preference par genre ;
- note moyenne du film ;
- popularite du film.

L'anciennete est reportee a une version ulterieure. Ce module ne fixe pas
encore les parametres des fonctions d'appartenance ; il definit seulement les
objets qui porteront ces definitions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .membership import MembershipDefinition


@dataclass(frozen=True)
class LinguisticTerm:
    """Terme linguistique rattache a une variable floue.

    Attributes:
        name: Nom du terme, par exemple `forte` ou `excellente`.
        membership: Definition de la fonction d'appartenance associee.

    TODO:
        Ajouter une methode d'evaluation lorsque `membership.py` sera pret.
    """

    name: str
    membership: MembershipDefinition


@dataclass
class LinguisticVariable:
    """Variable linguistique definie sur un univers de discours.

    Attributes:
        name: Nom technique de la variable.
        universe_min: Borne inferieure de l'univers.
        universe_max: Borne superieure de l'univers.
        terms: Termes linguistiques disponibles pour cette variable.

    TODO:
        - Charger les termes depuis `config/fuzzy_config.yaml`.
        - Fuzzifier une valeur numerique en degres par terme.
        - Verifier la couverture de l'univers de discours.
    """

    name: str
    universe_min: float
    universe_max: float
    terms: Mapping[str, LinguisticTerm] = field(default_factory=dict)

    def fuzzify(self, value: float) -> dict[str, float]:
        """Transformer une valeur crisp en degres linguistiques.

        Args:
            value: Valeur numerique a projeter sur les termes de la variable.

        Returns:
            Un dictionnaire `{nom_terme: degre}`.

        TODO:
            Appeler les fonctions d'appartenance des termes et retourner les
            degres calcules.
        """

        raise NotImplementedError("TODO: implementer la fuzzification.")
