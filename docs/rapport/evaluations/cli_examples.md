# Exemples CLI

Date : 2026-06-05

## Inference floue manuelle

La commande suivante execute le pipeline flou V1 sur trois valeurs crisp :

```bash
python main.py infer --genre-pref 0.9 --rating 4.8 --popularity 300 --explain
```

Sortie attendue :

```text
score=0.9074
output_memberships={'tres_fort': 1.0}
R1 degree=1.0000 -> tres_fort
```

## Recommandation Top-N

Le pipeline Top-N complet est expose par l'API Python via
`recommender.fuzzy_recommender.FuzzyRecommender`. Le branchement CLI Top-N avec
chargement de profils utilisateur sera ajoute apres le moteur d'explications.

Exemple d'intention CLI cible :

```bash
python main.py recommend --user-id 42 --top-n 10 --explain
```