# Vérification des chiffres publiables

**Conclusion : 1,53 point et 93,15 % sont confirmés**, exclusivement pour la moyenne des écarts absolus de cinq plis externes, en comparant notre modèle du comité top 40 % à notre politique neutralisée top 40 %. Ce n'est ni le résultat du post-traitement Pareto à ε = 0,005, ni l'écart du CSV final, ni une mesure de mérite.

## Population et définition

Les 10 000 demandes historiques sont réparties en cinq validations externes disjointes de 2 000 personnes. Chaque modèle est ajusté sur les 8 000 autres après sélection interne. Les groupes sont les centres (Capitale-Nationale et Montréal) et les régions éloignées (Bas-Saint-Laurent, Côte-Nord, Gaspésie–Îles-de-la-Madeleine). Chaque politique comparée attribue **800 bourses par pli**, soit 40 %. Les labels utilisés pour F1 et accuracy sont les décisions historiques du comité.

Dans chaque pli k, l'écart est `abs(octrois_centres/effectif_centres - octrois_éloignés/effectif_éloignés)`. Le résultat CV est la moyenne arithmétique des **cinq valeurs absolues**, multipliée par 100 pour l'exprimer en points de pourcentage. F1 et accuracy sont également moyennés sur les mêmes cinq plis, pour les mêmes décisions.

« Avant » : top 800 des probabilités du modèle compact reproduisant le comité. « Après » : top 800 du score cote R + poids des heures, propre au modèle du pli, après retrait des termes directs du contexte. Il ne s'agit pas de la baseline Random Forest officielle sur son holdout 70/30.

## Comparaison principale : moyenne des cinq plis

| Objet | Taux centres (%) | Taux éloignés (%) | Écart absolu (points) | F1 macro comité (%) | Accuracy comité (%) |
|---|---:|---:|---:|---:|---:|
| Comité, top 40 % | 48,9499 | 26,5749 | 22,3751 | 88,2886 | 88,7600 |
| Politique neutralisée, top 40 % | 40,3003 | 39,5506 | 1,5333 | 84,3084 | 84,9400 |
| Comité contraint, ε = 0,005 | 40,1667 | 39,7500 | 0,4167 | 84,7670 | 85,3800 |

Le diagnostic Pareto utilise une autre règle : il maximise la somme des probabilités du comité sous quota de 800 et contrainte d'écart ≤ 0,005 (soit 0,5 point). Il utilise directement les groupes régionaux. Cette règle n'est pas celle du CSV recommandé.

## Réductions calculées sans arrondir les valeurs d'entrée

- Vers **Politique neutralisée, top 40 %** : `100 × (1 − 0.015332822524879801 / 0.2237508360116294)` = **93,1473674923 %**.
- Vers **Comité contraint, ε = 0,005** : `100 × (1 − 0.0041665298029299998 / 0.2237508360116294)` = **98,1378707328 %**.

Le chiffre 93,15 % est le pourcentage de réduction de l'écart moyen, pas une hausse de F1, d'accuracy, d'utilité ou d'égalité des chances. Il s'agit du ratio des deux moyennes, pas de la moyenne des cinq réductions relatives.

## Vérification distincte : prédictions hors pli concaténées

| Objet | Taux centres (%) | Taux éloignés (%) | Écart absolu (points) | F1 macro comité (%) | Accuracy comité (%) |
|---|---:|---:|---:|---:|---:|
| Comité, top 40 % | 48,9500 | 26,5750 | 22,3750 | 88,2887 | 88,7600 |
| Politique neutralisée, top 40 % | 40,3000 | 39,5500 | 0,7500 | 84,3086 | 84,9400 |
| Comité contraint, ε = 0,005 | 40,1667 | 39,7500 | 0,4167 | 84,7670 | 85,3800 |

Le comité sélectionne 2 937/6 000 centres et 1 063/4 000 éloignés. La politique sélectionne 2 418/6 000 centres et 1 582/4 000 éloignés. Son écart concaténé est donc **0,75 point**, alors que sa moyenne d'écarts absolus est **1,5333 point**. Les plis 2 et 3 favorisent légèrement les éloignés en taux : leurs signes se compensent lors de la concaténation. La réduction concaténée serait 96,6480 %, mais elle correspond à une autre agrégation et ne doit pas remplacer 93,15 % dans la comparaison principale. Le F1 concaténé diffère aussi légèrement du F1 moyen.

