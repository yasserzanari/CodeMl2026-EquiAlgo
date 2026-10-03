# Compléments de preuves avant remise

Le modèle et `predictions.csv` restent figés. Le quota officiel est une plage inclusive de 36–44 % sur 4 000 candidatures ; 40 % est le choix de politique actuel. Aucun résultat supplémentaire ne sert à sélectionner une nouvelle règle.

L'analyse de stabilité des allocations réutilise les 200 poids bootstrap déjà calculés sur l'historique, conditionnellement à la spécification compacte. Pour chaque poids, la même fonction d'allocation exacte attribue 1 600 bourses aux mêmes 4 000 demandes. On rapporte le nombre de changements contre la décision actuelle, sa distribution et les fréquences de sélection individuelles, sans étiquette de mérite. Une fréquence de sélection n'est pas une probabilité de mérite, et ce bootstrap ne couvre pas l'incertitude normative, les familles de modèles ou les changements futurs de population.

La comparaison historique principale est fixée au même budget de 40 % dans chaque pli externe : score du comité complet et score neutralisé. Les mesures au seuil 0,5 restent un diagnostic séparé. On ne recalcule pas des scores cachés et on ne change pas les règles après observation.

Le notebook sera rendu dans JupyterLab, exécuté depuis un kernel neuf après les corrections de présentation, puis relu cellule par cellule. Les figures et tables détaillées auront des intitulés français et des liens de preuve. La présentation courte respecte les cinq minutes officielles ; les détails seront une annexe distincte, hors temps de pitch. Le minutage écrit ne remplace pas une répétition orale.
