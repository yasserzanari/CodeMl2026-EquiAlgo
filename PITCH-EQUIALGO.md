# Pitch ÉquiAlgo : cinq minutes

Durées cibles totalisant 5:00. Environ 670 mots ; répéter à voix haute et ajuster les pauses. Les sources sont dans les notes du PPTX.

## 1. ÉquiAlgo (0:00–0:25)

Nous proposons une politique de financement simple, reproductible et explicite sur ses limites. L'objectif est d'auditer les décisions historiques et de réduire certains effets du contexte. Notre fichier accorde 1 600 bourses à 4 000 personnes. Le mérite indépendant reste caché : notre présentation distingue donc les résultats mesurés, les choix normatifs et les questions encore ouvertes.

## 2. Diagnostic des biais (0:25–1:10)

Les décisions historiques favorisent les grands centres : les consignes rapportent 48,4 % d'octroi, contre 27,3 % dans les régions éloignées. La différence de cote R explique une partie de cet écart, sans identifier les causes du reste. Nous avons rejoué le notebook officiel inchangé. L'écart de taux d'octroi du modèle est de 18,76 points. Retirer la région puis le code postal laisse encore 17,31 points. La distance, le revenu et les heures transmettent aussi de l'information régionale. Ces associations motivent un audit quantitatif des proxies, sans transformer une corrélation en preuve causale.

## 3. Politique d’attribution (1:10–2:00)

Nous ajustons une régression logistique sur la cote R, les heures, le logarithme du revenu et le groupe régional. Ensuite, nous retirons les termes directs de revenu et de groupe du classement. Le score devient la cote R, plus 0,14343 fois les heures travaillées. Les 1 600 premiers reçoivent une bourse. Les égalités utilisent un hash stable de l'identifiant. La compensation des heures et le budget de 40 % sont des choix normatifs explicites. Ils n'ont pas été choisis pour maximiser HxBuddy dans cette reprise. Les essais précédents étaient toutefois connus. La méthode ne mesure pas une probabilité de mérite et ne prétend pas éliminer les inégalités structurelles.

## 4. Validation séparée de la sélection (2:00–2:50)

Nous comparons trois familles et trois régularisations avec une validation imbriquée. Les plis sont stratifiés par région et décision historique. La règle d'une erreur standard privilégie une configuration simple lorsque les résultats sont proches. Tous les plis retiennent le modèle compact avec C égal à 0,1. Le modèle du comité obtient 88,16 % de F1 macro, et la politique neutralisée 84,31 %, contre les mêmes décisions historiques. Cette baisse d'accord ne permet pas de conclure sur le mérite. Deux cents bootstraps donnent un poids des heures entre 0,129 et 0,161. C'est une stabilité conditionnelle, pas une garantie sur le test caché.

## 5. Contrainte d’équité et compromis (2:50–3:40)

Nous balayons dix réglages de la contrainte de parité sur les scores du comité produits hors pli. Une contrainte de 0,5 point réduit l'écart moyen à 0,42 point, avec 85,38 % d'accord historique. Sans contrainte, l'écart atteint 22,38 points et l'accord 88,76 %. Cette baisse d'accord n'établit aucun gain de mérite. Pour la politique finale, les contraintes d'au moins 0,5 point sont inactives : elles conservent les mêmes décisions et l'écart de 0,0207 point. Les cinq régions varient entre 38,29 et 41,55 %. L'égalité des chances et les 35 points techniques restent inconnus, faute de mérite indépendant.

## 6. Surveillance et recours (3:40–4:30)

La gouvernance précise qui intervient et quand. À chaque lot, les responsables des données et du modèle bloquent l'export en cas d'invalidité, de budget incorrect ou de divergence de reproduction. Le comité d'équité suit les cinq régions. Nous proposons une enquête au-delà de cinq points d'écart de taux, avec effectifs et incertitude. Ce seuil n'est pas officiel. Une mesure d'égalité des chances attend une référence indépendante, couvrant les personnes retenues et refusées. Une personne distincte du modèle traite les recours. Les erreurs systémiques suspendent les nouvelles décisions automatiques. Chaque version conserve ses données, paramètres et validations pour permettre une révision traçable.

## 7. Livrable et limites (4:30–5:00)

Le dossier rassemble un CSV contrôlé, un code reproductible, un notebook d'audit et ce support. Nous conservons l'ancien candidat et tous les résultats. Notre recommandation repose sur une méthode explicable, pas sur une promesse de classement. La priorité suivante, pour un usage réel, serait de définir et valider une référence de mérite indépendante avec les parties concernées. Le partage du dépôt et la soumission restent des actions manuelles de l'équipe.

## Sources

- Consignes officielles françaises : sections Contraintes, Livrables, Notation. HxBuddy-Challenges/03-ivado-equialgo/equialgo-participants/consignes-fr.pdf
- Baseline officielle rejouée : artifacts/equialgo/complements_20261003/baseline_officielle/sorties.txt
- Méthode, résultats et limites : RAPPORT-METHODOLOGIQUE-EQUIALGO.md ; artifacts/equialgo/methode_finale_20261003/resultats/rapport.json
- Fairlearn : https://fairlearn.org/main/user_guide/assessment/common_fairness_metrics.html
- Validation imbriquée : https://scikit-learn.org/stable/modules/cross_validation.html
- Gouvernance proposée : artifacts/equialgo/complements_20261003/presentation/plan_gouvernance.md
- Balayage de contrainte DP : artifacts/equialgo/complements_20261003/pareto/ ; ε=0 infaisable dans 2/5 plis, sans moyenne globale.