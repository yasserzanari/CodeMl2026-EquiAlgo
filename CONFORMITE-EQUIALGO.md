# ÉquiAlgo — conformité et portée des preuves

Date : 3 octobre 2026. Objet : dossier local destiné au jury, après compléments parallèles. Les exigences viennent du cahier fourni et de `HxBuddy-Challenges/03-ivado-equialgo/equialgo-participants/consignes-fr.pdf`. Ce document n'attribue pas une note à la place du jury.

## Exigences et preuves

| Exigence | Preuve livrée | Statut et limite |
|---|---|---|
| `predictions.csv` à la racine | 4 000 lignes de données ; en-tête exact `id_candidat,decision_octroi` ; labels entiers 0/1 ; IDs uniques, ordre source, aucun vide | Conforme localement ; SHA-256 `0120f838852cf652c01bcee39ee0ef453d2591a4b5394d033a506b4d48de18c6` |
| Enveloppe 36–44 % | 1 600 bourses / 4 000 = 40 % | Conforme ; budget choisi normativement, pas optimum caché prouvé |
| Diagnostic du biais | Notebook : taux historiques, baseline officielle rejouée, analyses par groupe et région | Livré ; associations observées, pas causalité identifiée |
| Variables proxies trouvées | Sept variables et ensembles : AUC région hors pli, distributions, contrôle par permutation | Livré dans le notebook et `artifacts/equialgo/complements_20261003/proxies/` |
| Métriques d'équité justifiées | Parité démographique observable, distinction avec TPR/FPR historiques et EO réelle | Livré ; EO contre mérite reste non mesurable |
| `model_corrige.py` ou notebook | Script figé, JSON de paramètres, protocole et entraînement reproductible | Livré ; dépendances sous `artifacts/` à conserver |
| Graphique de Pareto, plusieurs contraintes | Dix valeurs de ε, allocation sous budget, frontière historique tracée, diagnostic séparé de la politique finale | Livré dans le notebook et `pareto/front_pareto_contrainte.png` ; front auxiliaire, pas front officiel caché |
| Plan de surveillance | `PLAN-GOUVERNANCE-EQUIALGO.md` : rôles, fréquence, seuils proposés, escalades, recours, arrêt et reprise | Livré ; seuils non officiels, rôles à attribuer avant un éventuel usage réel |
| `presentation.pdf` | Support de sept diapositives et `PITCH-EQUIALGO.md` minuté pour cinq minutes | Livré ; répétition orale par l'équipe encore nécessaire |
| Dépôt GitHub public ou partagé avec le jury | `https://github.com/yasserzanari/CodeMl2026-EquiAlgo` | Public; page et livrables visibles sans connexion lors du contrôle du 3 octobre 2026 |
| Exécuter le notebook officiel avant modification | Rejeu intégral des cellules officielles dans `baseline_officielle/` | Exécution actuelle confirmée ; la chronologie « avant toute modification » des anciens travaux n'est pas attestée |

Le support de pitch, le code et les résultats ne sont pas des garanties de points. Le jury apprécie le diagnostic (25), la technique (35), la gouvernance (25), le pitch et le code (15). Les deux composantes techniques nécessitent la référence indépendante non fournie. L'erreur d'enveloppe donnerait zéro aux deux composantes ; cette erreur n'est pas présente ici.

## Matrice des affirmations

Les statuts portent sur la preuve de l'affirmation, pas sur la qualité globale du projet.

| Affirmation | Statut | Portée justifiée |
|---|---|---|
| Le CSV respecte le format et le budget sur la cohorte des 4 000 demandes | supported | Contrôle intégral des lignes et rejeu indépendant |
| La procédure de sélection du modèle est reproductible | supported | Validation imbriquée 5 × 3, graines et prétraitements documentés, rejeu des paramètres |
| Certaines variables contiennent de l'information régionale | supported | Prédiction du groupe sur 10 000 historiques, plis disjoints, AUC recalculées par rangs |
| Supprimer la région et le postal élimine les associations régionales | unsupported | Baseline rejouée : écart de sélection encore 17,31 points ; autres proxies mesurés |
| Une contrainte de parité produit un compromis avec l'accord historique | supported | Grille fixée, 48 cohortes faisables vérifiées ; comparaisons agrégées seulement sur cinq plis complets |
| La règle finale réduit les écarts de taux observés | supported | Description des cohortes présentes ; ne généralise pas automatiquement à de futurs candidats |
| La règle est équitable au sens du mérite réel | not tested | Référence absente ; les décisions historiques ne la remplacent pas |
| La correction supprime causalement les effets des inégalités | not tested | Retrait de termes directs d'un modèle associatif ; R/heures peuvent rester des proxies |
| Le système est prêt à décider en production réelle | partially supported | Code et proposition de gouvernance présents ; définition du mérite, approbations, rôles, données indépendantes et validation externe manquent |
| Le dépôt est accessible aux juges | supported | Dépôt public vérifié : `https://github.com/yasserzanari/CodeMl2026-EquiAlgo` |

## Sources, indépendance et limites

Les données historiques, les prédictions hors pli et les règles ont été relues par des sous-agents distincts. Le parent a recalculé les 55 AUC par pli, 11 AUC agrégées et les métriques de 48 allocations faisables à partir des sorties, sans modifier le modèle. Cette séparation apporte une revue de procédure ; elle ne crée pas une nouvelle vérité terrain ni un jeu de test indépendant. Les données avaient été explorées auparavant. Les anciens retours HxBuddy restent archivés et ne servent pas à choisir les réglages de ces compléments.

Les analyses régionales reposent sur des demandes supposées échangeables, sans validation temporelle ni liens familiaux observables. Le contrôle par permutation est un contrôle de plausibilité, pas un test d'absence de toutes les fuites possibles. Les intervalles et barres des figures sont descriptifs et identifiés comme tels.

Le CSV et le code du modèle ont été figés pendant les compléments. Les résultats de référence restent 88,1572 % de F1 contre le comité pour le modèle complet et 84,3084 % pour la politique neutralisée. Ce sont des métriques historiques, distinctes du mérite caché, du leaderboard et du score officiel sur 35.

## Contrôles et actions restantes

Les preuves machine sont `artifacts/equialgo/complements_20261003/verification_independante.json`, `verification_integration.json`, et les vérifications propres aux sous-dossiers. Les figures sont inspectées séparément. Le notebook est exécuté de haut en bas et sauvegardé avec sorties ; la mise en page HTML globale reste à regarder manuellement dans Jupyter, l'accès local par navigateur étant bloqué dans cet environnement.

Actions humaines restantes : relire les choix normatifs, répéter le pitch, vérifier le rendu du notebook dans Jupyter, transmettre les prédictions à HxBuddy si requis et finaliser la soumission Devpost. Le dépôt GitHub est public et contient les livrables; aucun envoi HxBuddy ni soumission finale Devpost n'a été effectué.
