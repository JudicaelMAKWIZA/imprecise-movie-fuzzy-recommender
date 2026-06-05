# Metriques de demonstration

Date : 2026-06-05

## Scenario

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
