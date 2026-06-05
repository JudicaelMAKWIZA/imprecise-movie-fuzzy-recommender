# Exemple de recommandations

Date : 2026-06-05

## Scenario

Profil utilisateur :

| Genre | Preference |
|---|---:|
| Sci-Fi | 0.9 |
| Comedy | 0.2 |

Catalogue de demonstration :

| movieId | Titre | Genres | Note moyenne | Popularite |
|---:|---|---|---:|---:|
| 1 | Interstellar (2014) | Sci-Fi | 4.8 | 300 |
| 2 | Weak Sci-Fi | Sci-Fi | 1.0 | 160 |
| 3 | Excellent Comedy | Comedy | 4.8 | 300 |

## Resultat Top-2

| Rang | movieId | Titre | Score | Regles activees |
|---:|---:|---|---:|---|
| 1 | 1 | Interstellar (2014) | 0.9074 | R1 |
| 2 | 2 | Weak Sci-Fi | 0.3000 | R7 |

Le film `Excellent Comedy` est exclu par le pre-filtrage, car la preference
Comedy vaut `0.2`, sous le seuil V1 de `0.5`.

## Interpretation

- `Interstellar (2014)` active R1 : genre fortement prefere, note excellente,
  popularite tres populaire.
- `Weak Sci-Fi` active R7 : genre prefere mais mauvaise note ; la sortie reste
  faible malgre la compatibilite de genre.

## Controle sur MovieLens reel

Profil :

| Genre | Preference |
|---|---:|
| Sci-Fi | 0.9 |
| Action | 0.7 |

Top-5 obtenu sur les 9 742 films de `data/movie/` :

| Rang | movieId | Titre | Score | Regles activees |
|---:|---:|---|---:|---|
| 1 | 260 | Star Wars: Episode IV - A New Hope (1977) | 0.8917 | R1 |
| 2 | 2571 | Matrix, The (1999) | 0.8891 | R1 |
| 3 | 2959 | Fight Club (1999) | 0.7689 | R1, R3 |
| 4 | 110 | Braveheart (1995) | 0.7473 | R1, R3 |
| 5 | 1196 | Star Wars: Episode V - The Empire Strikes Back (1980) | 0.7418 | R1, R3 |
