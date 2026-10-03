# ÉquiAlgo — dossier méthodologique

Équipe : **The Optimizers**. Challenge synthétique IVADO, CodeML 2026.

Le dossier privilégie une politique explicable et traçable. Les décisions historiques sont biaisées ; les mesures locales de leur reproduction ne sont pas des mesures du mérite indépendant utilisé par le jury.

## Livrables

- `predictions.csv` : 4 000 identifiants, décisions binaires, 1 600 bourses (40 %).
- `audit_rapport.ipynb` : audit exécuté, validation, proxies, équité et gouvernance.
- `model_corrige.py` et `modele_equialgo.json` : code et paramètres figés.
- `presentation.pdf` : support du pitch de cinq minutes.
- `PITCH-EQUIALGO.md` : texte et minutage ; source PPTX éditable sous `artifacts/equialgo/complements_20261003/presentation/output/presentation.pptx`.
- `PLAN-GOUVERNANCE-EQUIALGO.md` : surveillance, responsabilités proposées et recours.
- `RAPPORT-METHODOLOGIQUE-EQUIALGO.md` : décision, preuves et limites.
- `CONFORMITE-EQUIALGO.md` : correspondance entre exigences et preuves.
- `artifacts/equialgo/methode_finale_20261003/` : protocole, entraînement, résultats hors pli et vérificateur.
- `artifacts/equialgo/complements_20261003/` : baseline officielle exécutée, diagnostic des proxies, balayage des contraintes et gouvernance.

Les fichiers `artifacts/` de la méthode et des compléments font partie du dossier reproductible. Ne livrer que les quatre fichiers racine ne suffit pas à réexécuter le notebook, qui charge les résultats enregistrés et les compléments. Exclure les environnements et jonctions `node_modules`, `.venv`, ainsi que les aperçus temporaires `presentation/build/`, d'un partage ; la version éditable finale est dans `presentation/output/`.

## Installation et reproduction

Python 3.11.8 utilisé. Créer un environnement puis installer `requirements-equialgo.txt`. Déposer les données originales du challenge dans `data/equialgo/data/` : `donnees_demandes.csv` et `candidats_evaluation.csv`. Le notebook officiel et les consignes restent dans `HxBuddy-Challenges/03-ivado-equialgo/equialgo-participants/`. Conserver cette arborescence pour les liens documentaires.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-equialgo.txt
.\.venv\Scripts\python.exe model_corrige.py --model modele_equialgo.json --output predictions_reproduites.csv
.\.venv\Scripts\python.exe model_corrige.py --train --output-dir artifacts/equialgo/reproduction_methodologique
```

Les destinations doivent être nouvelles. Le rejeu doit produire le SHA-256 `0120f838852cf652c01bcee39ee0ef453d2591a4b5394d033a506b4d48de18c6`. L'entraînement sauvegarde les résultats dans son nouveau dossier ; le notebook livré affiche les résultats figés de la version soumise.

La règle finale classe `cote_r_equivalent + 0,14342577944475554 × heures_travail_semaine`, puis retient les 40 % premiers. Son poids vient d'un modèle logistique ajusté sur le contexte historique, sélectionné en validation imbriquée. Les contributions directes du revenu et de la région sont retirées lors du classement. Ni cette neutralisation, ni la parité des taux ne démontrent une correction causale ou l'égalité des chances réelle.

Pour recalculer les compléments depuis la racine :

```powershell
.\.venv\Scripts\python.exe artifacts/equialgo/complements_20261003/proxies/diagnostiquer.py
.\.venv\Scripts\python.exe artifacts/equialgo/complements_20261003/pareto/balayage.py
.\.venv\Scripts\python.exe artifacts/equialgo/complements_20261003/verifier_complements.py
```

Ces scripts écrivent leurs résultats dans leur sous-dossier dédié, sans changer `predictions.csv`. Le graphique du balayage est `artifacts/equialgo/complements_20261003/pareto/front_pareto_contrainte.png`, également tracé par le notebook. Les 24 cellules de celui-ci sont sauvegardées avec leurs sorties. Ouvrir `audit_rapport.ipynb` dans Jupyter et relancer toutes les cellules pour vérifier sa lecture et son exécution locales.

## Soumission manuelle

1. Lire le notebook et répéter le pitch avec son script. Vérifier que les choix normatifs sont défendables par l'équipe.
2. Préparer le dépôt du défi, avec les livrables et leurs dépendances. Ne pas publier les autres projets, l'environnement `.venv`, les fichiers temporaires ou des informations d'accès. Vérifier les droits de partage des données avant toute publication ; fournir aux juges les données officielles via leur canal autorisé.
3. Partager le dépôt avec les juges selon le mécanisme officiel et vérifier leur accès. Aucun remote GitHub n'était configuré à la racine lors du contrôle local ; aucune publication ou invitation n'a été effectuée par l'assistant.
4. Téléverser soi-même `predictions.csv` dans le défi ÉquiAlgo sur HxBuddy si demandé. Le F1 HxBuddy n'est pas la note IVADO sur 35 points. Conserver le hash avec le résultat dans `RESULTATS-HXBUDDY-EQUIALGO.md`.
5. Sur Devpost, choisir exactement le prix de ce défi, avec le même nom et les mêmes membres d'équipe que sur HxBuddy.

Le fichier historique à 94,48 % de F1 HxBuddy est archivé ; ce score ne s'applique pas au CSV méthodologique actuel. Aucun score caché ou classement n'est garanti.
