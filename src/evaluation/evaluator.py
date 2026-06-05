"""Orchestration de l'evaluation du systeme."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Iterable

from .metrics import coverage, diversity_score, precision_at_n, recall_at_n


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

    def evaluate(self) -> EvaluationReport:
        """Retourner un rapport vide explicite pour l'orchestration future."""

        return EvaluationReport(notes=["Evaluation complete non branchee aux donnees utilisateurs en V1."])
