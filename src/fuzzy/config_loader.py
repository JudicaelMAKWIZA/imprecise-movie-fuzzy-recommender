"""Chargement YAML du systeme flou.

Le fichier `config/fuzzy_config.yaml` est la source declarative des variables
linguistiques et de la base de regles V1. Ce module transforme cette
configuration en objets utilises par le moteur.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .fuzzy_set import FuzzySet
from .linguistic_variables import LinguisticVariable
from .membership_functions import TriangularMembershipFunction, TrapezoidalMembershipFunction
from .rule_base import FuzzyAntecedent, FuzzyConsequent, FuzzyRule, RuleBase


@dataclass(frozen=True)
class FuzzySystemConfig:
    """Objets construits depuis la configuration YAML."""

    input_variables: dict[str, LinguisticVariable]
    output_variables: dict[str, LinguisticVariable]
    rule_base: RuleBase
    defuzzification_method: str = "centroid"
    preferred_genre_threshold: float = 0.2
    neutral_average_rating: float = 3.5


def load_fuzzy_system_config(config_path: Path | str = Path("config/fuzzy_config.yaml")) -> FuzzySystemConfig:
    """Charger les variables et regles depuis `config_path`."""

    path = Path(config_path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    variables = _load_variables(data["variables"])
    rule_base = _load_rule_base(data["rule_base"], ruleset=data["fuzzy_system"]["ruleset"])
    output_names = {
        variable_name
        for variable_name, raw_variable in data["variables"].items()
        if raw_variable.get("role") == "output"
    }
    input_variables = {name: variable for name, variable in variables.items() if name not in output_names}
    output_variables = {name: variables[name] for name in output_names}
    return FuzzySystemConfig(
        input_variables=input_variables,
        output_variables=output_variables,
        rule_base=rule_base,
        defuzzification_method=data["fuzzy_system"].get("defuzzification_method", "centroid"),
        preferred_genre_threshold=float(data["fuzzy_system"].get("preferred_genre_threshold", 0.2)),
        neutral_average_rating=float(data["fuzzy_system"].get("neutral_average_rating", 3.5)),
    )


def _load_variables(raw_variables: dict[str, Any]) -> dict[str, LinguisticVariable]:
    variables: dict[str, LinguisticVariable] = {}
    for variable_name, raw_variable in raw_variables.items():
        universe_min, universe_max = raw_variable["universe"]
        variable = LinguisticVariable(
            name=variable_name,
            universe_min=float(universe_min),
            universe_max=float(universe_max),
        )
        for term_name, raw_term in raw_variable["terms"].items():
            variable.add_fuzzy_set(FuzzySet(term_name, _build_membership_function(raw_term)))
        variables[variable_name] = variable
    return variables


def _build_membership_function(raw_term: dict[str, Any]) -> TriangularMembershipFunction | TrapezoidalMembershipFunction:
    parameters = [float(value) for value in raw_term["parameters"]]
    if raw_term["type"] == "triangular":
        return TriangularMembershipFunction(*parameters)
    if raw_term["type"] == "trapezoidal":
        return TrapezoidalMembershipFunction(*parameters)
    raise ValueError(f"Type de fonction d'appartenance non supporte: {raw_term['type']}")


def _load_rule_base(raw_rule_base: dict[str, Any], ruleset: str) -> RuleBase:
    raw_ruleset = raw_rule_base[ruleset]
    if not raw_ruleset.get("rules"):
        raise ValueError(
            f"Le ruleset '{ruleset}' est declare mais ne contient aucune regle ; "
            "utilisez 'minimal_v1' ou completez la definition."
        )
    rules = []
    for raw_rule in raw_ruleset["rules"]:
        antecedents = [
            FuzzyAntecedent(variable=variable_name, term=term_name)
            for variable_name, term_name in raw_rule["if"].items()
        ]
        consequent_variable, consequent_term = next(iter(raw_rule["then"].items()))
        rules.append(
            FuzzyRule(
                identifier=raw_rule["id"],
                antecedents=antecedents,
                consequent=FuzzyConsequent(variable=consequent_variable, term=consequent_term),
                description=raw_rule.get("description", ""),
            )
        )
    rule_base = RuleBase(name=ruleset, rules=rules)
    rule_base.validate()
    return rule_base
