# Systeme de recommandation flou

Ce depot contient le squelette officiel du projet de logique floue pour un
systeme de recommandation de films base sur MovieLens `ml-latest-small`.

Les specifications de reference sont :

- `docs/Plan_v1___traycer.md`
- `docs/ARCHITECTURAL_DECISIONS.md`

## Etat actuel

Cette version implemente les fondations du projet :

- chargement valide des fichiers MovieLens ;
- pretraitement des caracteristiques de films ;
- ensembles flous ;
- fonctions d'appartenance triangulaire et trapezoidale from scratch ;
- variables linguistiques V1 ;
- fuzzification ;
- visualisation matplotlib des fonctions d'appartenance.

Restent volontairement hors de cette phase :

- moteur d'explications textuelles ;
- GUI fonctionnelle.

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
│   ├── data_manager/
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

## Modules principaux

- `src/data_manager/loader.py` : chargement, validation, erreurs et logging.
- `src/data_manager/preprocessor.py` : derivation `avg_rating`, `num_ratings`,
  `genre_list`, `genre_vector` et `release_year`.
- `src/fuzzy/fuzzy_set.py` : ensemble flou.
- `src/fuzzy/membership_functions.py` : fonctions triangulaire et trapezoidale.
- `src/fuzzy/linguistic_variables.py` : variables V1.
- `src/fuzzy/fuzzifier.py` : transformation crisp vers degres d'appartenance.
- `src/fuzzy/rule_base.py` : base de 8 regles V1 interpretables.
- `src/fuzzy/inference_engine.py` : activation Mamdani, implication, aggregation
  et traces d'inference.
- `src/fuzzy/defuzzification.py` : defuzzification centroide.
- `src/recommender/fuzzy_recommender.py` : pre-filtrage, scoring, classement et
  Top-N.
- `src/visualization/membership_plots.py` : graphiques matplotlib.

## Tests

```bash
python -m pytest -q -p no:cacheprovider
```

## Exemple CLI

```bash
python main.py infer --genre-pref 0.9 --rating 4.8 --popularity 300 --explain
```

## Prochaines etapes

1. Implementer le moteur d'explications textuelles.
2. Brancher la recommandation Top-N complete dans la CLI.
3. Ajouter l'evaluation sur utilisateurs MovieLens train/test.
