"""Moteur principal de recommandation floue.

Cette couche assemble l'Architecture B officielle :
pre-filtrage par genre, FIS Mamdani multi-criteres, tri Top-N, puis
explications. Elle ne doit pas contenir les formules floues ; elle orchestre les
services specialises.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from data_manager.movie_repository import MovieRepository
from data_manager.schemas import MovieFeatures
from fuzzy.defuzzification import Defuzzifier
from fuzzy.fuzzifier import Fuzzifier
from fuzzy.inference_engine import InferenceResult, MamdaniInferenceEngine
from fuzzy.linguistic_variables import LinguisticVariable, build_recommendation_score_variable
from recommender.user_profile import UserProfile


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
    preferred_genre_threshold: float = 0.5
    neutral_average_rating: float = 3.5

    def recommend(self, profile: UserProfile, top_n: int = 10) -> list[Recommendation]:
        """Produire une liste Top-N de recommandations.
        """

        if top_n <= 0:
            raise ValueError("top_n doit etre strictement positif.")

        recommendations = [self.score_movie(profile, movie) for movie in self.prefilter_candidates(profile)]
        recommendations.sort(
            key=lambda recommendation: (
                -(recommendation.score if recommendation.score is not None else -1.0),
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

    def prefilter_candidates(self, profile: UserProfile) -> list[MovieFeatures]:
        """Pre-filtrer les films selon les genres preferes.
        """

        preferred_genres = profile.preferred_genres(threshold=self.preferred_genre_threshold)
        if not preferred_genres:
            return []
        return self.repository.filter_by_genres(preferred_genres)

    def _build_crisp_inputs(self, profile: UserProfile, movie: MovieFeatures) -> dict[str, object]:
        average_rating = movie.average_rating if movie.average_rating is not None else self.neutral_average_rating
        popularity = movie.number_of_ratings if movie.number_of_ratings is not None else 0
        return {
            "genre_preference": profile.genre_preference_for_movie(movie.genre_list),
            "average_rating": max(0.5, min(5.0, float(average_rating))),
            "popularity": max(0.0, min(350.0, float(popularity))),
        }
