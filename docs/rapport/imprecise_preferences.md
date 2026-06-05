# Preferences imprecises

Date : 2026-06-05

Le sujet du travail porte sur la recommandation de films avec logique floue et
preferences imprecises. Le modele retenu evite de forcer toute saisie
utilisateur vers une valeur crisp unique.

## Formes acceptees

- `Sci-Fi=0.9` : preference crisp classique dans `[0, 1]`, acceptee
  uniquement en mode opt-in `crisp`.
- `Sci-Fi=forte` : preference linguistique conservee comme terme flou.
- `Sci-Fi=0.6..0.9` : preference intervalle.

Dans la GUI, le mode `intervalle` expose deux curseurs : la valeur principale
sert de borne basse et le second curseur sert de borne haute. Les bornes sont
normalisees dans `[0, 1]` et ordonnees avant d'etre transmises au profil.

## Passage vers le FIS

`UserProfile.genre_preference_for_movie` retourne un objet type qui indique si
au moins un genre du film est connu dans le profil. Lorsque plusieurs genres
du film sont declares par l'utilisateur, la strategie V1 par defaut calcule la
moyenne arithmetique des forces de preference correspondantes. L'ancienne
strategie par maximum reste disponible comme option explicite, mais elle n'est
plus le defaut car elle masque les preferences faibles ou negatives dans un
film multi-genres.

`Fuzzifier.fuzzify_imprecise_value` transforme ensuite :

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
