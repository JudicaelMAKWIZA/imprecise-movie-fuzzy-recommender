"""Fuzzification des valeurs numeriques.

Le fuzzifier orchestre les variables linguistiques V1 et produit les degres
d'appartenance consommes plus tard par le moteur Mamdani.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Mapping

from .linguistic_variables import LinguisticVariable, build_default_v1_variables

logger = logging.getLogger(__name__)


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

    def fuzzify_inputs(
        self,
        user_inputs: Mapping[str, float],
        movie_inputs: Mapping[str, float],
    ) -> dict[str, dict[str, float]]:
        """Fuzzify user and movie values into one stable dictionary.

        User inputs and movie inputs are merged. If a key appears in both,
        `movie_inputs` wins because movie features are the most specific values
        for a candidate during scoring.
        """

        merged_inputs = {**user_inputs, **movie_inputs}
        fuzzified = {
            variable_name: self.fuzzify_value(variable_name, value)
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
