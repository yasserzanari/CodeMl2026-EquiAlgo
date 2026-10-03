# Contrôles réalisés

- `balayage.py` exécuté avec succès ; résultats déterministes reproduits après correction de deux positions d'étiquettes.
- Optimiseur confronté à l'énumération exhaustive des sous-ensembles sur trois petites cohortes et dix contraintes chacune.
- Budget, contrainte rationnelle exacte, monotonie de l'objectif et invariance aux permutations vérifiés.
- CSV racine inchangé ; allocation finale sans contrainte identique à la recommandation.
- `front_pareto_contrainte.png` et `contrainte_et_ecart.png` inspectés visuellement : axes et légendes lisibles, absence de texte tronqué, étiquettes distinctes après correction.
- `cellules_notebook.ipynb` validé par nbformat ; code syntaxiquement compilé. Ce fragment doit être intégré puis exécuté dans le notebook racine, qui définit `ROOT` comme un pathlib.Path vers la racine du dépôt.

Le contrôle combinatoire porte sur l'objectif de somme des scores disponibles ; il ne valide pas leur rapport avec le mérite réel. Les métriques historiques restent auxiliaires. La parité exacte est infaisable dans deux plis externes et dans la cohorte d'évaluation au budget retenu ; les résultats infaisables sont marqués et non remplacés par des approximations silencieuses.
