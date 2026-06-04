# Décisions retenues après revue

## Architecture

Architecture B retenue :

Pré-filtrage → FIS Mamdani → Top-N → Explications

## Dataset

MovieLens Latest Small

Fichiers utilisés :

* movies.csv
* ratings.csv
* tags.csv
* links.csv

Les données brutes ne doivent jamais être modifiées.

Les données transformées seront stockées dans :

```text
data/processed/
```

## Version 1

Variables linguistiques :

* Préférence Genre
* Note moyenne
* Popularité

Variables reportées :

* Ancienneté

## Base de règles

Version initiale :

8 règles

Extension prévue :

20 règles

Les règles doivent rester facilement interprétables.

## Moteur d'inférence

Méthode retenue :

Mamdani


## Interface

Ordre de développement :

1. CLI
2. GUI

Le projet doit être entièrement démontrable depuis le terminal avant le développement de l'interface graphique.

## Explicabilité

Obligatoire.

Chaque recommandation doit pouvoir être justifiée à partir des règles floues activées.

## Bibliothèque floue

Le moteur flou principal sera développé par l'équipe (from scratch).

Les bibliothèques externes servent uniquement à :

* Validation
* Comparaison
* Vérification

Elles ne doivent pas constituer le cœur du système.

## Visualisation

Une visualisation graphique des fonctions d'appartenance doit être prévue.

Objectif :

* Vérification du comportement du système
* Support pour la démonstration et la défense

## Priorités de développement

Ordre recommandé :

1. Chargement des données
2. Prétraitement
3. Fonctions d'appartenance
4. Variables linguistiques
5. Fuzzification
6. Base de règles
7. Inférence Mamdani
8. Défuzzification
9. Recommandation
10. Explications
11. CLI
12. GUI

## Hors périmètre de la Version 1

Ne pas développer dans la première version :

* Deep Learning
* Réseaux de neurones
* Filtrage collaboratif avancé
* Systèmes distribués
* Optimisation Big Data
* Sources de données externes (TMDB, IMDb API, etc.)

L'objectif principal reste la démonstration d'un système de recommandation fondé sur la logique floue.
