"""Moteur d'inference Mamdani.

Ce module transforme une base de regles declarative et des entrees deja
fuzzifiees en sorties floues agregees. La defuzzification reste volontairement
hors de cette classe : le moteur produit une sortie linguistique interpretable
et les traces necessaires aux futures explications.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Mapping

from .aggregation import ConsequentAggregator
from .rule_base import FuzzyRule, RuleBase

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RuleActivation:
    """Trace d'activation d'une regle floue.

    Attributes:
        rule: Regle concernee.
        degree: Degre d'activation calcule par la t-norme.
        antecedent_degrees: Degres effectivement lus pour chaque antecedent,
            indexes par variable. Le terme linguistique associe reste visible
            dans `rule.antecedents`.
    """

    rule: FuzzyRule
    degree: float
    antecedent_degrees: Mapping[str, float] = field(default_factory=dict)

    @property
    def is_active(self) -> bool:
        """Indiquer si la regle contribue a la sortie agregee."""

        return self.degree > 0.0

    @property
    def consequent_term(self) -> str:
        """Terme de sortie active par la regle."""

        return self.rule.consequent.term


@dataclass
class InferenceResult:
    """Resultat structure d'une inference Mamdani.

    Attributes:
        crisp_score: Score defuzzifie dans `[0, 1]`.
        output_memberships: Degres agregees de la variable de sortie.
        activated_rules: Regles activees et degres associes.
        evaluated_rules: Trace complete des regles evaluees, y compris celles
            dont le degre d'activation vaut zero.
        output_variable: Nom de la variable de sortie floue.
    """

    crisp_score: float | None = None
    output_memberships: Mapping[str, float] = field(default_factory=dict)
    activated_rules: list[RuleActivation] = field(default_factory=list)
    evaluated_rules: list[RuleActivation] = field(default_factory=list)
    output_variable: str = "recommendation_score"


@dataclass
class MamdaniInferenceEngine:
    """Moteur d'inference floue de type Mamdani.

    Attributes:
        rule_base: Base de regles a evaluer.

    Le moteur applique :

    1. activation de chaque antecedent depuis les entrees fuzzifiees ;
    2. operateur `AND` par minimum ;
    3. implication Mamdani sous forme de consequent coupe au degre
       d'activation ;
    4. aggregation des consequents par maximum ;
    5. construction d'une trace exploitable par l'explicabilite.
    """

    rule_base: RuleBase

    def infer(self, fuzzy_inputs: Mapping[str, Mapping[str, float]]) -> InferenceResult:
        """Executer une inference sur des entrees deja fuzzifiees.

        Args:
            fuzzy_inputs: Degres d'appartenance par variable et par terme.

        Returns:
            Un `InferenceResult` contenant la sortie floue agregee et la trace
            des regles. `crisp_score` reste `None` tant que la defuzzification
            n'est pas appliquee.
        """

        self.rule_base.validate()
        self._validate_fuzzy_inputs(fuzzy_inputs)

        evaluated_rules = [self.activate_rule(rule, fuzzy_inputs) for rule in self.rule_base]
        activated_rules = [activation for activation in evaluated_rules if activation.is_active]
        output_memberships = self.aggregate_consequents(activated_rules)
        output_variable = self._resolve_output_variable()

        logger.info(
            "Inference Mamdani terminee: rules=%s active=%s output=%s",
            len(evaluated_rules),
            len(activated_rules),
            output_memberships,
        )
        return InferenceResult(
            crisp_score=None,
            output_memberships=output_memberships,
            activated_rules=activated_rules,
            evaluated_rules=evaluated_rules,
            output_variable=output_variable,
        )

    def activate_rule(
        self,
        rule: FuzzyRule,
        fuzzy_inputs: Mapping[str, Mapping[str, float]],
    ) -> RuleActivation:
        """Calculer le degre d'activation d'une regle.

        Les antecedents sont combines par l'operateur `AND` de Mamdani, ici la
        t-norme minimum. Une variable ou un terme absent des entrees fuzzifiees
        est interprete comme un degre nul.
        """

        antecedent_degrees = {
            antecedent.variable: self._membership_degree(fuzzy_inputs, antecedent.variable, antecedent.term)
            for antecedent in rule.antecedents
        }
        activation_degree = min(antecedent_degrees.values()) if antecedent_degrees else 0.0
        logger.debug(
            "Activation regle %s: antecedents=%s degree=%s",
            rule.identifier,
            antecedent_degrees,
            activation_degree,
        )
        return RuleActivation(rule=rule, degree=activation_degree, antecedent_degrees=antecedent_degrees)

    def imply_consequent(self, activation: RuleActivation) -> dict[str, float]:
        """Appliquer l'implication Mamdani a une activation de regle.

        Dans la representation symbolique actuelle, l'implication correspond a
        couper le terme consequent au degre d'activation de la regle. La forme
        continue de l'ensemble de sortie sera utilisee pendant la defuzzification
        future.
        """

        if not activation.is_active:
            return {}
        return {activation.consequent_term: activation.degree}

    def aggregate_consequents(self, activations: list[RuleActivation]) -> dict[str, float]:
        """Agreger les consequents actifs par maximum."""

        return ConsequentAggregator().aggregate(activations)

    @staticmethod
    def _membership_degree(
        fuzzy_inputs: Mapping[str, Mapping[str, float]],
        variable: str,
        term: str,
    ) -> float:
        return float(fuzzy_inputs.get(variable, {}).get(term, 0.0))

    @staticmethod
    def _validate_fuzzy_inputs(fuzzy_inputs: Mapping[str, Mapping[str, float]]) -> None:
        for variable, terms in fuzzy_inputs.items():
            if not isinstance(terms, Mapping):
                raise TypeError(f"Les degres de {variable} doivent etre un mapping de termes.")
            for term, degree in terms.items():
                numeric_degree = float(degree)
                if not 0.0 <= numeric_degree <= 1.0:
                    raise ValueError(
                        f"Le degre d'appartenance {variable}.{term}={degree} est hors de l'intervalle [0, 1]."
                    )

    def _resolve_output_variable(self) -> str:
        output_variables = {rule.consequent.variable for rule in self.rule_base}
        if len(output_variables) == 1:
            return next(iter(output_variables))
        if not output_variables:
            return "recommendation_score"
        raise ValueError(f"Une inference ne peut pas melanger plusieurs sorties: {sorted(output_variables)}")
