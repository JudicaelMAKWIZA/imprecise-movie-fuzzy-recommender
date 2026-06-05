"""Depot d'acces aux films candidats."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass

import pandas as pd
from pandas import DataFrame

from .schemas import MovieFeatures


@dataclass
class MovieRepository:
    """Point d'acces aux caracteristiques de films.

    Attributes:
        movies: Collection de films pretraites.

    Le repository accepte une collection de `MovieFeatures` et construit un
    index local pour les consultations frequentes. Il reste volontairement
    simple : aucune logique floue n'est placee ici.
    """

    movies: Iterable[MovieFeatures]

    def __post_init__(self) -> None:
        self.movies = list(self.movies)
        self._index = {movie.movie_id: movie for movie in self.movies}

    @classmethod
    def from_dataframe(cls, dataframe: DataFrame) -> "MovieRepository":
        """Construire un repository depuis les caracteristiques pretraitees."""

        movies: list[MovieFeatures] = []
        for row in dataframe.itertuples(index=False):
            movie_id = int(getattr(row, "movieId", getattr(row, "movie_id", 0)))
            average_rating = getattr(row, "avg_rating", getattr(row, "average_rating", None))
            number_of_ratings = getattr(row, "num_ratings", getattr(row, "number_of_ratings", None))
            release_year = getattr(row, "release_year", None)
            movies.append(
                MovieFeatures(
                    movie_id=movie_id,
                    title=str(getattr(row, "title")),
                    genre_list=_normalise_genre_list(getattr(row, "genre_list", [])),
                    average_rating=None if _is_missing(average_rating) else float(average_rating),
                    number_of_ratings=0 if _is_missing(number_of_ratings) else int(number_of_ratings),
                    release_year=None if _is_missing(release_year) else int(release_year),
                    genre_vector=_normalise_genre_vector(getattr(row, "genre_vector", {})),
                )
            )
        return cls(movies=movies)

    def get_by_id(self, movie_id: int) -> MovieFeatures | None:
        """Retrouver un film par identifiant MovieLens.
        """

        return self._index.get(movie_id)

    def filter_by_genres(self, genres: Iterable[str]) -> list[MovieFeatures]:
        """Pre-filtrer les films par genres candidats.

        Cette operation correspond a la premiere etape de l'Architecture B. Elle
        reste crisp et ne remplace pas le FIS Mamdani.
        """

        requested_genres = {_normalise_genre(genre) for genre in genres}
        if not requested_genres:
            return list(self.movies)
        return [
            movie
            for movie in self.movies
            if requested_genres.intersection({_normalise_genre(genre) for genre in movie.genre_list})
        ]

    def search_by_title(self, query: str) -> list[MovieFeatures]:
        """Rechercher des films par titre pour la CLI ou la GUI.
        """

        normalised_query = query.casefold().strip()
        if not normalised_query:
            return []
        return [movie for movie in self.movies if normalised_query in movie.title.casefold()]


def _normalise_genre(genre: str) -> str:
    return str(genre).casefold().strip()


def _is_missing(value: object) -> bool:
    return bool(pd.isna(value))


def _normalise_genre_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped or stripped.lower() == "nan":
            return []
        try:
            decoded = json.loads(stripped)
        except json.JSONDecodeError:
            decoded = stripped.split("|") if "|" in stripped else [stripped]
        return [str(genre).strip() for genre in decoded if str(genre).strip()]
    if isinstance(value, Iterable):
        return [str(genre).strip() for genre in value if str(genre).strip()]
    return []


def _normalise_genre_vector(value: object) -> dict[str, int]:
    if value is None:
        return {}
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped or stripped.lower() == "nan":
            return {}
        try:
            value = json.loads(stripped)
        except json.JSONDecodeError:
            return {}
    if isinstance(value, dict):
        return {str(genre): int(present) for genre, present in value.items()}
    return {}
