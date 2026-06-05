# Système de recommandation flou basé sur Mamdani

Le système implémente un moteur flou de type Mamdani développé principalement from scratch afin de démontrer les différentes étapes d'un système de recommandation de films à partir du jeu de données MovieLens (`ml-latest-small`) fondé sur des préférences imprécises.

---

## Fonctionnalités implémentées

### Gestion des données

* Chargement des données MovieLens
* Validation des fichiers d'entrée
* Prétraitement des métadonnées
* Construction du catalogue de films

### Moteur flou

* Ensembles flous
* Fonctions d'appartenance triangulaires
* Fonctions d'appartenance trapézoïdales
* Variables linguistiques
* Fuzzification
* Base de règles interprétables
* Inférence Mamdani
* Agrégation par maximum
* Défuzzification par centroïde
* Chargement des variables et règles depuis `config/fuzzy_config.yaml`

### Recommandation

* Construction de profils utilisateurs
* Préférences crisp (`Sci-Fi=0.9`) ou linguistiques (`Sci-Fi=forte`)
* Pré-filtrage de candidats
* Évaluation floue des films
* Calcul du score de recommandation
* Classement Top-N

### Explicabilité

Chaque recommandation peut être justifiée par :

* les règles activées ;
* leur degré d'activation ;
* les termes linguistiques impliqués ;
* le score final obtenu.

### Interfaces

#### CLI

Interface complète accessible depuis le terminal.

#### GUI

Interface graphique Tkinter permettant :

* le chargement du catalogue ;
* la sélection d'un utilisateur ;
* la saisie de préférences ;
* la génération de recommandations ;
* la consultation des explications.

### Évaluation

* Métriques de recommandation
* Tests unitaires
* Tests d'intégration
* Validation du pipeline complet

---

## Architecture

```text
Logique_Floue/
├── config/
├── data/
│   └── movie/
├── docs/
│   └── rapport/
├── src/
│   ├── data_manager/
│   ├── evaluation/
│   ├── fuzzy/
│   ├── recommender/
│   ├── ui/
│   │   ├── cli/
│   │   └── gui/
│   └── visualization/
├── tests/
├── main.py
├── pyproject.toml
└── requirements.txt
```

---

## Installation

Créer un environnement virtuel :

```bash
python -m venv .venv
```

Activation Windows :

```bash
.venv\Scripts\activate
```

Installation des dépendances :

```bash
pip install -r requirements.txt
pip install -e .
```

---

## Exécution

### Interface CLI

Afficher l'aide :

```bash
python main.py --help
```

Générer des recommandations :

```bash
python main.py recommend --user-id 1 --top-n 10 --explain
```

Recommandation avec préférences explicites imprécises :

```bash
python main.py recommend --user-id 1 --top-n 10 --set-genre "Sci-Fi=forte,Action=0.8" --explain
```

Évaluer un utilisateur avec découpage temporel train/test :

```bash
python main.py evaluate --user-id 1 --top-n 10
```

### Interface graphique

Lancer la GUI :

```bash
python main.py gui
```

---

## Variables linguistiques Version 1

### Entrées

#### Préférence de genre

Univers :

```text
[0 ; 1]
```

Termes :

* faible
* moyenne
* forte

#### Note moyenne

Univers :

```text
[0.5 ; 5]
```

Termes :

* mauvaise
* correcte
* bonne
* excellente

#### Popularité

Univers :

```text
[0 ; 350]
```

Termes :

* confidentiel
* modéré
* populaire
* très populaire

### Sortie

#### Score de recommandation

Univers :

```text
[0 ; 1]
```

Termes :

* très faible
* faible
* moyen
* fort
* très fort

---

## Pipeline de recommandation

```text
Profil utilisateur
        ↓
Pré-filtrage
        ↓
Fuzzification
        ↓
Inférence Mamdani
        ↓
Agrégation
        ↓
Défuzzification
        ↓
Score final
        ↓
Classement
        ↓
Top-N
        ↓
Explications
```

---

## Tests

Exécuter la suite complète :

```bash
./.venv/bin/pytest -q
```

Résultat actuel :

```text
77 tests réussis le 2026-06-05 avec `./.venv/bin/pytest -q`
0 échec
```

---

## Documentation

La documentation détaillée est disponible dans :

```text
docs/rapport/
```

Elle contient notamment :

* architecture du système ;
* moteur Mamdani ;
* pipeline de recommandation ;
* évaluations ;
* exemples CLI ;
* revue de littérature ;
* journal de développement.

---

## Objectif pédagogique

Ce projet a pour objectif principal de démontrer la conception complète d'un système de recommandation fondé sur la logique floue :

* modélisation des préférences imprécises ;
* interprétabilité des décisions ;
* inférence Mamdani ;
* recommandation de films à partir de données réelles MovieLens.
