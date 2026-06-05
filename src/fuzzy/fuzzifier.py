"""Fuzzification des valeurs numeriques.

Le fuzzifier orchestre les variables linguistiques V1 et produit les degres
d'appartenance consommes plus tard par le moteur Mamdani.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Mapping

import numpy as np

from .linguistic_variables import LinguisticVariable, build_default_v1_variables

logger = logging.getLogger(__name__)

_ALIASES_BY_VARIABLE: dict[str, dict[str, str]] = {
    "genre_preference": {
        "fort": "forte",
        "moyen": "moyenne",
        "beaucoup": "forte",
        "un_peu": "faible",
        "pas_du_tout": "faible",
    }
}


@dataclass
class Fuzzifier:
    """Convert numeric inputs into linguistic membership degrees.

    Attributes:
        variables: Registry of linguistic variables indexed by technical name.
    """

    variables: Mapping[str, LinguisticVariable] = field(default_factory=build_default_v1_variables)

    @classmethod
    def default_v1(cls) -> "Fuzzifier":
        """Create a fuzzifier configured with the official V1 variables."""

        return cls(variables=build_default_v1_variables())

    def fuzzify_value(self, variable_name: str, value: float) -> dict[str, float]:
        """Fuzzify one crisp value for a named linguistic variable.

        Raises:
            KeyError: If `variable_name` is unknown.
            ValueError: If `value` lies outside the variable universe.
        """

        variable = self.get_variable(variable_name)
        degrees = variable.fuzzify(value)
        logger.info("Valeur fuzzifiee: variable=%s value=%s", variable_name, value)
        return degrees

    def fuzzify_imprecise_value(
        self,
        variable_name: str,
        value: float | str | tuple[float, float] | object,
    ) -> dict[str, float]:
        """Fuzzifier une valeur crisp, un terme linguistique ou un intervalle.

        Un terme est transforme en intervalle via son alpha-cut a 0.5, puis
        projete comme les intervalles explicites. Un intervalle est projete en
        prenant, pour chaque terme, le degre maximal atteint dans l'intervalle
        afin de conserver l'imprecision sans choisir un seul point.
        """

        variable = self.get_variable(variable_name)
        if isinstance(value, str) or hasattr(value, "term"):
            raw_term = value if isinstance(value, str) else getattr(value, "term")
            term = _normalise_term(variable_name, str(raw_term))
            if term not in variable.fuzzy_sets:
                valid_terms = ", ".join(variable.fuzzy_sets)
                raise ValueError(
                    f"Terme linguistique inconnu pour {variable_name}: {value}. "
                    f"Termes valides: {valid_terms}."
                )
            universe = np.linspace(variable.universe_min, variable.universe_max, 501)
            alpha_values = variable.fuzzy_sets[term].alpha_cut(universe, alpha=0.5)
            if not alpha_values:
                raise ValueError(f"Le terme linguistique {term} ne produit aucun alpha-cut a 0.5.")
            return _fuzzify_interval(variable, min(alpha_values), max(alpha_values))
        if _is_interval(value):
            lower, upper = _interval_bounds(value)
            return _fuzzify_interval(variable, lower, upper)
        return self.fuzzify_value(variable_name, float(value))

    def fuzzify_inputs(
        self,
        user_inputs: Mapping[str, object],
        movie_inputs: Mapping[str, object],
    ) -> dict[str, dict[str, float]]:
        """Fuzzify user and movie values into one stable dictionary.

        User inputs and movie inputs are merged. If a key appears in both,
        `movie_inputs` wins because movie features are the most specific values
        for a candidate during scoring.
        """

        merged_inputs = {**user_inputs, **movie_inputs}
        fuzzified = {
            variable_name: self.fuzzify_imprecise_value(variable_name, value)
            for variable_name, value in merged_inputs.items()
            if variable_name in self.variables
        }
        unknown = sorted(set(merged_inputs).difference(self.variables))
        if unknown:
            logger.warning("Variables ignorees pendant la fuzzification: %s", unknown)
        return fuzzified

    def get_variable(self, variable_name: str) -> LinguisticVariable:
        """Return a linguistic variable by name."""

        try:
            return self.variables[variable_name]
        except KeyError as exc:
            raise KeyError(f"Variable linguistique inconnue: {variable_name}") from exc


def _normalise_term(variable_name: str, term: str) -> str:
    normalised = term.casefold().strip().replace(" ", "_").replace("-", "_")
    aliases = _ALIASES_BY_VARIABLE.get(variable_name, {})
    return aliases.get(normalised, normalised)


def _is_interval(value: object) -> bool:
    return (
        isinstance(value, tuple)
        and len(value) == 2
        and all(isinstance(bound, int | float) for bound in value)
    ) or all(hasattr(value, attr) for attr in ("lower", "upper"))


def _interval_bounds(value: object) -> tuple[float, float]:
    if isinstance(value, tuple):
        lower, upper = value
    else:
        lower, upper = getattr(value, "lower"), getattr(value, "upper")
    return float(lower), float(upper)


def _fuzzify_interval(variable: LinguisticVariable, lower: float, upper: float) -> dict[str, float]:
    variable.validate_value(lower)
    variable.validate_value(upper)
    if lower > upper:
        raise ValueError(f"L'intervalle [{lower}, {upper}] est invalide pour la variable {variable.name}.")
    points = np.linspace(lower, upper, 101)
    return {
        term: max(fuzzy_set.membership(float(point)) for point in points)
        for term, fuzzy_set in variable.fuzzy_sets.items()
    }
