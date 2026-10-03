# ÉquiAlgo — recommandation méthodologique du 3 octobre 2026

## Décision et fichiers

À la demande de l'utilisateur, la recommandation repose désormais sur une méthode justifiable, sans sélectionner les paramètres d'après HxBuddy. **`predictions.csv` à la racine contient la nouvelle politique : 4 000 décisions, 1 600 bourses (40 %). Son score HxBuddy est inconnu.**

Chemin exact : `predictions.csv à la racine du dépôt`.

SHA-256 : `0120f838852cf652c01bcee39ee0ef453d2591a4b5394d033a506b4d48de18c6`.

Le code est `model_corrige.py`, les paramètres sont `modele_equialgo.json`, et le notebook exécuté est `audit_rapport.ipynb`. Les résultats détaillés sont conservés sous `artifacts/equialgo/methode_finale_20261003/resultats/`. Le protocole a été écrit avant ces calculs. Les travaux précédents étaient déjà connus : cette reprise n'est pas une étude aveugle indépendante.

L'ancien meilleur leaderboard reste intact dans `artifacts/equialgo/archive/predictions_leaderboard_Q1650_bacd6c51.csv` : 1 650 bourses, accuracy rapportée 94,68 %, F1 macro rapporté 94,48 %. **Ces scores ne doivent pas être attribués au nouveau predictions.csv.**

## Modèle retenu et justification

Une régression logistique régularisée explique les décisions historiques par la cote R, les heures travaillées, le logarithme du revenu et le groupe régional. Elle ajuste les coefficients académiques en présence du contexte. Pour attribuer les bourses, on retire les termes directs de revenu et de groupe régional, puis on normalise le score par le coefficient de la cote R :

**Score final = cote R + 0,14342577944475554 × heures travaillées par semaine.**

Les 1 600 scores les plus élevés sont retenus. Les égalités sont départagées par un hash stable de l'identifiant, indépendamment de l'ordre des lignes. Les heures compensent ici la charge de travail : c'est un choix normatif explicite, pas une définition officielle du mérite. Le budget de 40 % est le milieu de la plage autorisée ; rien ne prouve qu'il maximise le score caché.

Cette neutralisation retire des effets directs dans une spécification donnée. **Elle n'identifie pas un effet causal, ne supprime pas tous les biais et ne fournit pas une probabilité de mérite.** La cote R et les heures peuvent porter des inégalités structurelles. La recommandation est défendable parmi les approches étudiées, pas démontrée optimale pour le mérite caché.

## Validation et expériences

Trois familles sont comparées : cote R/heures seules, contexte compact, contexte étendu (revenu, distance, première génération, régions et programmes). Chaque famille utilise trois régularisations, C = 0,1 ; 1 ; 10. Validation imbriquée : cinq plis externes stratifiés par région × décision, trois plis internes. Prétraitements appris exclusivement dans les données d'entraînement de chaque pli. Graines : 20261003 et 20261004.

Le critère auxiliaire est la log-loss historique. La règle d'une erreur standard retient la famille la plus simple et la régularisation la plus forte admissibles. **Les cinq plis externes et l'ajustement final retiennent le modèle compact avec C = 0,1.**

| Quantité mesurée | Résultat | Interprétation |
|---|---:|---|
| Log-loss du modèle du comité, moyenne des cinq plis externes | 0,25980 | Prédiction des décisions historiques |
| F1 macro du modèle du comité, seuil fixe 0,5 | 88,1572 % | Moyenne externe ; cible biaisée |
| Accuracy du modèle du comité | 88,68 % | Même cible historique |
| F1 macro de la politique finale, quota 40 % par pli | 84,3084 % | Accord avec le comité, pas mérite |
| Accuracy de la politique finale | 84,94 % | Accord avec le comité, pas mérite |
| F1 contre mérite réel / score IVADO | Inconnus | Étiquettes indépendantes indisponibles |

