"""Base de regles floues du systeme de recommandation.

La Version 1 retient exactement huit regles Mamdani interpretables. Chaque
regle combine les trois variables d'entree disponibles dans les fondations du
projet (`genre_preference`, `average_rating`, `popularity`) et active un terme
linguistique de sortie sur `recommendation_score`.

Ce module reste declaratif : il ne calcule pas d'activation de regle et ne fait
pas d'inference. Ces responsabilites appartiendront au moteur Mamdani.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping, Sequence


class RuleValidationError(ValueError):
    """Erreur levee lorsqu'une base de regles viole le contrat V1."""


V1_RULE_COUNT = 8
V1_INPUT_TERMS: Mapping[str, frozenset[str]] = {
    "genre_preference": frozenset({"faible", "moyenne", "forte"}),
    "average_rating": frozenset({"mauvaise", "correcte", "bonne", "excellente"}),
    "popularity": frozenset({"confidentiel", "modere", "populaire", "tres_populaire"}),
}
V1_OUTPUT_TERMS: Mapping[str, frozenset[str]] = {
    "recommendation_score": frozenset({"tres_faible", "faible", "moyen", "fort", "tres_fort"}),
}
V1_REQUIRED_ANTECEDENT_VARIABLES = frozenset(V1_INPUT_TERMS)


@dataclass(frozen=True)
class FuzzyAntecedent:
    """Condition d'entree d'une regle floue.

    Example:
        `genre_preference IS forte`.

    Attributes:
        variable: Nom de la variable linguistique.
        term: Terme attendu pour cette variable.
    """

    variable: str
    term: str

    def __post_init__(self) -> None:
        if not self.variable.strip():
            raise ValueError("Un antecedent doit definir une variable.")
        if not self.term.strip():
            raise ValueError("Un antecedent doit definir un terme linguistique.")


@dataclass(frozen=True)
class FuzzyConsequent:
    """Conclusion linguistique produite par une regle.

    Example:
        `recommendation_score IS tres_fort`.
    """

    variable: str
    term: str

    def __post_init__(self) -> None:
        if not self.variable.strip():
            raise ValueError("Un consequent doit definir une variable.")
        if not self.term.strip():
            raise ValueError("Un consequent doit definir un terme linguistique.")


@dataclass(frozen=True)
class FuzzyRule:
    """Representation declarative d'une regle IF-THEN.

    Attributes:
        identifier: Identifiant stable de la regle, par exemple `R1`.
        antecedents: Conditions floues combinees par une t-norme.
        consequent: Terme de sortie active par la regle.
        description: Phrase lisible pour l'explicabilite et le rapport.

        conjunction: Connecteur logique entre antecedents. La V1 utilise
            exclusivement `AND`, compatible avec la t-norme min du moteur
            Mamdani.
    """

    identifier: str
    antecedents: Sequence[FuzzyAntecedent]
    consequent: FuzzyConsequent
    description: str = ""
    conjunction: str = "AND"

    def __post_init__(self) -> None:
        if not self.identifier.strip():
            raise ValueError("Une regle doit avoir un identifiant stable.")
        if not self.antecedents:
            raise ValueError("Une regle doit avoir au moins un antecedent.")
        if self.conjunction != "AND":
            raise ValueError("La V1 ne supporte que le connecteur AND.")

        variables = [antecedent.variable for antecedent in self.antecedents]
        if len(variables) != len(set(variables)):
            raise ValueError(f"La regle {self.identifier} contient une variable en double.")

    @property
    def antecedent_variables(self) -> frozenset[str]:
        """Variables d'entree utilisees par la regle."""

        return frozenset(antecedent.variable for antecedent in self.antecedents)

    def as_text(self) -> str:
        """Rendre la regle dans une forme proche du langage naturel."""

        antecedents = f" {self.conjunction} ".join(
            f"{antecedent.variable} IS {antecedent.term}" for antecedent in self.antecedents
        )
        return f"{self.identifier}: IF {antecedents} THEN {self.consequent.variable} IS {self.consequent.term}"


