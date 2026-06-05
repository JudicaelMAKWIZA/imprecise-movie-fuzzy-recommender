"""Variables linguistiques de la Version 1.

Une variable linguistique contient plusieurs ensembles flous et transforme une
valeur numerique en degres d'appartenance par terme. Les variables V1 retenues
par les specifications sont :

- `genre_preference` sur `[0, 1]` ;
- `average_rating` sur `[0.5, 5.0]` ;
- `popularity` sur `[0, 350]`.

La variable de sortie `recommendation_score` est aussi declaree pour que la
base de regles puisse rester coherente avec les futurs modules d'inference et
de defuzzification.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Mapping

from .fuzzy_set import FuzzySet
from .membership_functions import TriangularMembershipFunction, TrapezoidalMembershipFunction

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LinguisticTerm:
    """Compatibilite semantique pour un terme linguistique.

    Attributes:
        name: Technical name of the term.
        fuzzy_set: Fuzzy set carrying the actual membership function.
    """

    name: str
    fuzzy_set: FuzzySet

    def membership(self, value: float) -> float:
        """Return the membership degree of `value` for this term."""

        return self.fuzzy_set.membership(value)


@dataclass
class LinguisticVariable:
    """Variable linguistique definie sur un univers numerique.

    Attributes:
        name: Technical variable name used by the FIS.
        universe_min: Lower bound of the discourse universe.
        universe_max: Upper bound of the discourse universe.
        fuzzy_sets: Fuzzy sets indexed by term name.
        label: Optional display label for documentation and UI.
    """

    name: str
    universe_min: float
    universe_max: float
    fuzzy_sets: dict[str, FuzzySet] = field(default_factory=dict)
    label: str | None = None

    @property
    def terms(self) -> Mapping[str, LinguisticTerm]:
        """Return terms as lightweight wrappers for backwards compatibility."""

        return {name: LinguisticTerm(name=name, fuzzy_set=fuzzy_set) for name, fuzzy_set in self.fuzzy_sets.items()}

    def add_fuzzy_set(self, fuzzy_set: FuzzySet) -> None:
        """Attach a fuzzy set to this linguistic variable."""

        if fuzzy_set.name in self.fuzzy_sets:
            raise ValueError(f"L'ensemble flou existe deja: {fuzzy_set.name}")
        self.fuzzy_sets[fuzzy_set.name] = fuzzy_set
        logger.debug("Ensemble flou ajoute: variable=%s set=%s", self.name, fuzzy_set.name)

    def validate_value(self, value: float) -> None:
        """Raise `ValueError` if `value` lies outside the universe."""

        if not self.universe_min <= float(value) <= self.universe_max:
            raise ValueError(
                f"La valeur {value} est hors de l'univers [{self.universe_min}, {self.universe_max}] "
                f"pour la variable {self.name}."
            )

    def fuzzify(self, value: float) -> dict[str, float]:
        """Transform a crisp value into membership degrees.

        Args:
            value: Numeric value inside the variable universe.

        Returns:
            Mapping `{term_name: membership_degree}`.
        """

        self.validate_value(value)
        degrees = {name: fuzzy_set.membership(value) for name, fuzzy_set in self.fuzzy_sets.items()}
        logger.debug("Fuzzification: variable=%s value=%s degrees=%s", self.name, value, degrees)
        return degrees


def build_genre_preference_variable() -> LinguisticVariable:
    """Build the V1 linguistic variable for user genre preference."""

    variable = LinguisticVariable("genre_preference", 0.0, 1.0, label="Preference Genre")
    variable.add_fuzzy_set(
        FuzzySet("faible", TrapezoidalMembershipFunction(0.0, 0.0, 0.2, 0.45), label="Faible")
    )
    variable.add_fuzzy_set(FuzzySet("moyenne", TriangularMembershipFunction(0.3, 0.5, 0.7), label="Moyenne"))
    variable.add_fuzzy_set(
        FuzzySet("forte", TrapezoidalMembershipFunction(0.55, 0.8, 1.0, 1.0), label="Forte")
    )
    return variable


def build_average_rating_variable() -> LinguisticVariable:
    """Build the V1 linguistic variable for MovieLens average rating."""

    variable = LinguisticVariable("average_rating", 0.5, 5.0, label="Note moyenne")
    variable.add_fuzzy_set(
        FuzzySet("mauvaise", TrapezoidalMembershipFunction(0.5, 0.5, 1.5, 2.5), label="Mauvaise")
    )
    variable.add_fuzzy_set(FuzzySet("correcte", TriangularMembershipFunction(2.0, 3.0, 3.8), label="Correcte"))
    variable.add_fuzzy_set(FuzzySet("bonne", TriangularMembershipFunction(3.2, 3.8, 4.5), label="Bonne"))
    variable.add_fuzzy_set(
        FuzzySet("excellente", TrapezoidalMembershipFunction(4.0, 4.5, 5.0, 5.0), label="Excellente")
    )
    return variable


def build_popularity_variable() -> LinguisticVariable:
    """Build the V1 linguistic variable for movie popularity."""

    variable = LinguisticVariable("popularity", 0.0, 350.0, label="Popularite")
    variable.add_fuzzy_set(
        FuzzySet("confidentiel", TrapezoidalMembershipFunction(0.0, 0.0, 10.0, 30.0), label="Confidentiel")
    )
    variable.add_fuzzy_set(FuzzySet("modere", TriangularMembershipFunction(20.0, 60.0, 120.0), label="Modere"))
    variable.add_fuzzy_set(FuzzySet("populaire", TriangularMembershipFunction(80.0, 150.0, 250.0), label="Populaire"))
    variable.add_fuzzy_set(
        FuzzySet(
            "tres_populaire",
            TrapezoidalMembershipFunction(200.0, 280.0, 350.0, 350.0),
            label="Tres populaire",
        )
    )
    return variable


def build_recommendation_score_variable() -> LinguisticVariable:
    """Build the linguistic output variable for recommendation scores."""

    variable = LinguisticVariable("recommendation_score", 0.0, 1.0, label="Score de recommandation")
    variable.add_fuzzy_set(
        FuzzySet("tres_faible", TrapezoidalMembershipFunction(0.0, 0.0, 0.1, 0.25), label="Tres faible")
    )
    variable.add_fuzzy_set(FuzzySet("faible", TriangularMembershipFunction(0.15, 0.3, 0.45), label="Faible"))
    variable.add_fuzzy_set(FuzzySet("moyen", TriangularMembershipFunction(0.35, 0.5, 0.65), label="Moyen"))
    variable.add_fuzzy_set(FuzzySet("fort", TriangularMembershipFunction(0.55, 0.7, 0.85), label="Fort"))
    variable.add_fuzzy_set(
        FuzzySet("tres_fort", TrapezoidalMembershipFunction(0.75, 0.9, 1.0, 1.0), label="Tres fort")
    )
    return variable


def build_default_v1_variables() -> dict[str, LinguisticVariable]:
    """Build every official V1 input linguistic variable."""

    variables = {
        "genre_preference": build_genre_preference_variable(),
        "average_rating": build_average_rating_variable(),
        "popularity": build_popularity_variable(),
    }
    logger.info("Variables linguistiques V1 construites: %s", list(variables))
    return variables


def build_default_v1_system_variables() -> dict[str, LinguisticVariable]:
    """Build V1 input variables plus the output `recommendation_score`."""

    variables = build_default_v1_variables()
    variables["recommendation_score"] = build_recommendation_score_variable()
    return variables
