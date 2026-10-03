# Plan de surveillance et de recours

Ce plan propose un fonctionnement pour une éventuelle expérimentation en production. Les données du défi sont synthétiques. **Les rôles, délais et seuils ci-dessous sont des propositions de l'équipe, pas des exigences officielles ni des garanties statistiques.** L'institution doit les approuver avant toute utilisation réelle. Aucun déploiement réel n'a été effectué.

## Responsabilité et légitimité

Le responsable du programme de bourses répond des décisions et du budget. Le responsable des données contrôle leur qualité et les accès. Le responsable du modèle entretient le code et reproduit les résultats. Un comité d'équité comprenant une représentation étudiante et régionale examine les hypothèses, les effets distributifs et les recours agrégés. Une personne chargée des recours, distincte de l'équipe de modélisation, conduit la révision des dossiers contestés. Ces fonctions sont à attribuer explicitement, sans supposer des personnes déjà nommées.

Le programme doit faire approuver le sens du mérite avant de prendre une décision réelle. Le choix de compenser les heures de travail et celui d'un budget de 40 % sont normatifs. Les décisions historiques ne constituent pas une référence de mérite. La neutralisation du revenu et du groupe régional ne démontre pas une correction causale. Les heures et la cote R peuvent toujours transmettre des inégalités. Les personnes qui ne travaillent pas parce qu'elles ont des responsabilités de soin, un handicap ou des contraintes d'accès à l'emploi pourraient être pénalisées par la compensation retenue. L'équipe doit faire examiner ces risques par les parties concernées sans collecter de données sensibles inutiles.

## Tableau de suivi proposé

Un point désigne ici un point de pourcentage. Les comparaisons se font sur des cohortes comparables, avec effectifs et intervalles d'incertitude. Un seuil de surveillance signale une investigation, pas une preuve de discrimination.

| Mesure | Fréquence et rôle responsable | Seuil proposé | Action et escalade |
|---|---|---|---|
| Schéma, identifiants, valeurs manquantes, domaine des caractéristiques | Chaque lot, responsable des données | Tout doublon d'identifiant, toute colonne obligatoire absente ou valeur invalide | Bloquer l'export. Corriger la source, documenter la cause, rejouer intégralement les contrôles. Aucune imputation silencieuse des données de décision. |
| Budget et reproductibilité | Chaque lot, responsable du modèle | Tout écart au budget approuvé de 40 % (arrondi explicite hors défi), toute divergence de hash ou de rejeu | Bloquer l'export et avertir le responsable du programme. Pour le défi, 1 600 décisions positives exactement ; plage officielle 1 440–1 760. |
| Données hors support de développement | Chaque lot, responsable des données | Plus de 1 % des dossiers hors des bornes observées d'une variable du score, ou nouvelle catégorie de contexte | Revue des dossiers affectés et de leur provenance avant validation du lot. Ne pas extrapoler sans justification. |
| Dérive de cote R et d'heures par région | Mensuellement si demandes continues, et avant chaque campagne, responsable des données | Écart standardisé absolu de moyenne > 0,25 par rapport au développement | Enquête sur la collecte, la population et les changements de politique. Comparer distributions complètes et effectifs. Le responsable du programme décide d'une suspension si le score perd sa pertinence. |
| Taux d'octroi entre les deux groupes et les cinq régions | Chaque lot, comité d'équité | Écart entre centres et régions éloignées > 5 points, ou variation > 3 points par rapport à la campagne de référence approuvée | Expliquer la composition des demandes, examiner les dossiers proches du seuil et les variables proxies. Aucune retouche automatique des quotas régionaux. |
| Égalité des chances et concordance avec mérite indépendant | À chaque campagne avec référence disponible, revue trimestrielle si flux continu, comité d'équité | Alerte exploratoire si écart absolu de TPR > 5 points ou hausse > 3 points par rapport à la référence approuvée | Calculer les incertitudes, enquêter sur les erreurs et saisir le responsable du programme. Si la qualité de référence est insuffisante, afficher « non mesurable » et maintenir la supervision humaine. |
| Recours, motifs et corrections | Chaque mois, responsable des recours | Toute erreur systémique confirmée ; ou hausse de 5 points du taux de décisions corrigées, avec effectifs publiés | Réviser les cas concernés, chercher les causes communes et informer le comité d'équité. Étendre la révision aux dossiers comparables, sans attendre qu'ils déposent un recours. |

