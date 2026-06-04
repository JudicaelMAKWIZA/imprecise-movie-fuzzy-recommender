"""Moteur d'inference Mamdani.

Ce module sera le coeur scientifique du projet. Il devra appliquer la sequence :
fuzzification, activation des regles, implication Mamdani, agregation des
consequents, puis defuzzification.

La version actuelle expose seulement les types de trace et la classe du moteur.
Elle ne contient aucune implementation du raisonnement flou.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .rule_base import FuzzyRule, RuleBase


@dataclass(frozen=True)
class RuleActivation:
    """Trace d'activation d'une regle floue.

    Attributes:
        rule: Regle concernee.
        degree: Degre d'activation calcule par la t-norme.

    TODO:
        Ajouter les degres par antecedent pour enrichir les explications.
    """

    rule: FuzzyRule
    degree: float


@dataclass
class InferenceResult:
    """Resultat structure d'une inference Mamdani.

    Attributes:
        crisp_score: Score defuzzifie dans `[0, 1]`.
        output_memberships: Degres agregees de la variable de sortie.
        activated_rules: Regles activees et degres associes.

    TODO:
        Ajouter les donnees necessaires aux visualisations de defuzzification.
    """

    crisp_score: float | None = None
    output_memberships: Mapping[str, float] = field(default_factory=dict)
    activated_rules: list[RuleActivation] = field(default_factory=list)


@dataclass
class MamdaniInferenceEngine:
    """Moteur d'inference floue de type Mamdani.

    Attributes:
        rule_base: Base de regles a evaluer.

    TODO:
        - Implementer l'activation des antecedents par t-norme min.
        - Implementer l'implication Mamdani.
        - Deleguer l'agregation et la defuzzification aux modules dedies.
        - Produire une trace complete pour `ExplanationEngine`.
    """

    rule_base: RuleBase

    def infer(self, fuzzy_inputs: Mapping[str, Mapping[str, float]]) -> InferenceResult:
        """Executer une inference sur des entrees deja fuzzifiees.

        Args:
            fuzzy_inputs: Degres d'appartenance par variable et par terme.

        Returns:
            Un `InferenceResult` contenant le score et la trace des regles.

        TODO:
            Implementer le pipeline Mamdani complet sans dependance externe.
        """

        raise NotImplementedError("TODO: implementer le moteur Mamdani.")
