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

Le pipeline Top-N complet est branche a la CLI. Les preferences explicites
peuvent etre crisp ou linguistiques :

```bash
python main.py recommend --user-id 42 --top-n 10 --set-genre "Sci-Fi=forte,Action=0.8" --explain
```

Sans `--set-genre`, le profil est derive de l'historique MovieLens de
l'utilisateur.

## Evaluation

```bash
python main.py evaluate --user-id 42 --top-n 10
```

La commande effectue un decoupage temporel 80/20 des notes de l'utilisateur :
train pour le profil, test pour la pertinence.
