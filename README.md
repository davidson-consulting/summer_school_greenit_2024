# Ecole d'été Green IT 2024 - Expérimentations sur les sondes énergétiques logicielles 

Travaux pratiques visant à mettre en avant les limitations inhérentes des sondes énergétiques logicielles / modèles énergétiques par répartition.

Instructeurs : 
- Emile CADOREL - Ingénieur R&D 
- Dimitri SAINGRE - Ingénieur R&D

Objectifs de la session : 
- Déployer Scaphandre et comprendre son fonctionnement 
- Effectuer des tests de montée en charge 
- Comprendre et mettre en avant les limitations de ces modèles par répartition

## Préparation de l'environnement 
Cette session pratique va se dérouler sur un cluster Nantais de Grid5000 : ecotype. Nous allons dans un premier temps préparer notre environnement technique. 

Réservation d'un serveur : `oarsub -I -p ecotype -l host=1,walltime=7:00 -t deploy`
Déploiement de l'OS : `kadeploy3 ubuntu2204-min`

Installation des dépendances : 
- Quelques packages `apt install stress-ng git`
- Scaphandre 

## Partie 1 - Utilisation de Scaphandre
Par simplicité, nous allons utiliser les fonctions stress comme applications à mesurer durant ce TP. 
Ces applications, en plus d'être facile à lancer, conduisent à une consommation de ressource très stables et peuvent être configurées pour consommer une 
quantité de ressources données. 

Scaphandre peut s'utiliser de plusieurs façon : 
- En mode "ligne de commande" : en sélectionnant une sortie `stdout`, Scaphandre affiche la consommation estimée des 15 processus les plus consommateurs
- En mode "script" : en sélectionnant la sortie `json`, Scaphandre écrit ses estimations dans un fichier de sortie au format JSON. 
- En mode "export" : Scaphandre peut exporter ses résultats vers un composant tier comme Prometheus. Un fichier docler-compose est proposé dans le répertoire
Github du projet pour déployer facilement un Dashboard Scaphandre. 

### Tâche 1 - Puissance sur un coeur CPU
Dans un premier temps, nous allons découvrir Scaphandre en le testant sur diverses fonctions stress. Vous pouvez trouver la liste des fonctions proposées 
par stress via la commande `stress-ng --cpu-method which`. En lançant divers stress sur un même nombre de CPU, voyez-vous une différence de consommation ? 
Lister quelques exemples de commandes stress et leur coût associé par coeurs.

Ecrire un script python permettant de lancer une commande stress passée en paramètre et d'évaluer sa consommation via Scaphandre.

### Tâche 2 - Puissance sur plusieurs coeurs CPU 
Nous allons maintenant évaluer la consommation d'un même stress sur plusieurs coeurs. Pour charger N coeurs, stress lance N instances de l'application 
demandée. Il s'agit donc du même programme, lancé N fois. Pour un stress donné, évaluer sa consommation quand il est lancé sur 1 coeur, puis 2, ... jusqu'au nombre
maximum de coeurs. Qu'en déduisez-vous ?

Pouvez-vous automatiser une telle expérimentation en Python ?

### Tâche 3 - Puissance sur plusieurs programmes en parallèle
Nous avons vu qu'un même programme peut induire une consommation différente selon son contexte d'execution. Nous allons illustrer cela un peu plus en étudiant la 
consommation d'un stress selon qu'il est lancé seul ou en parallèle d'autres stress. Le scénario d'expérimentation est le suivant : lancer un premier stress et 
étudier sa consommation énergétique. Lancer un second stress en parallèle du premier. Qu'observez-vous ?

Note : L'inconvénient d'utiliser que des stress est que le nom de toutes les applications sera le même. Il va être important de récupérer le PID des différents
stress lancés pour pouvoir les distinguer par la suite. 

### Tâche 4 - Consommation énergétique d'un stress
Nous nous sommes intéressés ici qu'à la puissance estimée d'un stress selon son contexte d'execution. Nous avons vu notamment qu'elle diminue 
en fontion du nombre de stress lancé. Qu'en est-il de sa consommation énergétique ? 

Note : pour rappel, la consommation énergétique en Joules correspond à la puissance (en Watts) multiplié par le temps. 

Il est possible de configurer stress pour lancer un nombre défini d'opérations, garantissant une même quantité de travail. Lancez un stress d'un nombre fixe 
d'opérations sur un coeur et estimez sa consommation en joules. Lancez ce même stress sur plusieurs coeurs et étudier l'impact sur la consommation en joules. 

## Partie 2 - Comprendre la consommation énergétique d'un serveur
Nous avons vu dans la première partie que la consommation énergétique d'un programme (ici *stress*) peut fluctuer en fonction de son environnement d'execution. 
Nous allons dans cette partie essayer de comprendre un peu mieux pourquoi.

### Tâche 1 - Profil de consommation d'un serveur 
Nous avons vu dans la tâche 1.2 qu'un même stress ne consommait pas autant d'énergie selon s'il était lancé sur un ou plusieurs coeurs en parallèle. Nous voulons
ici étudier l'évolution de la courbe de consommation de notre serveur en fonction du nombre de coeurs chargés par un stress. Nous nous intéresserons ici à la 
consommation globale du host, pas à la consommation individuelle estimée de chaque programme. 

Ecrire un script permettant d'illustrer la consommation de votre serveur en fonction du nombre de coeurs chargé par un stress. Dresser son profil de consommation 
de 0 à MAX coeurs. Comment charactériser la courbe de consommation de ce serveur ? Quel impact aura cette courbe de consommation sur le coût d'une application, selon 
qu'elle soit executée sur un serveur à vide ou un serveur déjà remplis ? 

Reproduire la construction de ce profil via différents stress. Qu'observez-vous ? Qu'en déduisez-vous sur la relation entre charge CPU et consommation énergétique ? 

### Tâche 2 
