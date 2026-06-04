"""Point d'entree principal du projet FuzzyRec.

Ce module delegue l'execution a l'interface en ligne de commande declaree dans
`src/ui/cli/commands.py`. La GUI n'est pas lancee ici pour la Version 1, car les
decisions architecturales imposent que le projet soit demonstrable depuis le
terminal avant le developpement graphique.

TODO:
    - Ajouter un mode de lancement GUI lorsque l'interface graphique sera
      implementee.
    - Centraliser le chargement de configuration avant l'appel aux commandes.
"""

from ui.cli.commands import main


if __name__ == "__main__":
    main()
