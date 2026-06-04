"""Orchestration de l'evaluation du systeme."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EvaluationReport:
    """Rapport structure des scores d'evaluation.

    Attributes:
        metrics: Valeurs numeriques par nom de metrique.
        notes: Commentaires qualitatifs ou limites de l'experience.

    TODO:
        Ajouter l'export JSON pour la CLI.
    """

    metrics: dict[str, float] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


@dataclass
class Evaluator:
    """Service responsable du protocole d'evaluation.

    TODO:
        - Diviser les donnees en train/test.
        - Generer des recommandations Top-N.
        - Comparer avec les notes reelles.
        - Comparer avec une baseline de popularite.
    """

    top_n: int = 10

    def evaluate(self) -> EvaluationReport:
        """Executer le protocole d'evaluation complet."""

        raise NotImplementedError("TODO: implementer l'evaluation complete.")
