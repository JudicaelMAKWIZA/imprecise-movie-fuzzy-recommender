"""Profil utilisateur flou."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GenrePreference:
    """Preference utilisateur associee a un genre MovieLens.

    Attributes:
        genre: Nom du genre, par exemple `Sci-Fi` ou `Comedy`.
        value: Intensite crisp dans `[0, 1]`, a fuzzifier ensuite.
        label: Libelle optionnel saisi par l'utilisateur, comme `beaucoup`.

    `value` est l'intensite crisp utilisee par la fuzzification. Le libelle est
    conserve pour l'interface et les explications futures.
    """

    genre: str
    value: float | None = None
    label: str | None = None


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

    def set_genre_preference(self, preference: GenrePreference) -> None:
        """Ajouter ou remplacer une preference par genre.
        """

        if not preference.genre.strip():
            raise ValueError("Le genre ne peut pas etre vide.")
        if preference.value is not None and not 0.0 <= preference.value <= 1.0:
            raise ValueError("La preference de genre doit appartenir a [0, 1].")
        self.genre_preferences[preference.genre] = preference

    def preferred_genres(self, threshold: float = 0.5) -> list[str]:
        """Retourner les genres dont la preference atteint le seuil donne."""

        return [
            preference.genre
            for preference in self.genre_preferences.values()
            if preference.value is not None and preference.value >= threshold
        ]

    def genre_preference_for_movie(self, movie_genres: list[str]) -> float:
        """Calculer une preference crisp pour un film.

        La V1 utilise la preference maximale parmi les genres du film. Si le
        profil ne contient aucune preference, la valeur neutre `0.5` est
        retournee. Si le profil contient des preferences mais aucune ne concerne
        le film, la valeur est `0.0`.
        """

        if not self.genre_preferences:
            return 0.5

        preferences_by_genre = {
            genre.casefold().strip(): preference.value
            for genre, preference in self.genre_preferences.items()
            if preference.value is not None
        }
        matching_values = [
            preferences_by_genre[genre.casefold().strip()]
            for genre in movie_genres
            if genre.casefold().strip() in preferences_by_genre
        ]
        return max(matching_values, default=0.0)
