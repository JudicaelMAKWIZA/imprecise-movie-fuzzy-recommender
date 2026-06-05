# Metriques de demonstration

Date : 2026-06-05

## Protocole CLI

La commande `evaluate` accepte maintenant `--user-id`. Pour l'utilisateur
demande, les notes sont triees par `timestamp` puis separees temporellement :
80 % construisent le profil avec `build_profile`, 20 % forment la
verite-terrain. Les films pertinents sont ceux du test dont la note est au
moins `4.0`.

Ce protocole evite deux fuites de donnees :

- une note ne peut pas servir a la fois a construire le profil et a evaluer la
  pertinence ;
- les caracteristiques films (`avg_rating`, `num_ratings`) sont reconstruites
  pour chaque utilisateur a partir du train temporel avec
  `MovieLensPreprocessor().build_movie_features(train_raw_data)`, puis un
  recommender ephemere est assemble avec `build_recommender_from_features`.

Ainsi, une note tenue dans le test de l'utilisateur cible ne peut pas augmenter
la moyenne ou la popularite du film pendant le calcul du Top-N. Cette
reconstruction par utilisateur est plus couteuse que la reutilisation du
repository pre-calcule, mais elle est retenue pour les mesures afin que les
scores reportes correspondent au protocole train/test.

Exemple :

```bash
python main.py evaluate --user-id 1 --top-n 10
```

## Scenario unitaire

Liste recommandee : `[1, 2]`

Films pertinents attendus : `[1]`

Catalogue total : `[1, 2, 3]`

## Resultats

| Metrique | Valeur |
|---|---:|
| Precision@2 | 0.5000 |
| Recall@2 | 1.0000 |
| Coverage | 0.6667 |
| Diversity | 0.0000 |

## Notes

La diversite vaut `0.0` dans ce mini-scenario parce que les deux films retenus
partagent le meme genre `Sci-Fi`. Ce comportement est attendu et rend la
metrique utile pour discuter la diversite future du Top-N.
