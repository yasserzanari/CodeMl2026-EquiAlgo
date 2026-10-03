# ÉquiAlgo — The Optimizers

**Une politique d’octroi explicable, reproductible et auditable pour le défi IVADO du CodeML 2026.** Notre travail diagnostique les écarts régionaux, compare une politique neutralisée au classement historique, puis documente les compromis, les limites et la surveillance nécessaire avant tout usage réel.

## Résultat vérifié

Nous avons réentraîné cinq modèles sur des plis externes disjoints et recalculé les décisions et métriques à partir des données autorisées. À quota identique de 40 % (800 bourses sur 2 000 personnes dans chaque pli), la politique neutralisée réduit l’écart absolu moyen de taux d’octroi entre les grands centres et les régions éloignées de **22,38 à 1,53 point**, soit **93,15 %**.

| Mesure — moyenne des cinq plis externes | Classement reproduisant le comité | Politique neutralisée | Évolution |
|---|---:|---:|---:|
| Écart absolu des taux d’octroi régionaux | 22,38 points | 1,53 point | **−93,15 %** |
| F1 macro contre les décisions historiques du comité | 88,29 % | 84,31 % | −3,98 points |
| Exactitude contre les décisions historiques du comité | 88,76 % | 84,94 % | −3,82 points |

Ces résultats décrivent un compromis : la politique distribue les bourses plus également entre les deux groupes observés, tout en reproduisant moins les décisions historiques. **Le F1 et l’exactitude mesurent l’accord avec le comité, pas le mérite réel.** Ces mesures ne démontrent ni une amélioration du mérite, ni l’égalité des chances officielle, ni un meilleur score caché.

Les agrégations ne doivent pas être confondues. La moyenne des cinq écarts absolus par pli vaut **1,53 point**; concaténer d’abord les prédictions donne **0,75 point**, car les directions de certains plis se compensent. Une politique Pareto distincte, avec contrainte régionale explicite ε = 0,005, donne **0,42 point** et n’est pas le CSV recommandé. Enfin, le CSV final montre un écart descriptif de **0,0207 point** sur ses 4 000 candidatures; cette cohorte sans étiquette ne permet pas de calculer son F1 ou son exactitude.

## Fichier de soumission

[`predictions.csv`](predictions.csv) contient 4 000 identifiants et exactement 1 600 décisions positives (40 %, dans la plage autorisée de 36–44 %). Son SHA-256 est `0120f838852cf652c01bcee39ee0ef453d2591a4b5394d033a506b4d48de18c6`. Le fichier respecte l’en-tête `id_candidat,decision_octroi`, les identifiants uniques et les valeurs binaires attendues. **Son score sur l’évaluation cachée est inconnu.**

## Méthode

Une régression logistique régularisée modélise les décisions historiques en tenant compte du contexte. Pour le classement final, nous retirons les contributions directes du revenu familial et de la région, puis utilisons le score explicable :

```text
score = cote_r_equivalent + 0.14342577944475554 × heures_travail_semaine
```

Les 1 600 scores les plus élevés sont retenus; un hash stable de l’identifiant départage les égalités sans dépendre de l’ordre des lignes. Le poids des heures et le quota sont des choix normatifs explicités, et non une définition officielle du mérite ni un optimum démontré sur le test caché.

## Reproduire

Environnement vérifié : Python 3.11.8.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-equialgo.txt
.\.venv\Scripts\python.exe model_corrige.py --model modele_equialgo.json --output predictions_reproduites.csv
```

Pour réentraîner et exécuter le notebook, obtenir les fichiers participant·es depuis le canal officiel et les placer dans `data/equialgo/data/` sous les noms `donnees_demandes.csv` et `candidats_evaluation.csv`, puis ouvrir `audit_rapport.ipynb` depuis la racine. Les données brutes ne sont pas redistribuées.

## Documentation et preuves

- [`docs/equialgo/08-chiffres-publiables.md`](docs/equialgo/08-chiffres-publiables.md) : définitions, calculs non arrondis, comptes par pli et distinction entre CV, Pareto et CSV final.
- [`artifacts/equialgo/verification_comparaisons_20261003/`](artifacts/equialgo/verification_comparaisons_20261003/) : recalcul indépendant, tableau des comparaisons, mesures par pli, réductions et journaux de vérification. Les données brutes et le fichier de décisions individuelles ne sont pas inclus.
- [`RAPPORT-METHODOLOGIQUE-EQUIALGO.md`](RAPPORT-METHODOLOGIQUE-EQUIALGO.md) : choix du modèle, validation imbriquée, résultats et limites.
- [`CONFORMITE-EQUIALGO.md`](CONFORMITE-EQUIALGO.md) : correspondance aux exigences et portée des preuves.
- [`PLAN-GOUVERNANCE-EQUIALGO.md`](PLAN-GOUVERNANCE-EQUIALGO.md) : surveillance proposée, seuils à approuver, recours humains et critères de suspension.
- [`PITCH-EQUIALGO.md`](PITCH-EQUIALGO.md) et [`presentation.pdf`](presentation.pdf) : présentation et script oral.

## Limites et responsabilité

Les données du défi sont synthétiques. Les décisions historiques sont une référence imparfaite et potentiellement biaisée; elles ne constituent pas une vérité terrain sur le mérite. La parité démographique observée n’établit pas l’égalité des chances conditionnée au mérite et ne prouve pas un effet causal. Le score technique caché, les résultats des autres équipes et la note du jury restent inconnus. Avant tout déploiement réel, il faudrait une référence indépendante du mérite, une validation externe et temporelle, l’approbation des choix normatifs, une gouvernance assignée et une supervision humaine effective.
