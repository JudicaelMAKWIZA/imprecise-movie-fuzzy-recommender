"""Vue graphique des explications de recommandation."""


class ExplanationView:
    """Composant prevu pour afficher les regles activees et criteres dominants.

    TODO:
        - Afficher les degres d'appartenance.
        - Afficher les regles activees au-dessus du seuil.
        - Ajouter la visualisation de defuzzification si disponible.
    """

    def render(self) -> None:
        """Afficher l'explication detaillee."""

        raise NotImplementedError("TODO: implementer la vue d'explication.")
