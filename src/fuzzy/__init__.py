"""Coeur scientifique flou du projet.

Le paquet `fuzzy` regroupe les briques du systeme d'inference Mamdani :
fonctions d'appartenance, variables linguistiques, fuzzification, base de
regles, agregation, defuzzification et moteur d'inference.

Les modules sont volontairement sous forme de squelette. Les fonctions qui
portent de la logique floue doivent rester non implementees jusqu'a la phase de
developpement correspondante.
"""

from .aggregation import ConsequentAggregator
from .defuzzification import Defuzzifier
from .fuzzification import Fuzzifier
from .inference_engine import InferenceResult, MamdaniInferenceEngine
from .linguistic_vars import LinguisticTerm, LinguisticVariable
from .membership import MembershipDefinition
from .rule_base import FuzzyRule, RuleBase

__all__ = [
    "ConsequentAggregator",
    "Defuzzifier",
    "Fuzzifier",
    "FuzzyRule",
    "InferenceResult",
    "LinguisticTerm",
    "LinguisticVariable",
    "MamdaniInferenceEngine",
    "MembershipDefinition",
    "RuleBase",
]
