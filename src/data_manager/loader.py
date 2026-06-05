"""Chargement valide des fichiers MovieLens.

Ce module charge les quatre fichiers requis par les specifications :
`movies.csv`, `ratings.csv`, `tags.csv` et `links.csv`. Il applique une
validation minimale mais stricte sur les colonnes attendues, les valeurs
obligatoires et les bornes des notes.

La logique de chargement est volontairement separee du pretraitement : le loader
lit et valide les donnees brutes, tandis que `MovieLensPreprocessor` derive les
attributs utiles au systeme flou.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

import pandas as pd
from pandas import DataFrame

logger = logging.getLogger(__name__)


class DataLoadingError(RuntimeError):
    """Erreur levee lorsqu'un fichier MovieLens ne peut pas etre lu."""


class DataValidationError(ValueError):
    """Erreur levee lorsqu'un fichier MovieLens ne respecte pas le schema attendu."""


@dataclass(frozen=True)
class MovieLensLoader:
    """Lecteur valide des fichiers bruts MovieLens `ml-latest-small`.

    Attributes:
        raw_dir: Dossier contenant les fichiers `movies.csv`, `ratings.csv`,
            `tags.csv` et `links.csv`.

    The loader returns pandas DataFrames because the downstream preprocessing
    phase needs reliable grouping, joining and aggregation operations. No file is
    ever modified by this class.
    """

    raw_dir: Path | str = Path("data/movie")

    MOVIES_COLUMNS: ClassVar[tuple[str, ...]] = ("movieId", "title", "genres")
    RATINGS_COLUMNS: ClassVar[tuple[str, ...]] = ("userId", "movieId", "rating", "timestamp")
    TAGS_COLUMNS: ClassVar[tuple[str, ...]] = ("userId", "movieId", "tag", "timestamp")
    LINKS_COLUMNS: ClassVar[tuple[str, ...]] = ("movieId", "imdbId", "tmdbId")

    def __post_init__(self) -> None:
        object.__setattr__(self, "raw_dir", Path(self.raw_dir))

    def load_movies(self) -> DataFrame:
        """Load and validate `movies.csv`.

        Returns:
            DataFrame with columns `movieId`, `title` and `genres`.

        Raises:
            DataLoadingError: If the file is missing or unreadable.
            DataValidationError: If the expected schema is not respected.
        """

        dataframe = self._read_csv("movies.csv")
        self.validate_movies(dataframe)
        return dataframe

    def load_ratings(self) -> DataFrame:
        """Load and validate `ratings.csv`.

        The rating column is checked against the MovieLens rating scale
        `[0.5, 5.0]`.
        """

        dataframe = self._read_csv("ratings.csv")
        self.validate_ratings(dataframe)
        return dataframe

    def load_tags(self) -> DataFrame:
        """Load and validate `tags.csv`."""

        dataframe = self._read_csv("tags.csv")
        self.validate_tags(dataframe)
        return dataframe

    def load_links(self) -> DataFrame:
        """Load and validate `links.csv`.

        `tmdbId` is allowed to contain missing values in MovieLens, so the
        validation only requires `movieId` and `imdbId` to be present.
        """

        dataframe = self._read_csv("links.csv", dtype={"imdbId": "string", "tmdbId": "string"})
        self.validate_links(dataframe)
        return dataframe

    def load_all(self) -> dict[str, DataFrame]:
        """Load every official MovieLens file.

        Returns:
            A dictionary with stable keys: `movies`, `ratings`, `tags`, `links`.
        """

        logger.info("Chargement complet du dataset MovieLens depuis %s", self.raw_dir)
        data = {
            "movies": self.load_movies(),
            "ratings": self.load_ratings(),
            "tags": self.load_tags(),
            "links": self.load_links(),
        }
        logger.info(
            "Dataset charge: movies=%s ratings=%s tags=%s links=%s",
            len(data["movies"]),
            len(data["ratings"]),
            len(data["tags"]),
            len(data["links"]),
        )
        return data

    def validate_movies(self, dataframe: DataFrame) -> None:
        """Validate the schema and required values of `movies.csv`."""

        self._validate_columns("movies.csv", dataframe, self.MOVIES_COLUMNS)
        self._validate_non_empty("movies.csv", dataframe)
        self._validate_required_values("movies.csv", dataframe, ("movieId", "title", "genres"))
        if dataframe["movieId"].duplicated().any():
            raise DataValidationError("movies.csv contient des movieId dupliques.")

    def validate_ratings(self, dataframe: DataFrame) -> None:
        """Validate the schema and rating scale of `ratings.csv`."""

        self._validate_columns("ratings.csv", dataframe, self.RATINGS_COLUMNS)
        self._validate_non_empty("ratings.csv", dataframe)
        self._validate_required_values("ratings.csv", dataframe, self.RATINGS_COLUMNS)
        invalid = dataframe.loc[~dataframe["rating"].between(0.5, 5.0), "rating"]
        if not invalid.empty:
            raise DataValidationError("ratings.csv contient des notes hors de l'intervalle [0.5, 5.0].")

    def validate_tags(self, dataframe: DataFrame) -> None:
        """Validate the schema of `tags.csv`."""

        self._validate_columns("tags.csv", dataframe, self.TAGS_COLUMNS)
        self._validate_non_empty("tags.csv", dataframe)
        self._validate_required_values("tags.csv", dataframe, self.TAGS_COLUMNS)

    def validate_links(self, dataframe: DataFrame) -> None:
        """Validate the schema of `links.csv`."""

        self._validate_columns("links.csv", dataframe, self.LINKS_COLUMNS)
        self._validate_non_empty("links.csv", dataframe)
        self._validate_required_values("links.csv", dataframe, ("movieId", "imdbId"))
        if dataframe["movieId"].duplicated().any():
            raise DataValidationError("links.csv contient des movieId dupliques.")

    def _read_csv(self, filename: str, **read_csv_kwargs: object) -> DataFrame:
        path = self.raw_dir / filename
        logger.info("Chargement du fichier %s", path)
        if not path.exists():
            logger.error("Fichier MovieLens introuvable: %s", path)
            raise DataLoadingError(f"Fichier introuvable: {path}")
        try:
            dataframe = pd.read_csv(path, **read_csv_kwargs)
        except Exception as exc:  # pragma: no cover - pandas details vary by version
            logger.exception("Impossible de lire %s", path)
            raise DataLoadingError(f"Impossible de lire {path}") from exc
        logger.debug("%s charge avec %s lignes et %s colonnes", filename, len(dataframe), len(dataframe.columns))
        return dataframe

    @staticmethod
    def _validate_columns(filename: str, dataframe: DataFrame, expected_columns: tuple[str, ...]) -> None:
        missing = set(expected_columns).difference(dataframe.columns)
        if missing:
            raise DataValidationError(f"{filename} ne contient pas les colonnes attendues: {sorted(missing)}")

    @staticmethod
    def _validate_non_empty(filename: str, dataframe: DataFrame) -> None:
        if dataframe.empty:
            raise DataValidationError(f"{filename} est vide.")

    @staticmethod
    def _validate_required_values(filename: str, dataframe: DataFrame, columns: tuple[str, ...]) -> None:
        null_columns = [column for column in columns if dataframe[column].isna().any()]
        if null_columns:
            raise DataValidationError(f"{filename} contient des valeurs manquantes: {null_columns}")
