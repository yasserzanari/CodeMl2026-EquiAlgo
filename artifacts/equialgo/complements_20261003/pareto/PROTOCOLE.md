# Balayage explicite de contrainte — protocole avant calcul

La grille est fixée à ε = [0, 0,005, 0,01, 0,02, 0,05, 0,10, 0,15, 0,20, 0,25, sans contrainte]. Le budget est fixé à 40 % dans chaque cohorte. Aucun point de cette expérience ne remplace la politique recommandée.

Contrainte : valeur absolue de la différence de taux de sélection entre régions éloignées et centres, au plus ε. Pour chaque nombre entier admissible de bourses en régions éloignées, sélectionner les plus grands scores dans chacun des deux groupes, puis retenir le nombre maximisant la somme des scores. Énumérer toutes ces valeurs donne l'optimum combinatoire de cette somme sous les deux contraintes. Les comparaisons de faisabilité utilisent des fractions exactes. Les scores sont des flottants numériques ; leur sommation n'est pas une preuve d'arithmétique réelle exacte.

Deux analyses : (1) probabilités de décisions historiques strictement hors pli, séparément dans chacun des cinq plis externes existants ; (2) score final neutralisé sur les 4 000 candidats non étiquetés. Pour (1), les étiquettes servent uniquement à mesurer l'accord après allocation, jamais à choisir les quotas de groupe. Rapport de moyennes des cinq plis uniquement si tous sont faisables. Les erreurs standard décrivent la dispersion entre plis dépendants, pas une incertitude du score caché.

Mesures : taux de sélection et écart, somme du score objectif, accuracy, F1 macro, TPR et FPR contre le comité historique uniquement. Dominance descriptive selon deux axes séparés : minimiser l'écart / maximiser l'accuracy, ou minimiser l'écart / maximiser le F1 macro. Les ex æquo sont conservés. La grille prédéfinie n'est pas une recherche de tous les modèles possibles.

Le comité étant biaisé, ce front observable n'est ni le front d'égalité des chances contre mérite, ni le score officiel du jury. La recommandation, le modèle et le CSV racine restent inchangés. Les valeurs ε relâchées illustrent le prix d'une contrainte de parité pour un score qui reproduit le comité ; elles ne recommandent pas son utilisation.

Vérifications prévues : budget et domaine des décisions, contrainte exacte, objectif non décroissant lorsque ε se relâche, optimum vérifié sur petits exemples par énumération exhaustive des sous-ensembles, invariance à la permutation des lignes, intégrité du CSV racine et concordance de la politique finale non contrainte avec le CSV.
