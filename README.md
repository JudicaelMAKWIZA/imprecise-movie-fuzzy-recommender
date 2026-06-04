# Systeme de recommandation flou

Ce depot contient le squelette officiel du projet de logique floue pour un
systeme de recommandation de films base sur MovieLens `ml-latest-small`.

Les specifications de reference sont :

- `docs/Plan_v1___traycer.md`
- `docs/ARCHITECTURAL_DECISIONS.md`

## Objectif actuel

Cette version met en place uniquement l'architecture logicielle. Elle ne
contient pas encore la logique metier :

- pas de fonctions d'appartenance implementees ;
- pas de base de regles floues implementees ;
- pas de moteur d'inference Mamdani implemente ;
- pas de logique de recommandation ;
- pas de GUI fonctionnelle.

Chaque module expose des classes, fonctions et docstrings servant de contrat
pour les prochaines phases de developpement.

## Architecture

```text
Logique_Floue/
├── config/
│   └── fuzzy_config.yaml
├── data/
│   ├── movie/
│   └── processed/
├── docs/
│   └── rapport/
├── src/
│   ├── fuzzy/
│   ├── data/
│   ├── recommender/
│   ├── ui/
│   │   ├── cli/
│   │   └── gui/
│   ├── evaluation/
│   └── visualization/
├── tests/
├── main.py
├── pyproject.toml
└── requirements.txt
```

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

## Utilisation prevue

La CLI est le premier point d'entree a rendre fonctionnel. Les commandes sont
deja declarees, mais elles renvoient volontairement une erreur tant que la
logique correspondante n'est pas implementee.

```bash
python main.py --help
python main.py recommend --user-id 42 --top-n 10 --explain
```

## Prochaines etapes

1. Implementer le chargement MovieLens.
2. Implementer le pretraitement dans `src/data/preprocessor.py`.
3. Implementer les fonctions d'appartenance dans `src/fuzzy/membership.py`.
4. Definir les variables linguistiques V1.
5. Ajouter les 8 regles initiales.
6. Implementer le moteur Mamdani et la defuzzification.
7. Brancher la recommandation, les explications, puis la CLI.
