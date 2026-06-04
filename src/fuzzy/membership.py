"""Definitions des fonctions d'appartenance floues.

Ce module doit devenir la bibliotheque manuelle des fonctions d'appartenance du
projet : triangulaire, trapezoidale, gaussienne et sigmoide. Les specifications
imposent que le moteur flou principal soit developpe par l'equipe ; les
bibliotheques externes comme scikit-fuzzy ne pourront servir qu'a la validation.

La version actuelle ne contient que les contrats et les types de base. Aucune
formule mathematique n'est implementee ici.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


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


def triangular(x: float, a: float, b: float, c: float) -> float:
    """Evaluer une fonction d'appartenance triangulaire.

    Cette fonction representera un terme linguistique avec un pic unique. Elle
    devra retourner un degre d'appartenance dans `[0, 1]`.

    Args:
        x: Valeur a evaluer sur l'univers de discours.
        a: Borne gauche ou le degre doit devenir nul.
        b: Sommet du triangle ou le degre doit valoir un.
        c: Borne droite ou le degre doit redevenir nul.

    Returns:
        Le degre d'appartenance de `x`.

    TODO:
        Implementer la formule triangulaire et les controles de bornes.
    """

    raise NotImplementedError("TODO: implementer la fonction triangulaire.")


def trapezoidal(x: float, a: float, b: float, c: float, d: float) -> float:
    """Evaluer une fonction d'appartenance trapezoidale.

    Cette fonction servira principalement aux termes situes aux extremites d'un
    univers de discours, comme `faible` ou `tres_populaire`.

    Args:
        x: Valeur a evaluer.
        a: Debut de la rampe montante.
        b: Debut du plateau.
        c: Fin du plateau.
        d: Fin de la rampe descendante.

    Returns:
        Le degre d'appartenance de `x`.

    TODO:
        Implementer la formule trapezoidale sans utiliser scikit-fuzzy.
    """

    raise NotImplementedError("TODO: implementer la fonction trapezoidale.")


def gaussian(x: float, mean: float, sigma: float) -> float:
    """Evaluer une fonction d'appartenance gaussienne.

    Cette forme est prevue pour experimentation ou comparaison, mais elle n'est
    pas prioritaire pour la Version 1 de l'architecture retenue.

    TODO:
        Implementer uniquement si les variables linguistiques futures en ont
        besoin ou si la validation scientifique l'exige.
    """

    raise NotImplementedError("TODO: implementer la fonction gaussienne.")


def sigmoid(x: float, center: float, slope: float) -> float:
    """Evaluer une fonction d'appartenance sigmoide.

    Cette fonction pourra representer des transitions progressives. Elle reste
    hors du coeur V1 tant que les termes triangulaires et trapezoidaux suffisent.

    TODO:
        Implementer apres stabilisation de la V1 minimale.
    """

    raise NotImplementedError("TODO: implementer la fonction sigmoide.")
