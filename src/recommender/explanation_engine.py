"""Generation d'explications de recommandations.

L'explicabilite est obligatoire dans les decisions architecturales. Ce module
transformera les traces d'inference Mamdani en explications structurees et en
texte lisible : degres linguistiques, regles activees, contribution des
criteres et score defuzzifie.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from data.schemas import MovieFeatures
from fuzzy.inference_engine import InferenceResult, RuleActivation
from recommender.user_profile import UserProfile


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
        text: Version textuelle optionnelle pour CLI ou GUI.

    TODO:
        Ajouter une representation JSON pour l'interface CLI.
    """

    movie: MovieFeatures
    score: float | None
    criteria: list[ExplanationCriterion] = field(default_factory=list)
    activated_rules: list[RuleActivation] = field(default_factory=list)
    text: str | None = None


@dataclass
class ExplanationEngine:
    """Service de transformation des traces floues en explications.

    Attributes:
        activation_threshold: Seuil minimal pour afficher une regle activee.

    TODO:
        - Filtrer les regles avec `degree > activation_threshold`.
        - Identifier le terme dominant de chaque variable.
        - Generer une explication textuelle par templates.
        - Calculer les contributions relatives par critere.
    """

    activation_threshold: float = 0.1

    def explain(
        self,
        profile: UserProfile,
        movie: MovieFeatures,
        inference: InferenceResult,
    ) -> RecommendationExplanation:
        """Construire une explication structuree.

        TODO:
            Exploiter les traces du moteur Mamdani et le profil utilisateur.
        """

        raise NotImplementedError("TODO: generer une explication structuree.")

    def render_text(self, explanation: RecommendationExplanation) -> str:
        """Rendre une explication sous forme textuelle.

        TODO:
            Construire un texte adapte a la CLI puis reutilisable par la GUI.
        """

        raise NotImplementedError("TODO: rendre l'explication en texte.")
