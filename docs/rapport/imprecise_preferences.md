# Preferences imprecises

Date : 2026-06-05

Le sujet du travail porte sur la recommandation de films avec logique floue et
preferences imprecises. Le modele retenu evite de forcer toute saisie
utilisateur vers une valeur crisp unique.

## Formes acceptees

- `Sci-Fi=0.9` : preference crisp classique dans `[0, 1]`.
- `Sci-Fi=forte` : preference linguistique conservee comme terme flou.
- `Sci-Fi=0.6..0.9` : preference intervalle.

## Passage vers le FIS

`UserProfile.genre_preference_for_movie` retourne l'objet de preference le plus
fort parmi les genres du film. `Fuzzifier.fuzzify_imprecise_value` transforme
ensuite :

- une valeur crisp en degres par fonctions d'appartenance ;
- un terme linguistique en intervalle via l'alpha-cut a `0.5`, puis en degres
  maximaux sur cet intervalle ;
- un intervalle en degres maximaux atteints sur cet intervalle.

Ainsi, `forte` n'est pas remplace par `0.9` et ne devient plus un vecteur
one-hot. Pour `genre_preference=forte`, l'alpha-cut du terme conserve la zone ou
l'appartenance a `forte` est au moins `0.5`; la fuzzification de cet intervalle
peut donc activer partiellement `moyenne` lorsque les ensembles se chevauchent.
L'imprecision reste visible dans les entrees floues consommees par Mamdani.

Ce choix rapproche la V1 des idees discutees dans la litterature sur les
preferences imprecises : les ensembles flous de type 2 et les hesitant fuzzy
sets representent explicitement une incertitude sur l'appartenance ou sur le
terme retenu. La V1 ne les implemente pas formellement, mais l'alpha-cut joue
un role pragmatique de zone d'hesitation autour du terme linguistique saisi.

## Alias linguistiques acceptes

Les alias sont limites par variable afin d'eviter de masquer une faute de
saisie sur une autre entree.

| Variable | Alias | Terme canonique |
|---|---|---|
| `genre_preference` | `fort` | `forte` |
| `genre_preference` | `moyen` | `moyenne` |
| `genre_preference` | `beaucoup` | `forte` |
| `genre_preference` | `un_peu` | `faible` |
| `genre_preference` | `pas_du_tout` | `faible` |

Tout autre terme normalise doit correspondre exactement a un ensemble flou de
la variable cible. Sinon, le fuzzifier leve une erreur listant les termes
valides.
