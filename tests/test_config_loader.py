"""Tests du chargeur YAML du systeme flou."""

import pytest
from pathlib import Path

from fuzzy.config_loader import load_fuzzy_system_config
from fuzzy.linguistic_variables import build_default_v1_system_variables
from fuzzy.rule_base import RuleBase


def test_yaml_config_matches_minimal_v1_builders() -> None:
    """La configuration YAML est equivalente aux constructeurs V1."""

    config = load_fuzzy_system_config("config/fuzzy_config.yaml")
    yaml_variables = {**config.input_variables, **config.output_variables}
    code_variables = build_default_v1_system_variables()

    assert yaml_variables.keys() == code_variables.keys()
    for variable_name, yaml_variable in yaml_variables.items():
        code_variable = code_variables[variable_name]
        assert (yaml_variable.universe_min, yaml_variable.universe_max) == (
            code_variable.universe_min,
            code_variable.universe_max,
        )
        assert yaml_variable.fuzzy_sets.keys() == code_variable.fuzzy_sets.keys()
        for term, yaml_set in yaml_variable.fuzzy_sets.items():
            assert yaml_set.membership_function.parameters == code_variable.fuzzy_sets[term].membership_function.parameters

    expected_rules = RuleBase.load_minimal_v1().rules
    assert [(rule.identifier, rule.consequent.term) for rule in config.rule_base.rules] == [
        (rule.identifier, rule.consequent.term) for rule in expected_rules
    ]


def test_yaml_config_rejects_declared_empty_ruleset(tmp_path) -> None:
    """Un ruleset declare mais vide doit produire un message exploitable."""

    config_text = Path("config/fuzzy_config.yaml").read_text(encoding="utf-8").replace(
        "ruleset: minimal_v1",
        "ruleset: intermediate",
        1,
    )
    config_path = tmp_path / "fuzzy_config.yaml"
    config_path.write_text(config_text, encoding="utf-8")

    with pytest.raises(ValueError, match="ruleset 'intermediate'.*ne contient aucune regle"):
        load_fuzzy_system_config(config_path)
