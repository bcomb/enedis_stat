Estimez le coût mensuel et annuel sur une année, de janvier à décembre, à partir des données d'Enedis (consommation horaire) et de la grille tarifaire des différents abonnements (BLEU/VERT en option base/hchp/tempo).

# Exécution du script
`python enedis_stat.py`

Dans le répertoire 'data/2023', vous trouverez 4 fichiers :
- enedis-hours.csv : contient la consommation horaire sur l'année
- hchp.csv : contient les tarifs heures creuses et heures pleines
- price.csv : contient les prix des offres
- tempo_calendar.csv : la couleur des jours de l'offre TEMPO

# Comment récupérer ses données
Rendez-vous sur le site : https://mon-compte-particulier.enedis.fr<br>

Dans la section `Gérer l'accès à mes données`, activez `Enregistrement de la consommation horaire` ainsi que `Collecte de la consommation horaire`

Dans la section `Télécharger mes données`<br>
Sélectionnez `Consommation horaire` et choisissez la période du 01/01 au 31/12 de l'année souhaitée

Ce script ne fonctionne qu'avec les données horaires.

# Calendrier TEMPO
Vous pouvez trouver le calendrier TEMPO ici : https://www.rte-france.com/eco2mix/telecharger-les-indicateurs
