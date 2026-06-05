"""Schemas de donnees utilises par la couche MovieLens.

Ces dataclasses documentent les colonnes brutes et les attributs derives
attendus. Elles ne chargent pas les CSV et ne calculent aucune caracteristique.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MovieRecord:
    """Ligne brute issue de `movies.csv`."""

    movie_id: int
    title: str
    genres: str


@dataclass(frozen=True)
class RatingRecord:
    """Ligne brute issue de `ratings.csv`."""

    user_id: int
    movie_id: int
    rating: float
    timestamp: int


@dataclass(frozen=True)
class TagRecord:
    """Ligne brute issue de `tags.csv`."""

    user_id: int
    movie_id: int
    tag: str
    timestamp: int


@dataclass(frozen=True)
class LinkRecord:
    """Ligne brute issue de `links.csv`."""

    movie_id: int
    imdb_id: str
    tmdb_id: str | None = None


@dataclass
class MovieFeatures:
    """Caracteristiques derivees d'un film pour le FIS.

    Attributes:
        movie_id: Identifiant MovieLens.
        title: Titre original.
        genre_list: Liste de genres separee depuis `movies.csv`.
        average_rating: Note moyenne derivee de `ratings.csv`.
        number_of_ratings: Nombre de notes recues, utilise comme popularite.
        release_year: Annee extraite du titre, reportee hors V1 mais prevue.
        genre_vector: Representation binaire ou numerique des genres.

    TODO:
        - Definir le format exact de `genre_vector`.
        - Ajouter les champs optionnels issus de TMDB uniquement hors V1.
    """

    movie_id: int
    title: str
    genre_list: list[str] = field(default_factory=list)
    average_rating: float | None = None
    number_of_ratings: int | None = None
    release_year: int | None = None
    genre_vector: dict[str, int] = field(default_factory=dict)
