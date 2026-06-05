# Journal de developpement

## 2026-06-05 - Audit et base de regles V1

### Contexte

Reprise du projet apres implementation des fondations : donnees, ensembles
flous, fonctions d'appartenance, variables linguistiques, fuzzification et
visualisation.

### Audit avant modification

- Documentation lue : plan V1, decisions architecturales, README, README du
  rapport.
- Tests de reference actuels : 77 passed avec `./.venv/bin/pytest -q`.
- Compilation Python : OK.
- Imports centraux : OK.
- Dataset MovieLens reel charge avec succes.
- Aucune bibliotheque floue externe detectee dans le coeur du projet.

### Decision

Le projet est coherent. Passage a l'etape prioritaire definie par les
decisions architecturales : base de regles V1.

### Travail realise

- Implementation de `RuleBase.load_minimal_v1`.
- Ajout d'une validation stricte de la base de regles.
- Definition de 8 regles Mamdani interpretables.
- Ajout de la sortie linguistique `recommendation_score`.
- Mise a jour de `config/fuzzy_config.yaml`.
- Ajout de tests unitaires pour la base de regles.
- Ajout d'un rapport d'audit dans `docs/rapport/audit_architecture_v1.md`.

### Verification finale

- Compilation Python : OK.
- Tests de reference actuels : 77 passed avec `./.venv/bin/pytest -q`.
- Base de regles chargee : 8 regles.
- Sortie systeme disponible : `recommendation_score`.

### Prochaine etape

Implementer le moteur d'inference Mamdani : activation des antecedents par
t-norme min, production des traces de regles activees, puis preparation de
l'aggregation des consequents.

## 2026-06-05 - Moteur d'inference Mamdani

### Contexte

La base de regles V1 etait disponible avec exactement 8 regles interpretables.
L'etape suivante definie par les decisions architecturales etait l'inference
Mamdani.

### Travail realise

- Implementation de `MamdaniInferenceEngine.infer`.
- Activation des antecedents depuis les entrees fuzzifiees.
- Operateur `AND` implemente par t-norme minimum.
- Implication Mamdani sous forme de consequent coupe au degre d'activation.
- Aggregation des consequents par maximum.
- Production de `RuleActivation` avec degres par antecedent.
- Production de `InferenceResult` avec `activated_rules` et `evaluated_rules`.
- Implementation de `ConsequentAggregator.aggregate`.
- Ajout de tests unitaires pour activation, implication, aggregation et traces.
- Ajout du schema `docs/rapport/mamdani_inference_engine.md`.

### Verification finale

- Compilation Python : OK.
- Tests de reference actuels : 77 passed avec `./.venv/bin/pytest -q`.
- Aucune bibliotheque floue externe ajoutee.

### Prochaine etape

Implementer la defuzzification centroide pour transformer la sortie floue
`recommendation_score` en score crisp dans `[0, 1]`.

## 2026-06-05 - Pipeline de recommandation V1

### Contexte

Le moteur Mamdani produisait une sortie floue agregee et des traces de regles.
Il manquait la defuzzification, le scoring final, le pre-filtrage et le Top-N.

### Audit avant modification

- Documentation prioritaire relue : plan V1, decisions architecturales, audit,
  journal et schema Mamdani.
- Tests de reference actuels : 77 passed avec `./.venv/bin/pytest -q`.
- Compilation Python : OK.
- Aucune bibliotheque floue externe detectee.
- Dette identifiee : `Defuzzifier`, `MovieRepository`, `UserProfile`,
  `FuzzyRecommender`, metriques et CLI `infer` etaient encore partiellement en
  placeholders.

### Travail realise

- Implementation de la defuzzification centroide.
- Reconstruction de la surface Mamdani de sortie `recommendation_score`.
- Integration complete dans `FuzzyRecommender`.
- Pre-filtrage par genres preferes.
- Scoring individuel des films.
- Classement et Top-N.
- Conservation de `crisp_inputs`, `fuzzy_inputs` et traces d'inference pour le
  futur moteur d'explications.
- Implementation de metriques simples : Precision@N, Recall@N, Coverage,
  Diversity.
- Implementation de la commande CLI `infer`.
- Creation de `docs/rapport/recommendation_pipeline.md`.
- Creation des artefacts dans `docs/rapport/evaluations/`.

### Verification finale

- Compilation Python : OK.
- Tests de reference actuels : 77 passed avec `./.venv/bin/pytest -q`.
- Scenario de demonstration : Top-2 produit `Interstellar (2014)` puis
  `Weak Sci-Fi`.
- Score maximal observe dans le scenario : 0.9074.
- Controle MovieLens reel : Top-5 genere avec succes sur les 9 742 films.

### Limites connues

- La base de regles V1 reste minimale et ne couvre pas toutes les combinaisons.
- Les preferences portent encore seulement sur les genres.

## 2026-06-05 - Corrections apres revue

### Travail realise

- Ajout des preferences linguistiques (`Sci-Fi=forte`) et intervalles
  (`Sci-Fi=0.6..0.9`) sans conversion crisp artificielle.
- Ajout de `src/fuzzy/config_loader.py` pour construire variables et regles
  depuis `config/fuzzy_config.yaml`.
- Refactorisation de `evaluate` avec `--user-id` et decoupage temporel 80/20.
- Deplacement de `MovieRepository` et des schemas vers `data_manager`.
- Suppression des shims `src/data`, `fuzzy/fuzzification.py` et
  `fuzzy/linguistic_vars.py`.
- Defuzzification vectorisee avec surfaces de sortie pre-calculees.
- Pre-filtrage strict : aucun genre au-dessus du seuil donne zero candidat.
- Note moyenne manquante traitee par la valeur neutre `3.5`.
- Profil derive avec ponderation `1 / nombre_de_genres`.

### Verification finale

- Tests : `77 passed in 2.51s` avec `./.venv/bin/pytest -q`.
- Benchmark scoring : 9 742 films en `1.1532 s`.
