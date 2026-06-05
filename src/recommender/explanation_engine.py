"""Generation d'explications de recommandations.

L'explicabilite est obligatoire dans les decisions architecturales. Ce module
transforme les traces d'inference Mamdani en explications structurees et en
texte lisible : degres linguistiques, regles activees, contribution des
criteres et score defuzzifie.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from data_manager.schemas import MovieFeatures
from fuzzy.inference_engine import InferenceResult, RuleActivation
from recommender.user_profile import UserProfile


VARIABLE_LABELS = {
    "genre_preference": "preference de genre",
    "average_rating": "note moyenne",
    "popularity": "popularite",
}

TERM_LABELS = {
    "faible": "faible",
    "moyenne": "moyenne",
    "forte": "forte",
    "mauvaise": "mauvaise",
    "correcte": "correcte",
    "bonne": "bonne",
    "excellente": "excellente",
    "confidentiel": "confidentiel",
    "modere": "modere",
    "populaire": "populaire",
    "tres_populaire": "tres populaire",
    "tres_faible": "tres faible",
    "moyen": "moyen",
    "fort": "fort",
    "tres_fort": "tres fort",
}

VARIABLE_ORDER = ("genre_preference", "average_rating", "popularity")


@dataclass(frozen=True)
class ExplanationCriterion:
    """Element explicatif lie a une variable d'entree.

    Attributes:
        name: Nom du critere, par exemple `genre_preference`.
        dominant_term: Terme linguistique dominant.
        degree: Degre d'appartenance associe.
        raw_value: Valeur crisp d'origine si disponible.
    """

    name: str
    dominant_term: str
    degree: float
    raw_value: float | int | str | None = None


@dataclass
class RecommendationExplanation:
    """Explication structuree d'une recommandation.

    Attributes:
        movie: Film explique.
        score: Score final defuzzifie.
        criteria: Criteres dominants ayant contribue au score.
        activated_rules: Regles retenues apres filtrage du seuil.
        output_memberships: Degres agreges de la sortie Mamdani.
        dominant_output_term: Terme de sortie le plus actif.
        text: Version textuelle optionnelle pour CLI ou GUI.
    """

    movie: MovieFeatures
    score: float | None
    criteria: list[ExplanationCriterion] = field(default_factory=list)
    activated_rules: list[RuleActivation] = field(default_factory=list)
    output_memberships: Mapping[str, float] = field(default_factory=dict)
    dominant_output_term: str | None = None
    text: str | None = None


@dataclass
class ExplanationEngine:
    """Service de transformation des traces floues en explications.

    Attributes:
        activation_threshold: Seuil minimal pour afficher une regle activee.

    Les explications sont construites uniquement a partir des traces deja
    produites par le moteur Mamdani : aucune regle n'est recalculee ici. Le
    service reste donc une couche de presentation et d'interpretation.
    """

    activation_threshold: float = 0.1

    def __post_init__(self) -> None:
        if not 0.0 <= self.activation_threshold <= 1.0:
            raise ValueError("activation_threshold doit appartenir a [0, 1].")

    def explain(
        self,
        profile: UserProfile,
        movie: MovieFeatures,
        inference: InferenceResult,
        crisp_inputs: Mapping[str, float] | None = None,
        fuzzy_inputs: Mapping[str, Mapping[str, float]] | None = None,
    ) -> RecommendationExplanation:
        """Construire une explication structuree.

        Args:
            profile: Profil utilisateur ayant produit la recommandation.
            movie: Film recommande ou score.
            inference: Resultat Mamdani contenant les regles evaluees.
            crisp_inputs: Valeurs numeriques avant fuzzification, si
                disponibles.
            fuzzy_inputs: Degres d'appartenance par variable et terme, si
                disponibles.

        Returns:
            Une explication structuree et son rendu textuel.
        """

        del profile  # Le profil est conserve dans la signature publique V1.
        selected_rules = [
            activation
            for activation in inference.activated_rules
            if activation.degree > self.activation_threshold
        ]
        criteria = self._build_criteria(
            inference=inference,
            crisp_inputs=crisp_inputs or {},
            fuzzy_inputs=fuzzy_inputs or {},
        )
        dominant_output_term = self._dominant_term(inference.output_memberships)
        explanation = RecommendationExplanation(
            movie=movie,
            score=inference.crisp_score,
            criteria=criteria,
            activated_rules=selected_rules,
            output_memberships=dict(inference.output_memberships),
            dominant_output_term=dominant_output_term,
        )
        explanation.text = self.render_text(explanation)
        return explanation

    def explain_recommendation(
        self,
        profile: UserProfile,
        recommendation: object,
    ) -> RecommendationExplanation:
        """Construire l'explication d'un objet `Recommendation`.

        La methode accepte un objet structurel pour eviter un couplage dur avec
        `fuzzy_recommender` et conserver une dependance a sens unique.
        """

        inference = getattr(recommendation, "inference", None)
        if inference is None:
            raise ValueError("La recommandation ne contient pas de trace d'inference.")
        return self.explain(
            profile=profile,
            movie=getattr(recommendation, "movie"),
            inference=inference,
            crisp_inputs=getattr(recommendation, "crisp_inputs", {}),
            fuzzy_inputs=getattr(recommendation, "fuzzy_inputs", {}),
        )

    def render_text(self, explanation: RecommendationExplanation) -> str:
        """Rendre une explication sous forme textuelle.

        Le texte reste volontairement compact pour etre exploitable dans la CLI
        et dans la GUI de demonstration.
        """

        score = explanation.score if explanation.score is not None else 0.0
        score_label = self._score_label(score)
        output_term = _format_term(explanation.dominant_output_term) if explanation.dominant_output_term else "aucun"

        lines = [
            f"Film : {explanation.movie.title}",
            f"Score de recommandation : {score:.4f} ({score_label}, sortie dominante: {output_term})",
            "Pourquoi ce film est recommande :",
        ]

        if explanation.criteria:
            for criterion in explanation.criteria:
                raw_value = "" if criterion.raw_value is None else f", valeur={criterion.raw_value}"
                lines.append(
                    "- "
                    f"{_format_variable(criterion.name)} = {_format_term(criterion.dominant_term)} "
                    f"(mu={criterion.degree:.4f}{raw_value})"
                )
        else:
            lines.append("- Aucun critere dominant n'a ete identifie.")

        lines.append("Regles floues activees :")
        if explanation.activated_rules:
            for activation in explanation.activated_rules:
                antecedents = " ET ".join(
                    f"{_format_variable(antecedent.variable)}={_format_term(antecedent.term)}"
                    f" (mu={activation.antecedent_degrees.get(antecedent.variable, 0.0):.4f})"
                    for antecedent in activation.rule.antecedents
                )
                lines.append(
                    "- "
                    f"{activation.rule.identifier} [mu={activation.degree:.4f}] : "
                    f"{antecedents} -> {_format_term(activation.consequent_term)}"
                )
        else:
            lines.append("- Aucune regle ne depasse le seuil d'affichage.")

        lines.append(f"Defuzzification centroide : {score:.4f}")
        return "\n".join(lines)

    def _build_criteria(
        self,
        *,
        inference: InferenceResult,
        crisp_inputs: Mapping[str, float],
        fuzzy_inputs: Mapping[str, Mapping[str, float]],
    ) -> list[ExplanationCriterion]:
        criteria_by_variable: dict[str, ExplanationCriterion] = {}

        for variable, term_degrees in fuzzy_inputs.items():
            dominant_term = self._dominant_term(term_degrees)
            if dominant_term is None:
                continue
            degree = float(term_degrees[dominant_term])
            criteria_by_variable[variable] = ExplanationCriterion(
                name=variable,
                dominant_term=dominant_term,
                degree=degree,
                raw_value=crisp_inputs.get(variable),
            )

        if not criteria_by_variable:
            activations = inference.activated_rules or inference.evaluated_rules
            for activation in activations:
                for antecedent in activation.rule.antecedents:
                    degree = float(activation.antecedent_degrees.get(antecedent.variable, 0.0))
                    existing = criteria_by_variable.get(antecedent.variable)
                    if existing is None or degree > existing.degree:
                        criteria_by_variable[antecedent.variable] = ExplanationCriterion(
                            name=antecedent.variable,
                            dominant_term=antecedent.term,
                            degree=degree,
                            raw_value=crisp_inputs.get(antecedent.variable),
                        )

        ordered = [
            criteria_by_variable[variable]
            for variable in VARIABLE_ORDER
            if variable in criteria_by_variable
        ]
        ordered.extend(
            criterion
            for variable, criterion in sorted(criteria_by_variable.items())
            if variable not in VARIABLE_ORDER
        )
        return ordered

    @staticmethod
    def _dominant_term(term_degrees: Mapping[str, float]) -> str | None:
        if not term_degrees:
            return None
        return max(term_degrees, key=lambda term: (float(term_degrees[term]), term))

    @staticmethod
    def _score_label(score: float) -> str:
        if score >= 0.75:
            return "fortement recommande"
        if score >= 0.5:
            return "recommandation moderee"
        if score > 0.0:
            return "recommandation faible"
        return "non recommande par les regles V1"


def _format_variable(name: str) -> str:
    return VARIABLE_LABELS.get(name, name.replace("_", " "))


def _format_term(name: str) -> str:
    return TERM_LABELS.get(name, name.replace("_", " "))
