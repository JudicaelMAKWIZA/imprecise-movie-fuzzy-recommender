# Audit architecture V1

Date : 2026-06-05

## Sources officielles lues

- `docs/Plan_v1___traycer.md` : fichier reel correspondant au plan V1 cite dans
  la demande sous le nom `docs/Plan_v1_Traycer.md`.
- `docs/ARCHITECTURAL_DECISIONS.md`
- `README.md`
- `docs/rapport/README.md`

## Synthese des specifications

Le projet doit rester un systeme de recommandation flou interpretable, fonde
sur une architecture de type :

```text
Pre-filtrage -> FIS Mamdani -> Top-N -> Explications
```

Les decisions V1 imposent :

- dataset MovieLens Latest Small ;
- donnees brutes immuables dans `data/movie/` ;
- donnees derivees calculees en memoire par `MovieLensPreprocessor` ;
- moteur flou developpe from scratch ;
- aucune bibliotheque floue externe dans le coeur du systeme ;
- variables linguistiques V1 : preference de genre, note moyenne, popularite ;
- anciennete reportee ;
- base initiale de 8 regles interpretables ;
- CLI avant GUI ;
- explicabilite obligatoire.

## Etat d'avancement avant implementation de la base de regles

Les fondations etaient coherentes et operationnelles :

- `src/data_manager/loader.py` charge et valide les quatre fichiers MovieLens ;
- `src/data_manager/preprocessor.py` derive `avg_rating`, `num_ratings`,
  `genre_list`, `genre_vector` et `release_year` ;
- `src/fuzzy/fuzzy_set.py` implemente `FuzzySet` ;
- `src/fuzzy/membership_functions.py` implemente les fonctions triangulaire et
  trapezoidale from scratch ;
- `src/fuzzy/linguistic_variables.py` definit les variables d'entree V1 ;
- `src/fuzzy/fuzzifier.py` transforme les valeurs numeriques en degres
  d'appartenance ;
- `src/visualization/membership_plots.py` produit des figures matplotlib ;
- `src/data_manager` est la couche officielle de chargement, schemas et acces
  repository.

Les modules encore volontairement incomplets etaient :

- base de regles ;
- moteur d'inference Mamdani ;
- aggregation ;
- defuzzification ;
- recommandation ;
- explications ;
- CLI metier ;
- GUI.

## Verifications avant modification

Commandes executees avant intervention :

```bash
python -m pytest -q -p no:cacheprovider
python -m compileall -q src tests main.py
```

Resultats :

- tests de reference actuels : 77 passed ;
- compilation : OK ;
- imports centraux : OK ;
- dataset reel : 9 742 films, 100 836 notes, 3 683 tags, 9 742 liens ;
- pretraitement en memoire : 9 742 lignes de caracteristiques ;
- recherche `scikit-fuzzy/skfuzzy` dans `requirements.txt`, `pyproject.toml`,
  `src` et `tests` : aucune occurrence.

## Decision d'audit

Le projet est coherent avec les specifications officielles. La prochaine etape
prioritaire est donc l'implementation de la base de regles V1.

## Intervention realisee

La base de regles V1 a ete implementee dans `src/fuzzy/rule_base.py` avec :

- exactement 8 regles ;
- antecedents sur `genre_preference`, `average_rating` et `popularity` ;
- consequent sur `recommendation_score` ;
- connecteur `AND`, compatible avec l'activation Mamdani par t-norme min ;
- descriptions textuelles pour l'explicabilite ;
- validation structurelle des identifiants, variables, termes, sortie,
  doublons et descriptions.

La variable linguistique de sortie `recommendation_score` a ete ajoutee dans
`src/fuzzy/linguistic_variables.py` pour preparer les etapes d'inference et de
defuzzification.

## Verifications apres implementation

Commandes executees :

```bash
python -m compileall -q src tests main.py
python -m pytest -q -p no:cacheprovider
```

Resultats :

- compilation : OK ;
- tests de reference actuels : 77 passed ;
- imports de `RuleBase`, `RuleValidationError` et des variables systeme : OK ;
- `RuleBase.load_minimal_v1()` retourne exactement 8 regles ;
- `build_default_v1_system_variables()` expose les entrees V1 et
  `recommendation_score`.

## Risques residuels

- Les 8 regles V1 ne couvrent pas tout l'espace combinatoire ; c'est normal pour
  une base minimale pedagogique.
- Le moteur Mamdani n'est pas encore implemente ; les regles ne sont donc pas
  encore activees numeriquement.
- La defuzzification et l'explication finale restent a brancher.

## Mise a jour 2026-06-05

Les commentaires de revue ont ete integres :

- preferences linguistiques et intervalles conserves jusqu'a la fuzzification ;
- chargeur YAML effectif pour `config/fuzzy_config.yaml` ;
- evaluation CLI avec `--user-id` et decoupage temporel train/test ;
- namespace `src/data` supprime au profit de `src/data_manager` ;
- defuzzification vectorisee avec surfaces pre-calculees ;
- pre-filtrage sans retour automatique au catalogue complet ;
- valeur neutre `3.5` pour `average_rating` manquant.

Verification finale :

```bash
./.venv/bin/pytest -q
```

Resultat : `77 passed in 2.51s`.

## Conclusion

L'architecture est maintenant alignee avec l'Architecture B et avec le sujet :
les preferences imprecises sont representees comme objets flous ou intervalles,
pas uniquement comme valeurs crisp.
