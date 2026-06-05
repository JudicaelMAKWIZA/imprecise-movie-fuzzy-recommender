"""Coeur scientifique flou du projet."""

from .aggregation import ConsequentAggregator
from .config_loader import FuzzySystemConfig, load_fuzzy_system_config
from .defuzzification import Defuzzifier
from .fuzzifier import Fuzzifier
from .fuzzy_set import FuzzySet
from .inference_engine import InferenceResult, MamdaniInferenceEngine
from .linguistic_variables import (
    LinguisticTerm,
    LinguisticVariable,
    build_average_rating_variable,
    build_default_v1_variables,
    build_default_v1_system_variables,
    build_genre_preference_variable,
    build_popularity_variable,
    build_recommendation_score_variable,
)
from .membership_functions import (
    MembershipDefinition,
    MembershipFunction,
    TrapezoidalMembershipFunction,
    TriangularMembershipFunction,
    trapezoidal,
    triangular,
)
from .rule_base import FuzzyAntecedent, FuzzyConsequent, FuzzyRule, RuleBase, RuleValidationError

__all__ = [
    "ConsequentAggregator",
    "Defuzzifier",
    "Fuzzifier",
    "FuzzySet",
    "FuzzyRule",
    "FuzzySystemConfig",
    "FuzzyAntecedent",
    "FuzzyConsequent",
    "InferenceResult",
    "LinguisticTerm",
    "LinguisticVariable",
    "MamdaniInferenceEngine",
    "MembershipDefinition",
    "MembershipFunction",
    "RuleBase",
    "RuleValidationError",
    "TrapezoidalMembershipFunction",
    "TriangularMembershipFunction",
    "build_average_rating_variable",
    "build_default_v1_variables",
    "build_default_v1_system_variables",
    "build_genre_preference_variable",
    "build_popularity_variable",
    "build_recommendation_score_variable",
    "load_fuzzy_system_config",
    "trapezoidal",
    "triangular",
]
