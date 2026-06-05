# Revue de litterature

Cette revue suit les references retenues par `docs/Plan_v1___traycer.md`. Elle
sert de socle au rapport scientifique et justifie les choix d'architecture.

## References fondatrices

### Zadeh (1965) - Fuzzy sets

Article fondateur de la theorie des ensembles flous. Il justifie la
representation d'une preference comme un degre d'appartenance dans `[0, 1]`
plutot qu'une categorie binaire.

Utilite pour le projet :

- formaliser les preferences utilisateur imprecises ;
- justifier les ensembles `faible`, `moyenne`, `forte` ;
- expliquer la difference entre filtrage crisp et raisonnement flou.

### Mamdani et Assilian (1975) - Fuzzy logic controller

Reference centrale pour les systemes d'inference linguistiques. Le modele
Mamdani produit des consequents flous interpretables, ce qui correspond a
l'objectif d'explicabilite du projet.

Utilite pour le projet :

- justifier les regles IF-THEN ;
- utiliser des consequents linguistiques comme `fort` ou `tres_fort` ;
- preparer l'activation des regles par t-norme min et l'agregation max.

### Yager et Zadeh (1992) - Applications in intelligent systems

Ouvrage de synthese sur les applications de la logique floue en intelligence
artificielle.

Utilite pour le projet :

- positionner le systeme comme approche interpretable ;
- relier variables linguistiques et decision multicritere ;
- structurer les explications autour des termes linguistiques.

## Systemes de recommandation

### Bobadilla et al. (2013) - Recommender systems survey

Survey general des systemes de recommandation. Il permet de situer le projet
par rapport aux approches classiques : filtrage collaboratif, contenu, hybride
et evaluation.

Utilite pour le projet :

- introduire le domaine des recommandations ;
- justifier les metriques futures ;
- expliquer pourquoi une approche explicable est pertinente.

### Isinkaye et al. (2015) - Principles, methods and evaluation

Article utile pour la methodologie d'evaluation des recommandations.

Utilite pour le projet :

- definir Precision@N et Recall@N ;
- preparer la comparaison avec une baseline ;
- separer evaluation quantitative et qualite explicative.

## Logique floue appliquee aux recommandations

### Yera et Martinez (2017) - Fuzzy tools in recommender systems

Survey specialise sur les outils flous dans les systemes de recommandation. Il
justifie l'usage de la logique floue pour representer des preferences humaines
imprecises et pour produire des recommandations plus interpretable.

Utilite pour le projet :

- positionner la contribution dans les systemes de recommandation flous ;
- justifier une base de regles transparente ;
- soutenir le choix d'un moteur from scratch pour la valeur pedagogique.

## Alternative a comparer

### Takagi et Sugeno (1985) - Fuzzy identification

Modele alternatif avec consequents fonctionnels. Il est plus efficace pour
certaines applications numeriques, mais moins naturel pour generer des
explications linguistiques.

Utilite pour le projet :

- fournir une comparaison critique Mamdani vs Sugeno ;
- justifier le choix de Mamdani dans une application pedagogique et explicable.

## Lien avec l'implementation actuelle

La base de regles V1 suit directement cette revue :

- les ensembles flous viennent de Zadeh ;
- les regles linguistiques viennent de Mamdani ;
- le domaine applicatif vient des surveys de recommandation ;
- l'explicabilite motive le choix de consequents linguistiques ;
- Sugeno reste une reference de comparaison, pas le moteur retenu.

## Justification de la defuzzification centroide

Le choix du centroide est coherent avec Mamdani et Assilian (1975), car les
consequents restent des ensembles flous linguistiques. Le centroide transforme
la surface agregee en score crisp tout en conservant l'information distribuee
sur les termes de sortie.

Dans le projet, cette methode est preferee a une selection du terme dominant,
car elle tient compte simultanement de plusieurs regles activees. Elle est aussi
preferee a Sugeno, car elle conserve la lisibilite linguistique des consequents
jusqu'a l'etape finale.
