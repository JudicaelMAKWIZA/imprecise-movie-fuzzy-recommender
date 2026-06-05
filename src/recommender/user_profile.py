"""Profil utilisateur flou."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeAlias


@dataclass(frozen=True)
class LinguisticGenrePreference:
    """Preference exprimee directement par un terme flou."""

    term: str


@dataclass(frozen=True)
class IntervalGenrePreference:
    """Preference imprecise exprimee comme intervalle de valeurs possibles."""

    lower: float
    upper: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.lower <= self.upper <= 1.0:
            raise ValueError("L'intervalle de preference doit verifier 0 <= lower <= upper <= 1.")


GenrePreferenceValue: TypeAlias = float | LinguisticGenrePreference | IntervalGenrePreference


@dataclass(frozen=True)
class GenrePreferenceMatch:
    """Preference agregee pour les genres d'un film."""

    value: GenrePreferenceValue | None
    known: bool
    matched_genres: tuple[str, ...] = ()
    aggregation: str = "mean"


@dataclass(frozen=True)
class GenrePreference:
    """Preference utilisateur associee a un genre MovieLens.

    Attributes:
        genre: Nom du genre, par exemple `Sci-Fi` ou `Comedy`.
        value: Intensite crisp, terme linguistique ou intervalle imprecis.
    """

    genre: str
    value: GenrePreferenceValue | None = None


@dataclass
class UserProfile:
    """Profil flou d'un utilisateur.

    Attributes:
        user_id: Identifiant MovieLens ou identifiant local.
        genre_preferences: Preferences par genre.
        recency_preference: Champ reserve pour une version future.
        popularity_importance: Champ reserve pour ponderer la popularite.

    Le profil V1 est volontairement leger : il porte uniquement les preferences
    par genre et fournit des helpers pour le pre-filtrage et le scoring.
    """

    user_id: int | None = None
    genre_preferences: dict[str, GenrePreference] = field(default_factory=dict)
    recency_preference: float | None = None
    popularity_importance: float | None = None
    genre_aggregation: str = "mean"

    def set_genre_preference(self, preference: GenrePreference) -> None:
        """Ajouter ou remplacer une preference par genre.
        """

        if not preference.genre.strip():
            raise ValueError("Le genre ne peut pas etre vide.")
        if isinstance(preference.value, float) and not 0.0 <= preference.value <= 1.0:
            raise ValueError("La preference de genre doit appartenir a [0, 1].")
        self.genre_preferences[preference.genre] = preference

    def preferred_genres(self, threshold: float = 0.5) -> list[str]:
        """Retourner les genres dont la preference atteint le seuil donne."""

        return [
            preference.genre
            for preference in self.genre_preferences.values()
            if _preference_strength(preference.value) >= threshold
        ]

    def genre_preference_for_movie(self, movie_genres: list[str], aggregation: str | None = None) -> GenrePreferenceMatch:
        """Calculer une preference de genre pour un film.

        La V1 agrege par defaut la force moyenne des genres du film declares
        dans le profil. `known=False` distingue explicitement un film dont
        aucun genre n'est present dans le profil d'une vraie preference faible.
        """

        if not self.genre_preferences:
            return GenrePreferenceMatch(value=None, known=False, aggregation=aggregation or self.genre_aggregation)

        strategy = aggregation or self.genre_aggregation
        if strategy not in {"mean", "max"}:
            raise ValueError("L'agregation de genres supporte uniquement 'mean' ou 'max'.")

        preferences_by_genre = {
            genre.casefold().strip(): preference.value
            for genre, preference in self.genre_preferences.items()
            if preference.value is not None
        }
        matching_pairs = [
            (genre, preferences_by_genre[genre.casefold().strip()])
            for genre in movie_genres
            if genre.casefold().strip() in preferences_by_genre
        ]
        if not matching_pairs:
            return GenrePreferenceMatch(value=None, known=False, aggregation=strategy)

        matched_genres = tuple(genre for genre, _ in matching_pairs)
        matching_values = [value for _, value in matching_pairs]
        if len(matching_values) == 1:
            return GenrePreferenceMatch(
                value=matching_values[0],
                known=True,
                matched_genres=matched_genres,
                aggregation=strategy,
            )
        if strategy == "max":
            value = max(matching_values, key=_preference_strength)
            return GenrePreferenceMatch(value=value, known=True, matched_genres=matched_genres, aggregation=strategy)

        strengths = [_preference_strength(value) for value in matching_values]
        return GenrePreferenceMatch(
            value=sum(strengths) / len(strengths),
            known=True,
            matched_genres=matched_genres,
            aggregation=strategy,
        )


def preference_strength(value: GenrePreferenceValue | None) -> float:
    if value is None:
        return 0.0
    if isinstance(value, float):
        return value
    if isinstance(value, IntervalGenrePreference):
        return value.upper
    normalised = value.term.casefold().replace(" ", "_").replace("-", "_")
    term_strengths = {
        "pas_du_tout": 0.0,
        "faible": 0.25,
        "un_peu": 0.35,
        "moyen": 0.5,
        "moyenne": 0.5,
        "beaucoup": 0.8,
        "fort": 1.0,
        "forte": 1.0,
    }
    return term_strengths.get(normalised, 0.0)


def _preference_strength(value: GenrePreferenceValue | None) -> float:
    return preference_strength(value)