@dataclass
class RuleBase:
    """Collection de regles floues activees par le moteur Mamdani.

    Attributes:
        name: Nom du jeu de regles, par exemple `minimal_v1`.
        rules: Liste ordonnee des regles.

    La methode `load_minimal_v1` construit la base officielle de huit regles.
    `validate` peut aussi etre utilisee pour verifier une base construite a la
    main pendant les tests ou les phases futures.
    """

    name: str
    rules: list[FuzzyRule] = field(default_factory=list)

    @classmethod
    def load_minimal_v1(cls) -> "RuleBase":
        """Creer la base de regles V1 minimale.

        Les huit regles sont volontairement compactes et interpretables. Elles
        couvrent les situations pedagogiques principales : compatibilite forte,
        compromis de popularite, compensation par note excellente, et penalite
        lorsque preference et qualite sont faibles.
        """

        rule_base = cls(
            name="minimal_v1",
            rules=[
                _rule(
                    "R1",
                    genre="forte",
                    rating="excellente",
                    popularity="tres_populaire",
                    score="tres_fort",
                    description=(
                        "Preference de genre forte, note excellente et popularite tres elevee : "
                        "recommandation maximale."
                    ),
                ),
                _rule(
                    "R2",
                    genre="forte",
                    rating="excellente",
                    popularity="confidentiel",
                    score="fort",
                    description=(
                        "Un film excellent dans un genre tres apprecie reste fortement recommande "
                        "meme s'il est confidentiel."
                    ),
                ),
                _rule(
                    "R3",
                    genre="forte",
                    rating="bonne",
                    popularity="populaire",
                    score="fort",
                    description="Genre tres apprecie, bonne note et popularite solide : recommandation forte.",
                ),
                _rule(
                    "R4",
                    genre="moyenne",
                    rating="excellente",
                    popularity="tres_populaire",
                    score="fort",
                    description=(
                        "Interet de genre moyen compense par une excellente note et une tres forte popularite."
                    ),
                ),
                _rule(
                    "R5",
                    genre="moyenne",
                    rating="bonne",
                    popularity="modere",
                    score="moyen",
                    description="Situation equilibree : preference, note et popularite restent intermediaires.",
                ),
                _rule(
                    "R6",
                    genre="faible",
                    rating="excellente",
                    popularity="tres_populaire",
                    score="moyen",
                    description=(
                        "Genre peu apprecie mais film excellent et tres populaire : recommandation prudente."
                    ),
                ),
                _rule(
                    "R7",
                    genre="forte",
                    rating="mauvaise",
                    popularity="populaire",
                    score="faible",
                    description=(
                        "La preference de genre ne suffit pas a compenser une mauvaise note, meme avec popularite."
                    ),
                ),
                _rule(
                    "R8",
                    genre="faible",
                    rating="mauvaise",
                    popularity="confidentiel",
                    score="tres_faible",
                    description=(
                        "Genre peu apprecie, mauvaise note et faible visibilite : recommandation tres faible."
                    ),
                ),
            ],
        )
        rule_base.validate()
        return rule_base

    @classmethod
    def load_intermediate(cls) -> "RuleBase":
        """Creer la base de regles etendue a 20 regles.

        TODO:
            Implementer apres validation scientifique de la base minimale.
        """

        raise NotImplementedError("TODO: declarer les 20 regles intermediaires.")

    def validate(self) -> None:
        """Valider la coherence structurelle de la base de regles.

        Raises:
            RuleValidationError: Si la base viole le contrat V1 : mauvais
                nombre de regles, identifiants dupliques, termes inconnus,
                variable manquante, consequent invalide ou description vide.
        """

        if not self.rules:
            raise RuleValidationError("Une base de regles ne peut pas etre vide.")

        if self.name == "minimal_v1" and len(self.rules) != V1_RULE_COUNT:
            raise RuleValidationError(f"minimal_v1 doit contenir exactement {V1_RULE_COUNT} regles.")

        identifiers = [rule.identifier for rule in self.rules]
        duplicate_identifiers = _duplicates(identifiers)
        if duplicate_identifiers:
            raise RuleValidationError(f"Identifiants de regles dupliques: {duplicate_identifiers}")

        if self.name == "minimal_v1":
            expected_identifiers = [f"R{index}" for index in range(1, V1_RULE_COUNT + 1)]
            if identifiers != expected_identifiers:
                raise RuleValidationError(f"minimal_v1 attend les identifiants ordonnes {expected_identifiers}.")

        signatures: set[tuple[tuple[tuple[str, str], ...], tuple[str, str]]] = set()
        for rule in self.rules:
            self._validate_rule(rule)
            signature = (
                tuple((antecedent.variable, antecedent.term) for antecedent in rule.antecedents),
                (rule.consequent.variable, rule.consequent.term),
            )
            if signature in signatures:
                raise RuleValidationError(f"Regle dupliquee detectee: {rule.identifier}")
            signatures.add(signature)

    def __iter__(self) -> Iterable[FuzzyRule]:
        """Iterer sur les regles declarees.

        Cette methode fournit seulement un confort structurel et ne calcule
        aucune activation floue.
        """

        return iter(self.rules)

    def get_rule(self, identifier: str) -> FuzzyRule:
        """Retourner une regle par identifiant stable."""

        for rule in self.rules:
            if rule.identifier == identifier:
                return rule
        raise KeyError(f"Regle inconnue: {identifier}")

    def _validate_rule(self, rule: FuzzyRule) -> None:
        if not rule.description.strip():
            raise RuleValidationError(f"La regle {rule.identifier} doit avoir une description explicative.")

        if rule.antecedent_variables != V1_REQUIRED_ANTECEDENT_VARIABLES:
            raise RuleValidationError(
                f"La regle {rule.identifier} doit utiliser exactement les variables "
                f"{sorted(V1_REQUIRED_ANTECEDENT_VARIABLES)}."
            )

        for antecedent in rule.antecedents:
            expected_terms = V1_INPUT_TERMS.get(antecedent.variable)
            if expected_terms is None:
                raise RuleValidationError(
                    f"La regle {rule.identifier} utilise une variable inconnue: {antecedent.variable}."
                )
            if antecedent.term not in expected_terms:
                raise RuleValidationError(
                    f"La regle {rule.identifier} utilise le terme inconnu "
                    f"{antecedent.variable}.{antecedent.term}."
                )

        expected_output_terms = V1_OUTPUT_TERMS.get(rule.consequent.variable)
        if expected_output_terms is None:
            raise RuleValidationError(
                f"La regle {rule.identifier} utilise une sortie inconnue: {rule.consequent.variable}."
            )
        if rule.consequent.term not in expected_output_terms:
            raise RuleValidationError(
                f"La regle {rule.identifier} utilise le terme de sortie inconnu "
                f"{rule.consequent.variable}.{rule.consequent.term}."
            )


def _rule(
    identifier: str,
    *,
    genre: str,
    rating: str,
    popularity: str,
    score: str,
    description: str,
) -> FuzzyRule:
    return FuzzyRule(
        identifier=identifier,
        antecedents=(
            FuzzyAntecedent("genre_preference", genre),
            FuzzyAntecedent("average_rating", rating),
            FuzzyAntecedent("popularity", popularity),
        ),
        consequent=FuzzyConsequent("recommendation_score", score),
        description=description,
    )


def _duplicates(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates
