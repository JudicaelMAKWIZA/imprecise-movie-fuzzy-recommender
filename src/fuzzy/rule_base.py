"""Base de regles floues du systeme de recommandation.

Les decisions officielles imposent une Version 1 avec 8 regles interpretables,
puis une extension prevue a 20 regles. Ce module definit les structures de
donnees qui accueilleront ces regles sans encore les declarer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence


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


@dataclass(frozen=True)
class FuzzyConsequent:
    """Conclusion linguistique produite par une regle.

    Example:
        `recommendation_score IS tres_fort`.
    """

    variable: str
    term: str


@dataclass(frozen=True)
class FuzzyRule:
    """Representation declarative d'une regle IF-THEN.

    Attributes:
        identifier: Identifiant stable de la regle, par exemple `R1`.
        antecedents: Conditions floues combinees par une t-norme.
        consequent: Terme de sortie active par la regle.
        description: Phrase lisible pour l'explicabilite et le rapport.

    TODO:
        - Ajouter le connecteur logique lorsque les regles OR seront utiles.
        - Ajouter une ponderation optionnelle si la V1 le demande.
    """

    identifier: str
    antecedents: Sequence[FuzzyAntecedent]
    consequent: FuzzyConsequent
    description: str = ""


@dataclass
class RuleBase:
    """Collection de regles floues activees par le moteur Mamdani.

    Attributes:
        name: Nom du jeu de regles, par exemple `minimal_v1`.
        rules: Liste ordonnee des regles.

    TODO:
        - Charger les 8 regles initiales depuis la configuration.
        - Verifier que les regles restent interpretables.
        - Detecter les variables ou termes inconnus.
    """

    name: str
    rules: list[FuzzyRule] = field(default_factory=list)

    @classmethod
    def load_minimal_v1(cls) -> "RuleBase":
        """Creer la base de regles V1 minimale.

        Returns:
            Une instance contenant les 8 regles officielles.

        TODO:
            Ajouter les regles seulement pendant la phase d'implementation de
            la base de regles. Le squelette ne doit pas les coder.
        """

        raise NotImplementedError("TODO: declarer les 8 regles V1.")

    @classmethod
    def load_intermediate(cls) -> "RuleBase":
        """Creer la base de regles etendue a 20 regles.

        TODO:
            Implementer apres validation scientifique de la base minimale.
        """

        raise NotImplementedError("TODO: declarer les 20 regles intermediaires.")

    def validate(self) -> None:
        """Valider la coherence structurelle de la base de regles.

        TODO:
            Controler les identifiants, antecedents, consequents et doublons.
        """

        raise NotImplementedError("TODO: implementer la validation des regles.")

    def __iter__(self) -> Iterable[FuzzyRule]:
        """Iterer sur les regles declarees.

        Cette methode fournit seulement un confort structurel et ne calcule
        aucune activation floue.
        """

        return iter(self.rules)
