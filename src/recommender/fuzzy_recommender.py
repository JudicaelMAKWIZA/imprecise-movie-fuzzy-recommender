"""Moteur principal de recommandation floue.

Cette couche assemble l'Architecture B officielle :
pre-filtrage par genre, FIS Mamdani multi-criteres, tri Top-N, puis
explications. Elle ne doit pas contenir les formules floues ; elle orchestre les
services specialises.
"""

from __future__ import annotations

from dataclasses import dataclass

from data.movie_repository import MovieRepository
from data.schemas import MovieFeatures
from fuzzy.fuzzification import Fuzzifier
from fuzzy.inference_engine import InferenceResult, MamdaniInferenceEngine
from recommender.user_profile import UserProfile


@dataclass(frozen=True)
class Recommendation:
    """Resultat de recommandation pour un film.

    Attributes:
        movie: Film recommande.
        score: Score crisp final dans `[0, 1]`.
        inference: Trace d'inference permettant l'explication.

    TODO:
        Ajouter un champ `explanation` lorsque le moteur d'explications sera
        branche au pipeline.
    """

    movie: MovieFeatures
    score: float | None
    inference: InferenceResult | None = None


@dataclass
class FuzzyRecommender:
    """Facade de recommandation pour la CLI, la GUI et les tests.

    Attributes:
        repository: Acces aux films pretraites.
        fuzzifier: Service de conversion crisp vers degres flous.
        inference_engine: Moteur Mamdani.

    TODO:
        - Implementer le pre-filtrage par genre.
        - Scorer chaque film candidat par le FIS.
        - Trier et retourner les Top-N.
        - Conserver les traces necessaires aux explications.
    """

    repository: MovieRepository
    fuzzifier: Fuzzifier
    inference_engine: MamdaniInferenceEngine

    def recommend(self, profile: UserProfile, top_n: int = 10) -> list[Recommendation]:
        """Produire une liste Top-N de recommandations.

        TODO:
            Orchestrer l'Architecture B complete apres implementation du FIS.
        """

        raise NotImplementedError("TODO: implementer la recommandation Top-N.")

    def score_movie(self, profile: UserProfile, movie: MovieFeatures) -> Recommendation:
        """Calculer le score flou d'un film candidat.

        TODO:
            Fuzzifier les entrees, appeler Mamdani, puis encapsuler le resultat.
        """

        raise NotImplementedError("TODO: scorer un film avec le FIS.")

    def prefilter_candidates(self, profile: UserProfile) -> list[MovieFeatures]:
        """Pre-filtrer les films selon les genres preferes.

        TODO:
            Appliquer le pre-filtrage crisp de l'Architecture B.
        """

        raise NotImplementedError("TODO: pre-filtrer les candidats.")