Le F1 macro est la moyenne des F1 des classes 0 et 1, chaque F1 étant `2TP/(2TP+FP+FN)` pour sa classe. Les valeurs présentées sont ensuite moyennées sur les cinq plis externes. L'accuracy est la proportion de décisions correctes par rapport à la cible indiquée. Une baisse d'accord avec le comité ne démontre ni une amélioration ni une dégradation du mérite.

Dans la sélection interne finale, la log-loss vaut 0,26005 pour le compact C=0,1, contre 0,25878 pour C=10. Ce dernier minimum n'est pas retenu, car le premier satisfait la règle de simplicité. La famille académique seule reste vers 0,31863 ; la famille étendue n'apporte pas un gain justifiant sa complexité. Ces chiffres internes servent à sélectionner, pas à annoncer une performance indépendante.

Deux cents bootstraps stratifiés, configuration finale fixe, donnent un intervalle percentile descriptif à 95 % de **0,12927 à 0,16084** pour le poids des heures, toujours positif. L'exclusion successive des régions donne des poids de **0,13459 à 0,15274**. Cela documente la stabilité conditionnelle du coefficient, sans couvrir toute l'incertitude de sélection ou du mérite.

Les bonus manuels de distance/première génération, le plafonnement des heures et les poids choisis sur HxBuddy ne sont pas réutilisés. Leurs résultats antérieurs restent dans `RESULTATS-HXBUDDY-EQUIALGO.md`. Les recherches précédentes d'ensembles, interactions et classements n'établissaient pas un gain validé sur le mérite. Aucun résultat caché ni label individuel n'a été inventé.

## Équité et exigences officielles

Sources : [consignes françaises](HxBuddy-Challenges/03-ivado-equialgo/equialgo-participants/consignes-fr.pdf), [README officiel](HxBuddy-Challenges/03-ivado-equialgo/equialgo-participants/README.md), description HxBuddy transmise par l'utilisateur.

| Critère officiel | Exigence vérifiable et état |
|---|---|
| Diagnostic, 25 points | Données historiques, écarts régionaux, proxies et limites documentés dans le notebook ; note qualitative inconnue |
| Équité, 20 points | Réduction de l'écart d'égalité des chances contre référence indépendante ; écart initial annoncé 0,270 ; valeur finale incalculable localement |
| Utilité, 15 points | Accord avec la référence indépendante, normalisé entre allocation aléatoire respectant le budget et allocation parfaite ; score inconnu |
| Budget technique | 36–44 %, donc 1 440–1 760 octrois ; 1 600 conformes ; ce n'est pas une obligation de 1 650 |
| Gouvernance et éthique, 25 points | Hypothèses, limites, suivi et recours documentés ; appréciation du jury inconnue |
| Pitch et code, 15 points | Code reproductible, notebook exécuté et `presentation.pdf` de sept diapositives ; script de cinq minutes fourni, répétition orale à faire |
| Format officiel | Deux colonnes exactes `id_candidat,decision_octroi`, 4 000 lignes, décisions binaires ; vérifié |
| HxBuddy | Accuracy et F1 macro indicatifs contre mérite ; ne reproduisent pas les 35 points IVADO |

La consigne générique HxBuddy mentionne `id` et `label`, tandis que l'exemple officiel du défi utilise `id_candidat` et `decision_octroi`. Le fichier conserve le format spécifique du défi déjà utilisé dans les candidats évalués. L'échec de `comparaison_finale.csv` ne justifie pas d'envoyer une table de comparaison : utiliser uniquement le fichier de prédictions.

