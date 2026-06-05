"""Point d'entree principal du projet FuzzyRec.

Ce module delegue l'execution a l'interface en ligne de commande declaree dans
`src/ui/cli/commands.py`. La commande `python main.py gui` lance l'interface
Tkinter de demonstration, tandis que les autres commandes restent utilisables
depuis le terminal.
"""

from pathlib import Path
import sys

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ui.cli.commands import main


if __name__ == "__main__":
    main()
