"""Orchestration de l'evaluation du systeme."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Iterable
from typing import TYPE_CHECKING

from pandas import DataFrame

from .metrics import coverage, diversity_score, precision_at_n, recall_at_n

if TYPE_CHECKING:
    from recommender.fuzzy_recommender import FuzzyRecommender


@dataclass
class EvaluationReport:
    """Rapport structure des scores d'evaluation.

    Attributes:
        metrics: Valeurs numeriques par nom de metrique.
        notes: Commentaires qualitatifs ou limites de l'experience.

    Le rapport reste volontairement simple et serialisable.
    """

    metrics: dict[str, float] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


@dataclass
class Evaluator:
    """Service responsable du protocole d'evaluation.

    Ce service couvre l'evaluation simple necessaire a la V1 demonstrable. Les
    protocoles train/test plus avances seront ajoutes lorsque la recommandation
    sera branchee aux historiques utilisateurs.
    """

    top_n: int = 10

    def evaluate_lists(
        self,
        recommended: Iterable[int],
        relevant: Iterable[int],
        full_catalog: Iterable[int],
        genres_by_movie: dict[int, set[str]] | None = None,
    ) -> EvaluationReport:
        """Evaluer une liste de recommandations deja produite."""

        recommended_list = list(recommended)
        relevant_list = list(relevant)
        report = EvaluationReport(
            metrics={
                "precision_at_n": precision_at_n(recommended_list, relevant_list, self.top_n),
                "recall_at_n": recall_at_n(recommended_list, relevant_list, self.top_n),
                "coverage": coverage(recommended_list, full_catalog),
                "diversity": diversity_score(recommended_list[: self.top_n], genres_by_movie),
            }
        )
        if not relevant_list:
            report.notes.append("Aucun film pertinent fourni ; le rappel vaut 0.0 par convention.")
        return report

    def evaluate_user(
        self,
        *,
        user_id: int,
        raw_data: dict[str, DataFrame],
        recommender: FuzzyRecommender,
        test_ratio: float = 0.2,
        relevance_threshold: float = 4.0,
    ) -> EvaluationReport:
        """Evaluer un utilisateur avec decoupage temporel train/test.

        Les notes de l'utilisateur sont triees par `timestamp`. Les premieres
        notes construisent le profil, les plus recentes forment la verite-terrain.
        """

        if not 0.0 < test_ratio < 1.0:
            raise ValueError("test_ratio doit appartenir a ]0, 1[.")
        train_user_ratings, test_user_ratings = _split_user_ratings(
            raw_data["ratings"],
            user_id=user_id,
            test_ratio=test_ratio,
        )
        user_ratings_count = len(train_user_ratings) + len(test_user_ratings)
        if user_ratings_count < 2:
            return EvaluationReport(notes=["Evaluation impossible: moins de deux notes pour cet utilisateur."])

        ratings = raw_data["ratings"]
        train_ratings = ratings.loc[ratings["userId"] != user_id]
        train_ratings = DataFrame([*train_ratings.to_dict("records"), *train_user_ratings.to_dict("records")])
        from recommender.fuzzy_recommender import PrefilterEmptyError
        from recommender.pipeline_factory import build_profile

        train_raw_data = {**raw_data, "ratings": train_ratings}
        profile = build_profile(user_id=user_id, raw_data=train_raw_data)
        try:
            recommendations = recommender.recommend(profile, top_n=self.top_n)
        except PrefilterEmptyError as exc:
            report = EvaluationReport(notes=[str(exc)])
            report.metrics = {
                "precision_at_n": 0.0,
                "recall_at_n": 0.0,
                "coverage": 0.0,
                "diversity": 0.0,
            }
            return report
        recommended_ids = [recommendation.movie.movie_id for recommendation in recommendations]
        relevant_ids = test_user_ratings.loc[
            test_user_ratings["rating"] >= relevance_threshold,
            "movieId",
        ].astype(int).tolist()
        full_catalog = raw_data["movies"]["movieId"].astype(int).tolist()
        genres_by_movie = {
            movie.movie_id: set(movie.genre_list)
            for movie in recommender.repository.movies
            if movie.movie_id in recommended_ids
        }
        report = self.evaluate_lists(recommended_ids, relevant_ids, full_catalog, genres_by_movie)
        report.notes.append(
            f"Decoupage temporel user_id={user_id}: train={len(train_user_ratings)}, test={len(test_user_ratings)}."
        )
        return report

    def evaluate(self) -> EvaluationReport:
        """Retourner un rapport vide explicite pour l'orchestration future."""

        return EvaluationReport(notes=["Evaluation complete non branchee aux donnees utilisateurs en V1."])


def _split_user_ratings(ratings: DataFrame, *, user_id: int, test_ratio: float) -> tuple[DataFrame, DataFrame]:
    user_ratings = ratings.loc[ratings["userId"] == user_id].sort_values("timestamp")
    if len(user_ratings) < 2:
        return user_ratings, user_ratings.iloc[0:0]
    test_size = max(1, int(round(len(user_ratings) * test_ratio)))
    train_user_ratings = user_ratings.iloc[:-test_size]
    test_user_ratings = user_ratings.iloc[-test_size:]
    if train_user_ratings.empty:
        train_user_ratings = user_ratings.iloc[:1]
        test_user_ratings = user_ratings.iloc[1:]
    return train_user_ratings, test_user_ratings