Les seuils d'équité sont volontairement des points de départ à discuter. Le faible écart descriptif du fichier de défi (0,0207 point entre deux groupes) n'est pas un seuil de production. Les petits groupes doivent être décrits avec prudence. Sous 100 dossiers dans un groupe, on publie des effectifs et intervalles en précisant l'instabilité ; on ne classe pas un groupe comme « conforme » sur la seule estimation ponctuelle. Pour les TPR, on indique aussi le nombre de personnes reconnues méritantes dans chaque groupe. Les contrôles de groupe ne doivent pas rendre des individus identifiables.

## Mesurer l'égalité des chances sans reproduire le comité

Une future référence exige une définition du mérite approuvée, une collecte consentie et autorisée, et une évaluation humaine indépendante des décisions historiques. Un échantillon doit couvrir les personnes retenues et refusées, ainsi que chaque région, pour limiter les étiquettes sélectives. Les évaluateurs suivent un protocole commun, documentent leurs désaccords et n'utilisent pas la décision du modèle comme vérité. L'équipe ne doit pas assimiler automatiquement la réussite scolaire ultérieure au mérite : l'accès à une bourse peut influencer cette réussite.

L'égalité des chances compare `TPR_g = vrais positifs_g / personnes méritantes_g`. Les vrais positifs et le dénominateur nécessitent cette référence indépendante. La parité démographique compare seulement les taux d'octroi. Elle est observable sur le fichier d'évaluation et utile au suivi, mais ne valide pas le critère technique officiel. En l'absence de référence, aucune valeur d'EO ni aucun score sur 35 n'est annoncé.

## Recours et information des candidats

Proposition à faire approuver : fournir un avis expliquant le rôle du score, les facteurs utilisés, le budget et le droit à une révision humaine. Accuser réception d'une contestation sous cinq jours ouvrables et viser une réponse motivée sous vingt jours ouvrables. Permettre la correction des données et l'examen des circonstances absentes du modèle. Ne jamais faire traiter un recours uniquement par le même classement automatique.

La personne chargée des recours consigne la demande, les pièces, la décision et la justification. Le responsable du programme gère explicitement l'effet d'une correction sur le budget, par une réserve approuvée ou une procédure de réattribution documentée. Un recours ne doit pas entraîner une sanction. Ces délais et modalités restent des propositions opérationnelles, pas un exposé de droits juridiques.

## Versionnement, arrêt et retour à une version antérieure

Chaque lot conserve, avec accès limité : version du code, environnement, paramètres, protocole de validation, hashes des données et du CSV, date, responsable ayant approuvé l'export, résultats de contrôle et journal des exceptions. Le registre lie chaque résultat à une empreinte exacte du fichier. Les accès et la durée de conservation sont à fixer par le responsable des données selon la finalité approuvée, sans publication de dossiers individuels.

Une erreur de données, une impossibilité de reproduire ou un défaut systémique déclenche le gel des nouvelles décisions automatiques. Le responsable du programme autorise la reprise après correction, rejeu des contrôles et revue du comité d'équité. Le retour à une version antérieure n'est possible que si cette version a été approuvée pour le même contexte et n'est pas la cause de l'incident. À défaut, les dossiers passent en examen humain. Le modèle historique biaisé n'est pas un choix de retour automatique.

Aucune réactualisation continue à partir des seules décisions de l'institution. Toute nouvelle version refait une validation séparée, l'audit des proxies, les analyses de sous-groupes et la revue des hypothèses. Une nouvelle version ne remplace le modèle courant qu'après approbation documentée. Le responsable du programme et le comité d'équité revoient les choix normatifs avant chaque campagne et après tout incident majeur.

## Sources et statut

- Consignes officielles françaises, sections Mandat, Contraintes, Livrables et Notation : `HxBuddy-Challenges/03-ivado-equialgo/equialgo-participants/consignes-fr.pdf`.
- Résultats internes reproduits : `artifacts/equialgo/methode_finale_20261003/resultats/rapport.json`.
- Définitions des métriques : [Fairlearn, Common fairness metrics](https://fairlearn.org/main/user_guide/assessment/common_fairness_metrics.html).
- Tous les seuils et délais de ce plan sont des propositions. Leur adoption en production, l'attribution des rôles et la création d'une référence indépendante restent à réaliser.
