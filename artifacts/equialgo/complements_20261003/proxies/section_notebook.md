## Diagnostic quantitatif des variables proxies

**Question testée : peut-on retrouver le groupe régional à partir des autres caractéristiques ?** La cible de cette analyse est « régions éloignées » (Bas-Saint-Laurent, Côte-Nord, Gaspésie–Îles-de-la-Madeleine), et non l'octroi ni le mérite. Une association géographique n'est pas en elle-même une preuve de discrimination causale ; elle montre pourquoi supprimer la colonne région ne suffit pas.

Le protocole dans `artifacts/equialgo/complements_20261003/proxies/PROTOCOLE.md` a été fixé avant ces calculs : 10 000 demandes historiques, cinq plis stratifiés par région (graine 20261013), régression logistique C=1 sans recherche de paramètres. Standardisation et encodage catégoriel sont appris uniquement dans chaque entraînement. Le revenu est transformé en logarithme. La région, l'identifiant et la décision historique sont exclus des prédicteurs. Chaque individu reçoit exactement une prédiction de validation par modèle. Aucune étiquette cachée n'est utilisée.

| Variable ou ensemble | AUC région, moyenne des 5 plis | Min–max des plis |
|---|---:|---:|
| Code postal seul | 1,0000 | 1,0000–1,0000 |
| Distance au campus | 0,9981 | 0,9975–0,9992 |
| Heures travaillées | 0,8052 | 0,7937–0,8176 |
| Log du revenu familial | 0,6925 | 0,6677–0,7059 |
| Première génération | 0,5896 | 0,5690–0,6050 |
| Cote R | 0,5611 | 0,5418–0,5845 |
| Programme | 0,5528 | 0,5379–0,5702 |
| Cote R + heures | 0,8103 | 0,7985–0,8244 |
| Ensemble sans code postal | 0,9988 | 0,9973–0,9997 |
| Ensemble avec code postal | 1,0000 | 1,0000–1,0000 (arrondi) |
| Ensemble sans postal, cible permutée | 0,5116 | 0,4916–0,5258 |

L'AUC vaut 0,5 pour un classement constant. Les barres représentent la variation entre plis, **pas** un intervalle de confiance. Le contrôle négatif permute une fois la cible régionale (graine 20261014) : il donne une discrimination proche du hasard ; ce test limité ne prouve pas à lui seul l'absence de fuite. Le modèle linéaire ne détecte pas nécessairement tous les signaux non linéaires. Le modèle « cote R + heures » apprend à reconnaître la région : son AUC n'est **pas** celle de notre score d'octroi.

Le postal identifie parfaitement le groupe dans ces données synthétiques : les 18 codes observés appartiennent chacun à un seul groupe. Ils sont tous représentés dans l'entraînement de chaque pli ; aucune catégorie de validation n'est inconnue. Ce résultat vaut pour ces catégories et régions connues, pas pour de nouveaux codes. Même sans le postal, la distance permet presque de reconstituer le groupe : **enlever les colonnes géographiques ne supprime donc pas l'information géographique**.

Les profils descriptifs le confirment : distance moyenne 19,79 km dans les centres contre 221,45 km dans les régions éloignées ; heures 8,97 contre 13,02 ; revenu familial 76 056 $ contre 56 330 $ ; première génération 26,48 % contre 44,40 % ; cote R 27,99 contre 27,33. Le programme est moins discriminant : la proportion éloignée varie de 33,77 % en génie à 46,89 % en arts et lettres. Les différences standardisées et effectifs sont fournis dans `distributions.csv` et `categories.csv` ; elles décrivent des profils et ne répartissent pas causalement les responsabilités.

**Biais observable du comité.** Sur l'ensemble historique, les taux d'octroi sont 48,37 % (6 000 centres) et 27,30 % (4 000 éloignés), soit 21,07 points d'écart. Le modèle compact du comité, en prédictions externes hors pli au seuil 0,5, donne 47,97 % et 25,70 %. La politique neutralisée, avec 40 % d'octroi dans chaque pli, donne 40,30 % et 39,55 %, soit 0,75 point d'écart agrégé. Ce dernier chiffre est différent de la moyenne des écarts absolus par pli (1,53 point) et de l'écart sur les 4 000 candidats d'évaluation (0,0207 point) : populations et agrégations diffèrent.

La baseline officielle, réexécutée inchangée séparément, confirme la difficulté : écart de parité 0,1876 avec toutes les variables, 0,1805 sans région, 0,1731 sans région ni postal. Ces valeurs proviennent de son propre découpage et ne doivent pas être assimilées aux écarts de notre validation imbriquée. Les sorties sont conservées sous `artifacts/equialgo/complements_20261003/baseline_officielle/` ; cette reproduction tardive n'est pas une preuve de son exécution avant le développement.

**Conséquence pour la mitigation.** Le retrait direct du revenu et du groupe est une décision normative transparente, mais les deux variables conservées portent encore de l'information régionale. Le rôle positif des heures suppose que la charge de travail mérite une compensation ; cette hypothèse doit être discutée, surveillée et contestable. Une quasi-parité d'octroi n'établit ni égalité des chances ni exactitude sur le mérite. Sans dates ni identifiants de ménage, la validation ne couvre pas les évolutions futures, les ménages corrélés ni les régions inconnues. L'observation des caractéristiques au dépôt est supposée, faute d'horodatages.

Reproduction depuis la racine : `.\.venv\Scripts\python.exe artifacts/equialgo/complements_20261003/proxies/diagnostiquer.py`, puis `verifier.py` dans le même dossier. Le script ne modifie ni le modèle final ni les prédictions de soumission. Les 55 ajustements et leurs prédictions hors pli sont conservés ; les cellules suivantes relisent ces résultats et redessinent les figures sans réentraîner.

Sources : `HxBuddy-Challenges/03-ivado-equialgo/equialgo-participants/README.md`, consignes françaises fournies, données officielles synthétiques. Aucune information tirée du classement HxBuddy ne détermine ce diagnostic.
