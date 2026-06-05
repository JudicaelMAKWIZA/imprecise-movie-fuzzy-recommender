"""Pretraitement des donnees MovieLens pour le systeme flou.

Le preprocesseur derive les attributs V1 attendus par les specifications :
`avg_rating`, `num_ratings`, `genre_list` et `genre_vector`. L'anciennete reste
reportee, mais `release_year` est extraite comme champ informatif pour garder
une architecture extensible.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd
from pandas import DataFrame

from .loader import DataValidationError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MovieLensPreprocessor:
    """Transforme les donnees brutes MovieLens en caracteristiques de films.

    Attributes:
        processed_dir: Dossier de sortie pour les donnees derivees. Ce dossier
            est cree a la demande et separe strictement les donnees transformees
            des fichiers bruts.
    """

    processed_dir: Path | str = Path("data/processed")

    def __post_init__(self) -> None:
        object.__setattr__(self, "processed_dir", Path(self.processed_dir))

    def build_movie_features(self, raw_data: dict[str, DataFrame]) -> DataFrame:
        """Build the feature table used by the fuzzy recommender.

        Args:
            raw_data: Dictionary returned by `MovieLensLoader.load_all`.

        Returns:
            DataFrame containing one row per movie and the derived columns:
            `genre_list`, `genre_vector`, `avg_rating`, `num_ratings` and
            `release_year`.

        Raises:
            DataValidationError: If required raw tables are missing.
        """

        self._validate_raw_data(raw_data)
        logger.info("Construction des caracteristiques de films MovieLens")
        movies = raw_data["movies"].copy()
        ratings = raw_data["ratings"].copy()

        rating_stats = (
            ratings.groupby("movieId", as_index=False)
            .agg(avg_rating=("rating", "mean"), num_ratings=("rating", "size"))
            .astype({"num_ratings": "int64"})
        )

        features = movies.merge(rating_stats, on="movieId", how="left")
        features["avg_rating"] = features["avg_rating"].astype("Float64")
        features["num_ratings"] = features["num_ratings"].astype("Int64")
        features["genre_list"] = features["genres"].map(self.split_genres)
        features["release_year"] = features["title"].map(self.extract_release_year).astype("Int64")

        vocabulary = self.build_genre_vocabulary(features["genre_list"])
        features["genre_vector"] = features["genre_list"].map(
            lambda genres: {genre: int(genre in genres) for genre in vocabulary}
        )

        for genre in vocabulary:
            features[f"genre_{self._normalise_genre_column(genre)}"] = features["genre_list"].map(
                lambda genres, selected=genre: int(selected in genres)
            )

        logger.info("Caracteristiques construites pour %s films", len(features))
        return features

    def split_genres(self, genres: str) -> list[str]:
        """Split the MovieLens pipe-separated genre string.

        `(no genres listed)` is represented as an empty list because it should
        not activate any genre preference during pre-filtering.
        """

        if not isinstance(genres, str) or genres.strip() in {"", "(no genres listed)"}:
            return []
        return [genre.strip() for genre in genres.split("|") if genre.strip()]

    def build_genre_vocabulary(self, genre_lists: Iterable[list[str]]) -> list[str]:
        """Build a stable sorted vocabulary from movie genre lists."""

        vocabulary = sorted({genre for genres in genre_lists for genre in genres})
        logger.debug("Vocabulaire de genres construit: %s", vocabulary)
        return vocabulary

    def extract_release_year(self, title: str) -> int | None:
        """Extract a four-digit release year from a MovieLens title.

        The latest four-digit year enclosed in parentheses is returned. `None`
        is returned when the title does not expose a parseable year.
        """

        if not isinstance(title, str):
            return None
        matches = re.findall(r"\((\d{4})\)", title)
        if not matches:
            return None
        return int(matches[-1])

    def save_processed(self, features: DataFrame, filename: str = "movies_features.csv") -> Path:
        """Persist processed features under `data/processed/`.

        CSV is used by default to avoid optional parquet engines. Complex list
        and dictionary columns are JSON-encoded in the saved file.
        """

        self.processed_dir.mkdir(parents=True, exist_ok=True)
        path = self.processed_dir / filename
        serialisable = features.copy()
        for column in ("genre_list", "genre_vector"):
            if column in serialisable.columns:
                serialisable[column] = serialisable[column].map(json.dumps)

        if path.suffix.lower() != ".csv":
            raise ValueError("Seul le format CSV est supporte dans cette phase.")
        serialisable.to_csv(path, index=False)
        logger.info("Caracteristiques sauvegardees dans %s", path)
        return path

    def load_processed(self, filename: str = "movies_features.csv") -> DataFrame:
        """Load processed features saved by `save_processed`."""

        path = self.processed_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Fichier de donnees derivees introuvable: {path}")
        dataframe = pd.read_csv(path)
        for column in ("genre_list", "genre_vector"):
            if column in dataframe.columns:
                dataframe[column] = dataframe[column].map(json.loads)
        logger.info("Caracteristiques derivees chargees depuis %s", path)
        return dataframe

    @staticmethod
    def _normalise_genre_column(genre: str) -> str:
        return re.sub(r"[^a-z0-9]+", "_", genre.lower()).strip("_")

    @staticmethod
    def _validate_raw_data(raw_data: dict[str, DataFrame]) -> None:
        required_keys = {"movies", "ratings", "tags", "links"}
        missing = required_keys.difference(raw_data)
        if missing:
            raise DataValidationError(f"Donnees brutes incompletes: {sorted(missing)}")
