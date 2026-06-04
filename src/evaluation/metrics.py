"""Metriques d'evaluation du systeme de recommandation.

Les metriques prevues par les specifications incluent Precision@N, Recall@N,
Coverage et Diversite. Elles sont declarees ici sans implementation.
"""

from __future__ import annotations

from collections.abc import Iterable


def precision_at_n(recommended: Iterable[int], relevant: Iterable[int], n: int) -> float:
    """Calculer Precision@N.

    TODO:
        Implementer apres stabilisation du format des recommandations.
    """

    raise NotImplementedError("TODO: implementer Precision@N.")


def recall_at_n(recommended: Iterable[int], relevant: Iterable[int], n: int) -> float:
    """Calculer Recall@N.

    TODO:
        Implementer apres definition du protocole train/test.
    """

    raise NotImplementedError("TODO: implementer Recall@N.")


def coverage(recommended_catalog: Iterable[int], full_catalog: Iterable[int]) -> float:
    """Calculer la couverture du catalogue.

    TODO:
        Implementer lorsque les sorties Top-N seront disponibles.
    """

    raise NotImplementedError("TODO: implementer Coverage.")


def diversity_score(recommended: Iterable[int]) -> float:
    """Calculer une mesure de diversite intra-liste.

    TODO:
        Definir la fonction de similarite entre films avant implementation.
    """

    raise NotImplementedError("TODO: implementer la diversite.")
