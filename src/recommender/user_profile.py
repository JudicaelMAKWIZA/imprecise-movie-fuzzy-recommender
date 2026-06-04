"""Profil utilisateur flou.

Le profil utilisateur represente les preferences linguistiques, notamment les
preferences par genre pour la V1. Les valeurs numeriques restent crisp tant que
la fuzzification n'a pas ete appliquee par `Fuzzifier`.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GenrePreference:
    """Preference utilisateur associee a un genre MovieLens.

    Attributes:
        genre: Nom du genre, par exemple `Sci-Fi` ou `Comedy`.
        value: Intensite crisp dans `[0, 1]`, a fuzzifier ensuite.
        label: Libelle optionnel saisi par l'utilisateur, comme `beaucoup`.

    TODO:
        - Mapper les libelles linguistiques vers des valeurs crisp.
        - Valider les genres disponibles dans le dataset.
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

    TODO:
        - Construire un profil depuis les notes historiques.
        - Construire un profil depuis des choix CLI ou GUI.
        - Serialiser le profil pour reutilisation.
    """

    user_id: int | None = None
    genre_preferences: dict[str, GenrePreference] = field(default_factory=dict)
    recency_preference: float | None = None
    popularity_importance: float | None = None

    def set_genre_preference(self, preference: GenrePreference) -> None:
        """Ajouter ou remplacer une preference par genre.

        TODO:
            Valider la valeur, le genre et le libelle linguistique.
        """

        raise NotImplementedError("TODO: modifier une preference de genre.")