Sur les 4 000 demandes, le taux est 949/2 372 = **40,0084 %** dans les centres et 651/1 628 = **39,9877 %** en régions éloignées. Écart de parité démographique : **0,0207 point de pourcentage**, sans quota régional forcé. Les cinq taux régionaux vont néanmoins de **38,2937 % à 41,5482 %**. Ce résultat descriptif n'est pas une preuve d'égalité des chances : celle-ci conditionne sur le mérite réel, absent ici. Voir les [définitions et limites Fairlearn](https://fairlearn.org/main/user_guide/assessment/common_fairness_metrics.html).

La neutralisation est balayée de 0 à 1 pour montrer le compromis avec l'accord historique. La neutralisation complète a été décidée normativement, sans choisir le meilleur point après observation. Les contraintes de parité ε = 0 ; 0,005 ; 0,01 ; 0,02 ; 0,05 et sans contrainte ont aussi été calculées : parité exacte infaisable à ce budget entier, autres contraintes non actives, même allocation. Cette frontière se réduit donc à un point faisable ; elle n'établit pas un optimum sur l'utilité officielle cachée.

## Audit et contrôles

Les 10 000 identifiants historiques et 4 000 identifiants d'évaluation sont uniques et disjoints ; aucun manque détecté. Aucun doublon exact de caractéristiques dans l'historique. Les identifiants servent seulement à l'appariement et au départage. Aucun apprentissage sur les étiquettes d'évaluation, qui ne sont pas disponibles. Sans dates ni identifiant de personne récurrente, la validation suppose des demandes échangeables ; elle ne garantit pas le transport temporel ni l'absence de liens non observés.

Le vérificateur séparé a contrôlé les colonnes, types, identifiants et ordre source, 4 000 lignes, absence de vides et doublons, domaine {0,1}, 1 600 octrois, lecture CSV et empreintes des sources. Il a reproduit le classement en arithmétique décimale indépendante, les décisions après trois permutations, l'invariance aux changements de contexte seuls, la monotonie en cote R/heures, toutes les métriques externes, la sélection interne du premier pli et le réajustement final. Écart maximal de probabilités lors du rejeu : 1,45 × 10⁻¹⁵.

Comparaison par identifiant avec **79 fichiers admissibles antérieurs** : aucun vecteur identique ; le plus proche diffère de quatre décisions. Ce ne sont pas 79 modèles indépendants. Par rapport au meilleur historique Q1650 : **50 sorties, zéro entrée**, principalement liées au budget retenu. Ce changement ne prouve pas une amélioration du score.

Le notebook complété compte 24 cellules, dont 10 cellules de code exécutées intégralement sans erreur. Les figures d'origine et des compléments ont été inspectées visuellement. L'export HTML a été généré, mais sa mise en page globale n'a pas pu être inspectée dans le navigateur : l'accès local a été refusé par la politique du navigateur. La vérification numérique et celle des figures sont terminées. Le PDF de sept pages a été rendu et inspecté.

## Compléments de diagnostic et de livraison

Trois sous-agents ont travaillé en parallèle, puis les résultats ont été intégrés et revus. Le modèle et le CSV recommandé gardent leurs empreintes initiales. Les compléments n'ont servi à choisir ni un nouveau poids ni un nouveau quota.

**Proxies.** Une régression logistique fixée prédit le groupe régional à partir de chaque variable, avec cinq plis et prétraitements appris sur les seuls entraînements. AUC moyennes : postal 1,0000 ; distance 0,9981 ; heures 0,8052 ; log-revenu 0,6925 ; première génération 0,5896 ; cote R 0,5611 ; programme 0,5528. Le contrôle à cible permutée vaut 0,5116. Ce sont des associations au groupe régional, pas des performances de mérite. Les 55 AUC par pli et les 11 AUC agrégées ont été recalculées par rangs dans une vérification indépendante. Les résultats et leurs limites sont dans `artifacts/equialgo/complements_20261003/proxies/` et le notebook.

**Front de Pareto supplémentaire.** Un balayage explicite de dix contraintes de parité a été appliqué aux probabilités historiques hors pli, avec budget de 40 % et allocation optimale pour la somme des probabilités. Pour ε=0,005 (0,5 point autorisé), l'écart moyen vaut 0,4167 point et l'accord avec le comité 85,38 %. Sans contrainte : 22,3751 points et 88,76 %. Les comptes et métriques de 48 allocations faisables ont été recalculés indépendamment. La parité exacte n'étant faisable que dans trois plis, aucune moyenne partielle n'est présentée comme comparable aux cinq plis. Ce front diagnostique est distinct de celui de la politique finale, dont les contraintes testées restent non actives. Le graphique figure dans le notebook et `artifacts/equialgo/complements_20261003/pareto/front_pareto_contrainte.png`. Aucun de ces accords historiques ne mesure l'utilité officielle.

**Baseline officielle.** Les cellules d'origine ont été rejouées sans modification dans un dossier isolé : accuracy historique 88,13 %, écart de sélection 18,76 points ; retirer région et postal laisse 17,31 points. Le découpage officiel est différent de notre validation imbriquée, donc une comparaison de ces nombres ne prouve pas un gain statistique. Ce contrôle postérieur ne démontre pas une exécution avant tous les travaux antérieurs.

**Gouvernance et pitch.** `PLAN-GOUVERNANCE-EQUIALGO.md` précise responsables par rôle, fréquences, seuils proposés, actions, recours et conditions de reprise. Les seuils sont des propositions à approuver, pas des prescriptions des organisateurs. `presentation.pdf` et `PITCH-EQUIALGO.md` couvrent sept diapositives en cinq minutes visées. La source PPTX éditable est dans `artifacts/equialgo/complements_20261003/presentation/output/presentation.pptx`.

**Portabilité et partage.** Le vérificateur historique résout désormais les chemins de provenance relativement au dossier du projet ; il a été exécuté avec succès depuis une copie située ailleurs. `requirements-equialgo.txt` fige l'environnement Python. Les dépendances `artifacts/` doivent accompagner les fichiers racine. `CONFORMITE-EQUIALGO.md` distingue preuves locales et étapes humaines restantes. Aucun remote GitHub n'est configuré à la racine ; aucun accès des juges n'a été confirmé ou créé.

## Reproduire et soumettre manuellement

Depuis la racine du projet, avec l'environnement Python fourni :

```powershell
.\.venv\Scripts\python.exe model_corrige.py --model modele_equialgo.json --output predictions_reproduites.csv
.\.venv\Scripts\python.exe model_corrige.py --train --output-dir artifacts/equialgo/reproduction_methodologique
```

Utiliser des destinations nouvelles : le code refuse d'écraser un export existant. Python 3.11.8, NumPy 2.4.6, pandas 3.0.6, scikit-learn 1.9.1 ; autres détails et graines dans le protocole et les résultats. La [validation imbriquée](https://scikit-learn.org/stable/modules/cross_validation.html) sépare sélection et mesure externe ; elle ne remplace pas une vérité terrain pertinente.

1. Contrôler le notebook dans Jupyter et les choix normatifs, puis répéter le pitch de `presentation.pdf` avec `PITCH-EQUIALGO.md` pour tenir cinq minutes.
2. Dans le défi ÉquiAlgo sur HxBuddy, sélectionner le `predictions.csv` à la racine indiqué plus haut. Effectuer soi-même l'envoi si souhaité ; aucun envoi n'a été fait ici.
3. Conserver le nom et le hash avec le résultat ; l'ajouter au registre sans attribuer ce score à une autre version.
4. Pour le dépôt officiel, joindre les fichiers demandés et partager le dépôt avec le jury selon les consignes. Sur Devpost, choisir exactement le prix correspondant au défi et garder le même nom et les mêmes membres d'équipe. Aucune publication n'a été effectuée ici.

En production réelle, un tel score exigerait une validation de mérite indépendante, un suivi des taux/erreurs régionaux, une surveillance des changements de données, un recours humain et une révision des choix normatifs. Le challenge porte sur des données synthétiques. Aucun score de 99 %, classement futur ou note du jury n'est garanti.
