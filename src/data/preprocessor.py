"""Pretraitement des donnees MovieLens.

Le pretraitement produira les attributs derives requis par le FIS :
`average_rating`, `number_of_ratings`, `genre_list`, `genre_vector` et, plus
tard, `release_year`. Les sorties doivent etre stockees dans `data/processed/`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MovieLensPreprocessor:
    """Transformateur des donnees brutes en caracteristiques de films.

    Attributes:
        processed_dir: Dossier ou ecrire les donnees derivees.

    TODO:
        - Calculer la moyenne des notes par film.
        - Calculer le nombre de notes par film.
        - Extraire les listes de genres.
        - Encoder les genres dans un vecteur stable.
        - Ne jamais modifier les fichiers bruts.
    """

    processed_dir: Path = Path("data/processed")

    def build_movie_features(self, raw_data: dict[str, Any]) -> Any:
        """Construire la table des caracteristiques de films.

        Args:
            raw_data: Donnees chargees par `MovieLensLoader.load_all`.

        Returns:
            Structure tabulaire ou collection de `MovieFeatures`.

        TODO:
            Implementer le pipeline de derivation apres le chargement CSV.
        """

        raise NotImplementedError("TODO: construire les caracteristiques de films.")

    def extract_release_year(self, title: str) -> int | None:
        """Extraire l'annee de sortie depuis un titre MovieLens.

        Cette variable est reportee hors V1 selon les decisions, mais la methode
        est reservee pour garder l'architecture extensible.

        TODO:
            Implementer l'extraction regex lorsque l'anciennete sera activee.
        """

        raise NotImplementedError("TODO: extraire l'annee depuis le titre.")

    def save_processed(self, features: Any, filename: str = "movies_features.parquet") -> Path:
        """Sauvegarder les donnees derivees.

        TODO:
            Definir le format de sortie officiel, parquet ou CSV.
        """

        raise NotImplementedError("TODO: sauvegarder les donnees derivees.")

    def load_processed(self, filename: str = "movies_features.parquet") -> Any:
        """Charger des donnees derivees deja construites.

        TODO:
            Ajouter ce raccourci pour eviter de recalculer le pretraitement.
        """

        raise NotImplementedError("TODO: charger les donnees derivees.")
