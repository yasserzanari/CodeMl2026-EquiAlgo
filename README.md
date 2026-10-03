# ÉquiAlgo — The Optimizers

Réponse au défi IVADO du CodeML 2026 : diagnostiquer les biais d’octroi régionaux, proposer une règle d’attribution reproductible et définir sa surveillance avant tout usage réel.

## Résultat remis

- `predictions.csv` : format officiel `id_candidat,decision_octroi`, 4 000 personnes et exactement 1 600 bourses (40 %, dans l’enveloppe de 36–44 %).
- SHA-256 : `0120f838852cf652c01bcee39ee0ef453d2591a4b5394d033a506b4d48de18c6`.
- `audit_rapport.ipynb` : diagnostic, validation, proxys, métriques et limites.
- `model_corrige.py` + `modele_equialgo.json` : règle déterministe et paramètres.
- `presentation.pdf` + `PITCH-EQUIALGO.md` : support et script de présentation de cinq minutes.

## Méthode et preuve

Le score final est `cote_r_equivalent + 0.14342577944475554 × heures_travail_semaine`; les 1 600 scores les plus élevés sont retenus. Les contributions directes du revenu familial et de la région sont retirées du classement. Les égalités sont départagées par un hash stable de l’identifiant.

La baseline du comité accorde 48,4 % des bourses dans les grands centres contre 27,3 % dans les régions éloignées. Le rejeu mesure un écart de sélection de 18,76 points; retirer région et code postal laisse 17,31 points. L’audit met en évidence des variables proxies, notamment le code postal et la distance.

Sur le CSV final, l’écart descriptif de taux d’octroi entre grands centres et régions éloignées est de 0,0207 point de pourcentage. Il s’agit de parité démographique, **pas** d’une mesure de l’égalité des chances. Le mérite indépendant utilisé par le barème technique est caché; ni les décisions du comité ni les scores HxBuddy ne le remplacent. Le score IVADO sur 35 points est donc inconnu localement. Les choix de poids et de budget sont normatifs et ne prouvent pas une correction causale.

Le front de Pareto supplémentaire porte sur les probabilités hors pli d’imiter les décisions historiques. Il illustre un compromis de diagnostic, et non le front d’égalité des chances contre le mérite caché.

## Reproduire

Environnement validé : Python 3.11.8. Depuis la racine du dépôt :

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-equialgo.txt
.\.venv\Scripts\python.exe model_corrige.py --model modele_equialgo.json --output predictions_reproduites.csv
```

Pour réentraîner et relancer l’audit, obtenir les deux CSV participant·es depuis le canal officiel du défi et les placer dans `data/equialgo/data/` sous les noms `donnees_demandes.csv` et `candidats_evaluation.csv`. Puis ouvrir `audit_rapport.ipynb` depuis la racine. Les résultats enregistrés et les fichiers de vérification nécessaires aux figures sont inclus; les données brutes du défi ne sont pas redistribuées dans ce dépôt.

## Gouvernance proposée

`PLAN-GOUVERNANCE-EQUIALGO.md` décrit les contrôles par campagne, les responsabilités, les seuils d’alerte proposés, les recours humains, les conditions de suspension et la validation d’une référence indépendante. Ces rôles et seuils doivent être approuvés; aucune mise en production réelle n’a eu lieu. Les données du défi sont synthétiques.

## Arborescence

- `artifacts/equialgo/methode_finale_20261003/` : protocole, résultats hors pli, vérifications et figures.
- `artifacts/equialgo/complements_20261003/proxies/` : audit des proxys et résultats.
- `artifacts/equialgo/complements_20261003/pareto/` : grille de contraintes et front de diagnostic.
- `artifacts/equialgo/complements_20261003/baseline_officielle/` : journal et vérification du rejeu; aucun jeu de données brut ni CSV de sortie de la baseline.
- `RAPPORT-METHODOLOGIQUE-EQUIALGO.md`, `CONFORMITE-EQUIALGO.md` : résultats, correspondance au barème et limites.

Le dépôt n’inclut ni les données brutes du défi, ni identifiants d’accès, ni secrets. Les résultats de l’ancien fichier HxBuddy ne sont pas attribués au `predictions.csv` courant.
