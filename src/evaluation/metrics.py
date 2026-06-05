"""Metriques d'evaluation du systeme de recommandation."""

from __future__ import annotations

from collections.abc import Iterable


def precision_at_n(recommended: Iterable[int], relevant: Iterable[int], n: int) -> float:
    """Calculer Precision@N.

    `relevant` contient les identifiants de films juges pertinents. La precision
    est calculee sur les `n` premiers elements recommandes.
    """

    if n <= 0:
        raise ValueError("n doit etre strictement positif.")
    recommended_top_n = list(recommended)[:n]
    if not recommended_top_n:
        return 0.0
    relevant_set = set(relevant)
    hits = sum(1 for movie_id in recommended_top_n if movie_id in relevant_set)
    return hits / n


def recall_at_n(recommended: Iterable[int], relevant: Iterable[int], n: int) -> float:
    """Calculer Recall@N.

    Le rappel vaut zero lorsqu'aucun film pertinent n'est disponible.
    """

    if n <= 0:
        raise ValueError("n doit etre strictement positif.")
    relevant_set = set(relevant)
    if not relevant_set:
        return 0.0
    recommended_top_n = set(list(recommended)[:n])
    return len(recommended_top_n.intersection(relevant_set)) / len(relevant_set)


def coverage(recommended_catalog: Iterable[int], full_catalog: Iterable[int]) -> float:
    """Calculer la couverture du catalogue.

    La couverture mesure la proportion de films du catalogue total qui
    apparaissent au moins une fois dans les recommandations.
    """

    full_catalog_set = set(full_catalog)
    if not full_catalog_set:
        return 0.0
    return len(set(recommended_catalog).intersection(full_catalog_set)) / len(full_catalog_set)


def diversity_score(recommended: Iterable[int], genres_by_movie: dict[int, set[str]] | None = None) -> float:
    """Calculer une mesure simple de diversite intra-liste.

    Si `genres_by_movie` est fourni, la diversite est `1 - similarite_jaccard`
    moyenne entre paires de films. Sans genres, la fonction retourne `0.0`
    lorsque la liste contient des doublons et `1.0` lorsque tous les identifiants
    sont distincts.
    """

    recommended_list = list(recommended)
    if len(recommended_list) < 2:
        return 0.0

    if genres_by_movie is None:
        return 1.0 if len(recommended_list) == len(set(recommended_list)) else 0.0

    distances: list[float] = []
    for index, movie_a in enumerate(recommended_list):
        for movie_b in recommended_list[index + 1 :]:
            genres_a = genres_by_movie.get(movie_a, set())
            genres_b = genres_by_movie.get(movie_b, set())
            union = genres_a.union(genres_b)
            if not union:
                distances.append(0.0)
                continue
            similarity = len(genres_a.intersection(genres_b)) / len(union)
            distances.append(1.0 - similarity)

    return sum(distances) / len(distances) if distances else 0.0
