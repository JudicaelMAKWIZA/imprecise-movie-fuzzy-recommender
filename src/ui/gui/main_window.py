"""Fenetre principale prevue pour la GUI.

La specification impose de prioriser la CLI avant la GUI. Cette classe existe
donc uniquement comme contrat d'architecture.
"""


class MainWindow:
    """Conteneur principal de l'application graphique.

    TODO:
        - Choisir definitivement tkinter ou PyQt.
        - Brancher l'editeur de preferences.
        - Brancher la vue des recommandations.
        - Brancher la vue d'explication.
    """

    def show(self) -> None:
        """Afficher la fenetre principale."""

        raise NotImplementedError("TODO: implementer la GUI apres la CLI.")
