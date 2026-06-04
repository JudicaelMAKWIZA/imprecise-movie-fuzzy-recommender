"""Depot d'acces aux films candidats.

Le repository masquera le format de stockage des donnees derivees et fournira
des methodes de consultation aux couches recommandation et CLI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .schemas import MovieFeatures


@dataclass
class MovieRepository:
    """Point d'acces aux caracteristiques de films.

    Attributes:
        movies: Collection de films pretraites.

    TODO:
        - Indexer les films par `movie_id`.
        - Fournir un pre-filtrage par genre pour l'Architecture B.
        - Conserver des methodes simples pour la CLI.
    """

    movies: Iterable[MovieFeatures]

    def get_by_id(self, movie_id: int) -> MovieFeatures | None:
        """Retrouver un film par identifiant MovieLens.

        TODO:
            Implementer un index pour eviter une recherche lineaire.
        """

        raise NotImplementedError("TODO: retrouver un film par identifiant.")

    def filter_by_genres(self, genres: Iterable[str]) -> list[MovieFeatures]:
        """Pre-filtrer les films par genres candidats.

        Cette operation correspond a la premiere etape de l'Architecture B. Elle
        reste crisp et ne remplace pas le FIS Mamdani.

        TODO:
            Implementer le pre-filtrage sans exclure abusivement les candidats.
        """

        raise NotImplementedError("TODO: pre-filtrer les films par genre.")

    def search_by_title(self, query: str) -> list[MovieFeatures]:
        """Rechercher des films par titre pour la CLI ou la GUI.

        TODO:
            Ajouter une recherche simple et deterministic.
        """

        raise NotImplementedError("TODO: rechercher des films par titre.")
