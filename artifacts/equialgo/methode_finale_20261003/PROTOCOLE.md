# Décision méthodologique — protocole avant calcul

Le 3 octobre 2026, l'utilisateur demande explicitement d'arrêter de choisir les modèles selon le leaderboard et de retenir la méthode la plus défendable, avec predictions.csv. Cette décision remplace l'objectif de certifier un record caché. Les résultats HxBuddy restent archivés, mais ne servent ni à sélectionner un poids ni un quota dans ce protocole. Les recherches antérieures sont connues : ce n'est pas une analyse aveugle ou une validation indépendante nouvelle.

## Contrat et choix normatifs

Une demande, une décision binaire. Variables supposées disponibles au dépôt : cote R, heures et contexte; dates non fournies. Les labels disponibles sont ceux du comité biaisé, pas le mérite. L'objectif technique final reste une allocation académique tenant compte de la charge de travail, sans effet DIRECT du lieu, du revenu, du programme, de la distance ou du statut familial à caractéristiques R/heures fixées. Cela n'est pas une preuve causale d'équité; R et heures peuvent eux-mêmes porter des inégalités structurelles.

Choix assumés : la cote R est le critère académique; les heures sont une compensation de charge, avec coefficient positif appris après ajustement du contexte. Ce choix normatif est cohérent avec la tâche mais n'est pas une définition officielle du mérite. Pas de bonus ad hoc de première génération/distance. Budget fixé avant calcul à **40 % = 1 600/4 000**, milieu de la plage autorisée 36–44 %. Ce budget n'est ni une exigence de 1 600 bourses ni un optimum statistique prouvé. Départage hash stable préexistant, sans information de mérite.

## Modèle et validation

Régression logistique régularisée, trois spécifications candidates : A R/heures seuls (contrôle de l'omission du contexte); B R/heures/log-revenu/groupe éloigné (compacte); C R/heures/log-revenu/distance/première génération + régions et programmes catégoriels (contexte étendu). C dans {0,1; 1; 10}. Tous les prétraitements et vocabulaires ajustés au train de chaque pli.

Cinq plis externes région × décision, seed 20261003; trois plis internes, seed 20261004. Critère auxiliaire log-loss des décisions historiques. Dans chaque train externe : calcul des pertes internes des neuf configurations, seuil de simplicité = meilleur mean + son écart-type/sqrt(3), puis retenir la famille la plus simple à l'intérieur de ce seuil, et la régularisation la plus forte admissible. Réestimer sur le train externe; métriques externes de l'algorithme complet de sélection. Même sélection sur tout l'historique pour le modèle final. Pas de choix à partir des scores externes ni d'HxBuddy.

Diagnostic du comité : F1 macro et accuracy au seuil fixe 0,5, log-loss et Brier hors pli. Politique : retirer les termes de contexte du score logistique, normaliser par le coefficient R, donc **R + poids_heures × heures**. Quota global 40 % par cohorte. Coefficients R et heures doivent être positifs; sinon arrêter la génération et documenter. Aucun score probabiliste n'est présenté comme probabilité de mérite.

La validation du comité mesure l'ajustement d'un mécanisme historique; la politique neutralisée est évaluée séparément contre l'historique, avec mention explicite de sa cible imparfaite. Aucune confusion avec le F1 de mérite ou les points IVADO. Absence de timestamps : hypothèse IID des demandes, avec audit de doublons et IDs; cette validation ne prouve pas le transport temporel.

## Stabilité et équité

200 bootstraps stratifiés région × décision, seed 20261005, configuration finale fixe; intervalle descriptif percentile 2,5–97,5 du poids des heures (conditionnel à ce modèle, pas toute l'incertitude de sélection). En plus, ajuster la configuration finale en excluant successivement chaque région pour inspecter les coefficients. Déclarer la variabilité; ne pas sélectionner un poids dans l'intervalle pour augmenter un score.

Mesurer sélection, TPR et FPR contre comité par régions sur données hors pli, en séparant ces métriques de l'égalité des chances vraie, inconnue. Faire varier la neutralisation du contexte de 0 à 1, quota constant, pour visualiser l'accord historique et la parité observée. Choix final = neutralisation complète, décidé normativement avant calcul et non au meilleur point du graphique.

Sur la cohorte d'évaluation, front diagnostique de contraintes de parité démographique ε = 0; 0,005; 0,01; 0,02; 0,05; sans contrainte. Pour chaque ε faisable, maximiser la somme des scores R/heures sous budget 1 600 et écart de taux <=ε. L'utility affichée est le score académique construit conservé, pas l'utility officielle cachée. Signaler l'infaisabilité éventuelle de ε=0 à cause des entiers. Le CSV final garde le classement global sans quota régional forcé : la parité démographique n'est pas l'égalité des chances, et égaliser artificiellement les taux n'est pas automatiquement souhaitable.

## Handoff et contrôles

Sauvegarder le modèle en JSON, les choix internes, les prédictions hors pli, les métriques, l'intervalle/stabilité et les courbes. Générer d'abord un CSV séparé; vérifier format, ID/order, 4 000 lignes, 0/1, 1 600 bourses, aucun vide/doublon, invariance du score au contexte et à l'ordre, monotonie. Comparer aux anciens CSV par ID et signaler les doublons éventuels, sans modifier le modèle pour forcer la nouveauté.

Archiver les octets de l'ancien predictions.csv et de l'ancien notebook avant de mettre à jour les fichiers à la racine. Valider/reproduire les décisions dans un processus séparé. Créer model_corrige.py et un notebook d'audit cohérent et exécuté. Les métadonnées doivent distinguer le meilleur leaderboard historique et la nouvelle recommandation méthodologique, dont le score HxBuddy sera inconnu. Aucune soumission ni publication.

Sources : README et consignes officielles locaux; [validation croisée scikit-learn](https://scikit-learn.org/stable/modules/cross_validation.html); [définitions et limites des métriques Fairlearn](https://fairlearn.org/main/user_guide/assessment/common_fairness_metrics.html).
