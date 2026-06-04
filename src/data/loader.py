"""Chargement des fichiers MovieLens.

Ce module sera responsable de lire les quatre CSV officiels :
`movies.csv`, `ratings.csv`, `tags.csv` et `links.csv`. Les donnees brutes ne
doivent pas etre modifiees ; toute transformation devra passer par
`MovieLensPreprocessor`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MovieLensLoader:
    """Lecteur des fichiers bruts MovieLens.

    Attributes:
        raw_dir: Chemin vers le dossier contenant les CSV MovieLens.

    TODO:
        - Verifier la presence des quatre fichiers attendus.
        - Charger les CSV avec pandas.
        - Normaliser les noms de colonnes si necessaire.
    """

    raw_dir: Path = Path("data/movie")

    def load_movies(self) -> Any:
        """Charger `movies.csv`.

        TODO:
            Retourner un DataFrame pandas ou une collection typee.
        """

        raise NotImplementedError("TODO: charger movies.csv.")

    def load_ratings(self) -> Any:
        """Charger `ratings.csv`.

        TODO:
            Retourner les notes necessaires au calcul de moyenne et popularite.
        """

        raise NotImplementedError("TODO: charger ratings.csv.")

    def load_tags(self) -> Any:
        """Charger `tags.csv`.

        TODO:
            Prevoir l'enrichissement semantique optionnel par tags.
        """

        raise NotImplementedError("TODO: charger tags.csv.")

    def load_links(self) -> Any:
        """Charger `links.csv`.

        TODO:
            Garder les liens pour extensions futures sans API externe en V1.
        """

        raise NotImplementedError("TODO: charger links.csv.")

    def load_all(self) -> dict[str, Any]:
        """Charger tous les fichiers bruts MovieLens.

        TODO:
            Construire un dictionnaire stable consomme par le preprocesseur.
        """

        raise NotImplementedError("TODO: charger tous les fichiers MovieLens.")
