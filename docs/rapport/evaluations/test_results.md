# Resultats de tests

Date : 2026-06-05

Commande :

```bash
./.venv/bin/pytest -q
```

Resultat apres integration des preferences imprecises, du chargeur YAML, de
l'evaluation train/test et des corrections d'architecture :

```text
77 passed in 2.51s
```

Commandes de controle complementaires :

```bash
./.venv/bin/python -m compileall -q src tests main.py
rg "scikit-fuzzy|skfuzzy" requirements.txt pyproject.toml src tests
```

Resultats :

- compilation : OK ;
- aucune reference `scikit-fuzzy` ou `skfuzzy` dans les dependances, le code ou
  les tests.
- controle d'integration MovieLens reel : Top-5 genere avec succes sur 9 742
  films.
- benchmark scoring : 9 742 films en `1.1532 s` (`0.1184 ms/film`).