Les taux moyens des groupes ne suffisent donc pas à retrouver l'écart absolu moyen par simple soustraction. Cette non-commutativité explique le chiffre 1,53 et ne constitue pas une incohérence.

## CSV final : autre cohorte, sans cible de mérite

| Objet | Taux centres (%) | Taux éloignés (%) | Écart absolu (points) | F1 macro comité (%) | Accuracy comité (%) |
|---|---:|---:|---:|---:|---:|
| CSV final, 1 600/4 000 | 40,0084 | 39,9877 | 0,0207 | Non mesurable | Non mesurable |

La cohorte finale comprend 2 372 centres et 1 628 éloignés, dont respectivement 949 et 651 sélectionnés. Le modèle final est ajusté sur les 10 000 historiques. **Aucune réduction entre la CV et ce CSV n'est calculée**, car les modèles et populations diffèrent. Son F1, son accuracy contre mérite et l'égalité des chances officielle restent inconnus.

## Comptes permettant de refaire le calcul

| Pli | Effectifs centres / éloignés | Comité : octrois centres / éloignés | Neutralisée : octrois centres / éloignés | Pareto : octrois centres / éloignés |
|---|---:|---:|---:|---:|
| 0 | 1199 / 801 | 583 / 217 | 491 / 309 | 482 / 318 |
| 1 | 1200 / 800 | 597 / 203 | 484 / 316 | 482 / 318 |
| 2 | 1201 / 799 | 588 / 212 | 472 / 328 | 482 / 318 |
| 3 | 1200 / 800 | 585 / 215 | 479 / 321 | 482 / 318 |
| 4 | 1200 / 800 | 584 / 216 | 492 / 308 | 482 / 318 |

## Intégrité et limites

Le recalcul reconstruit les cinq partitions externes avec leur graine, rejoint les labels et régions aux données originales, puis réajuste indépendamment cinq régressions et leurs standardisations sur les seuls entraînements. Il reproduit les probabilités hors pli et toutes les décisions des trois variantes. Les métriques proviennent des comptes de confusion, avec contrôle par scikit-learn ; les sorties affichées du notebook ne servent pas d'entrée. La contrainte Pareto est réénumérée avec fractions exactes. Un second audit en lecture seule confirme les comptes et résultats.

Aucune fuite directe n'a été détectée dans cette voie de calcul. La sélection interne originale a été lue et auditée ; elle n'a pas été intégralement recalculée lors de ce contrôle complémentaire. Les données avaient déjà été explorées et les anciens retours HxBuddy étaient connus. C'est une validation de développement. Les demandes sont supposées échangeables ; liens familiaux et transport temporel restent non testés. L'allocation utilise la cohorte entière pour son quota, ce qui correspond à une décision par lot, sans utiliser les labels externes pour choisir le seuil.

La parité démographique ne démontre ni une correction causale ni l'égalité des chances conditionnée au mérite. Aucun score du test caché n'a été inféré. Le CSV, le code du modèle et ses paramètres sont restés inchangés. Aucune modification de Devpost n'a été effectuée.

## Preuves et reproduction

- [Script de recalcul indépendant](../../artifacts/equialgo/verification_comparaisons_20261003/recalculer.py).
- [Tableau complet, agrégations séparées](../../artifacts/equialgo/verification_comparaisons_20261003/tableau_comparaisons.csv).
- [Comptes et mesures par pli](../../artifacts/equialgo/verification_comparaisons_20261003/mesures_par_pli.csv).
- [Réductions non arrondies](../../artifacts/equialgo/verification_comparaisons_20261003/reductions.csv).
- [Décisions recalculées](../../artifacts/equialgo/verification_comparaisons_20261003/decisions_recalculees.csv).
- [Vérification, hashes et différences de probabilités](../../artifacts/equialgo/verification_comparaisons_20261003/verification.json).
- [Source hors pli originale](../../artifacts/equialgo/methode_finale_20261003/resultats/hors_pli.csv).

Depuis la racine : `.\.venv\Scripts\python.exe artifacts/equialgo/verification_comparaisons_20261003/recalculer.py`. Cette commande recalcule les preuves dans son dossier, sans modifier la soumission.
