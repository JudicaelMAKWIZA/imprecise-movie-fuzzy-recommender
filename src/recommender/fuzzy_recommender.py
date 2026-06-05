"""Moteur principal de recommandation floue.

Cette couche assemble l'Architecture B officielle :
pre-filtrage par genre, FIS Mamdani multi-criteres, tri Top-N, puis
explications. Elle ne doit pas contenir les formules floues ; elle orchestre les
services specialises.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Mapping

from data_manager.movie_repository import MovieRepository
from data_manager.schemas import MovieFeatures
from fuzzy.defuzzification import Defuzzifier
from fuzzy.fuzzifier import Fuzzifier
from fuzzy.inference_engine import InferenceResult, MamdaniInferenceEngine
from fuzzy.linguistic_variables import LinguisticVariable, build_recommendation_score_variable
from recommender.user_profile import GenrePreferenceMatch, UserProfile, preference_strength


@dataclass(frozen=True)
class PrefilterResult:
    """Resultat explicite du pre-filtrage par genres."""

    candidates: list[MovieFeatures]
    preferred_genres: list[str]
    threshold: float
    reason: str = ""


class PrefilterEmptyError(ValueError):
    """Erreur levee quand le pre-filtrage ne produit aucun candidat."""

    def __init__(self, result: PrefilterResult, preferences: Mapping[str, object]) -> None:
        self.result = result
        self.preferences = dict(preferences)
        message = _render_prefilter_message(result, self.preferences)
        super().__init__(message)


@dataclass(frozen=True)
class Recommendation:
    """Resultat de recommandation pour un film.

    Attributes:
        movie: Film recommande.
        score: Score crisp final dans `[0, 1]`.
        inference: Trace d'inference permettant l'explication.
        fuzzy_inputs: Entrees fuzzifiees ayant produit le score.
        crisp_inputs: Valeurs derivees du profil et du film.
    """

    movie: MovieFeatures
    score: float | None
    inference: InferenceResult | None = None
    fuzzy_inputs: Mapping[str, Mapping[str, float]] = field(default_factory=dict)
    crisp_inputs: Mapping[str, object] = field(default_factory=dict)


@dataclass
class FuzzyRecommender:
    """Facade de recommandation pour la CLI, la GUI et les tests.

    Attributes:
        repository: Acces aux films pretraites.
        fuzzifier: Service de conversion crisp vers degres flous.
        inference_engine: Moteur Mamdani.
        defuzzifier: Convertisseur de la sortie floue en score crisp.
    """

    repository: MovieRepository
    fuzzifier: Fuzzifier
    inference_engine: MamdaniInferenceEngine
    defuzzifier: Defuzzifier = field(default_factory=Defuzzifier)
    output_variable: LinguisticVariable = field(default_factory=build_recommendation_score_variable)
    preferred_genre_threshold: float = 0.2
    neutral_average_rating: float = 3.5
    not_covered: list[Recommendation] = field(default_factory=list, init=False)

    def with_repository(self, repository: MovieRepository) -> FuzzyRecommender:
        """Retourner une facade equivalente branchee sur un autre repository."""

        return replace(self, repository=repository)

    def recommend(self, profile: UserProfile, top_n: int = 10) -> list[Recommendation]:
        """Produire une liste Top-N de recommandations.
        """

        if top_n <= 0:
            raise ValueError("top_n doit etre strictement positif.")

        prefilter_result = self.prefilter_candidates(profile)
        if not prefilter_result.candidates:
            raise PrefilterEmptyError(prefilter_result, _profile_preferences(profile))

        scored = [self.score_movie(profile, movie) for movie in prefilter_result.candidates]
        self.not_covered = [recommendation for recommendation in scored if recommendation.score is None]
        recommendations = [recommendation for recommendation in scored if recommendation.score is not None]
        recommendations.sort(
            key=lambda recommendation: (
                -float(recommendation.score),
                -(recommendation.movie.number_of_ratings or 0),
                -(recommendation.movie.average_rating or 0.0),
                recommendation.movie.title.casefold(),
            )
        )
        return recommendations[:top_n]

    def score_movie(self, profile: UserProfile, movie: MovieFeatures) -> Recommendation:
        """Calculer le score flou d'un film candidat.
        """

        crisp_inputs = self._build_crisp_inputs(profile, movie)
        if isinstance(crisp_inputs["genre_preference"], GenrePreferenceMatch) or crisp_inputs["popularity"] is None:
            return Recommendation(movie=movie, score=None, inference=None, crisp_inputs=crisp_inputs)
        fuzzy_inputs = self.fuzzifier.fuzzify_inputs(
            user_inputs={"genre_preference": crisp_inputs["genre_preference"]},
            movie_inputs={
                "average_rating": crisp_inputs["average_rating"],
                "popularity": crisp_inputs["popularity"],
            },
        )
        inference = self.inference_engine.infer(fuzzy_inputs)
        score = self.defuzzifier.defuzzify(
            dict(inference.output_memberships),
            variable=self.output_variable,
        )
        inference.crisp_score = score
        return Recommendation(
            movie=movie,
            score=score,
            inference=inference,
            fuzzy_inputs=fuzzy_inputs,
            crisp_inputs=crisp_inputs,
        )

    def prefilter_candidates(self, profile: UserProfile) -> PrefilterResult:
        """Pre-filtrer les films selon les genres preferes.
        """

        preferred_genres = profile.preferred_genres(threshold=self.preferred_genre_threshold)
        if not preferred_genres:
            return PrefilterResult(
                candidates=[],
                preferred_genres=[],
                threshold=self.preferred_genre_threshold,
                reason="Aucun genre n'atteint le seuil de prefiltrage.",
            )
        candidates = [
            movie
            for movie in self.repository.filter_by_genres(preferred_genres)
            if movie.number_of_ratings is not None
        ]
        reason = "" if candidates else "Aucun film avec popularite connue ne correspond aux genres preferes."
        return PrefilterResult(
            candidates=candidates,
            preferred_genres=preferred_genres,
            threshold=self.preferred_genre_threshold,
            reason=reason,
        )

    def _build_crisp_inputs(self, profile: UserProfile, movie: MovieFeatures) -> dict[str, object]:
        genre_match = profile.genre_preference_for_movie(movie.genre_list)
        average_rating = movie.average_rating if movie.average_rating is not None else self.neutral_average_rating
        popularity = movie.number_of_ratings
        if not genre_match.known or popularity is None:
            return {
                "genre_preference": genre_match,
                "average_rating": max(0.5, min(5.0, float(average_rating))),
                "popularity": None,
            }
        return {
            "genre_preference": genre_match.value,
            "average_rating": max(0.5, min(5.0, float(average_rating))),
            "popularity": max(0.0, min(350.0, float(popularity))),
        }


def _profile_preferences(profile: UserProfile) -> dict[str, float]:
    return {
        preference.genre: preference_strength(preference.value)
        for preference in profile.genre_preferences.values()
    }


def _render_prefilter_message(result: PrefilterResult, preferences: Mapping[str, object]) -> str:
    rendered_preferences = ", ".join(
        f"{genre}={float(strength):.3f}" if isinstance(strength, int | float) else f"{genre}={strength}"
        for genre, strength in preferences.items()
    ) or "aucune"
    reason = f" {result.reason}" if result.reason else ""
    return (
        "Aucun candidat apres prefiltrage."
        f"{reason} Seuil utilise: {result.threshold:.3f}. "
        f"Preferences saisies: {rendered_preferences}. "
        "Augmentez au moins une preference de genre ou abaissez le seuil de prefiltrage."
    )
