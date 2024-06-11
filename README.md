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
- Scaphandre (https://github.com/hubblo-org/scaphandre) - Nous utiliserons la version 0.5.0 de Scaphandre, récupérable de la façon suivante : 
`wget https://github.com/hubblo-org/scaphandre/releases/download/v0.5.0/scaphandre-x86_64-unknown-linux-gnu`

## Partie 1 - Utilisation de Scaphandre
Par simplicité, nous allons utiliser les fonctions stress comme applications à mesurer durant ce TP. 
Ces applications, en plus d'être facile à lancer, conduisent à une consommation de ressource très stables et peuvent être configurées pour consommer une 
quantité de ressources données. 

**Note :** Stress est une suite d'applications permettant d'effectuer des tests de montée en charge configurables sur différents composants d'un serveur (CPU, mémoire, 
IO, ...). 

Scaphandre peut s'utiliser de plusieurs façon : 
- En mode "ligne de commande" : en sélectionnant une sortie `stdout`, Scaphandre affiche la consommation estimée des 15 processus les plus consommateurs
- En mode "script" : en sélectionnant la sortie `json`, Scaphandre écrit ses estimations dans un fichier de sortie au format JSON. 
- En mode "export" : Scaphandre peut exporter ses résultats vers un composant tier comme Prometheus. Un fichier docler-compose est proposé dans le répertoire
Github du projet pour déployer facilement un Dashboard Scaphandre. 

### Tâche 1.1 - Puissance sur un coeur CPU
Dans un premier temps, nous allons découvrir Scaphandre en le testant sur diverses fonctions stress. Vous pouvez trouver la liste des fonctions proposées 
par stress via la commande `stress-ng --cpu-method which`. En lançant diverses fonctions stress sur un même nombre de CPU, voyez-vous une différence de consommation ? 
Lister quelques exemples de commandes stress et leur coût associé en Watts.

Ecrire un script python permettant de lancer une commande stress passée en paramètre et d'évaluer sa consommation via Scaphandre.

### Tâche 1.2 - Puissance sur plusieurs coeurs CPU 
Nous allons maintenant évaluer la consommation d'un même stress sur plusieurs coeurs. Pour charger N coeurs, stress lance N instances de l'application 
demandée. Il s'agit donc du même programme, lancé N fois. Pour un stress donné, évaluer sa consommation quand il est lancé sur 1 coeur, puis plusieurs. Qu'observez-vous 
vis à vis de l'évolution de la consommation de chaque stress par rapport à l'augmentation de la charge serveur ?

Pouvez-vous automatiser une telle expérimentation en Python ? Reproduisez l'expérimentation sur plusieurs opérations de stress différentes.

Des utilitaires comme `htop` sont très pratique pour étudier la consommation de ressources de notre serveur en temps réel. Etudier la consommation énergétique de nos 
différents stress en comparaison de leur consommation CPU. Que pourriez-vous en déduire entre le lien entre pourcentage d'utilisation CPU et consommation énergétique ?
Plus précisément, la consommation énergétique est-elle directement liée au pourcentage d'utilisation CPU ? 

**Notes :** Pour faciliter la récupération de la consommation des différents stress lancé, il est conseillé de les executer dans des *cgroups*. Pour rappel, 
les cgroups sont une fonctionnalité de Linux permettant de lancer plusieurs processus dans des groupes logiques. Les cgroups sont à l'origine utilisés pour 
affecter des limites de ressources (CPU, mémoire...) à divers groupes de processus. Nous les utiliserons ici pour faciliter la récupération des PIDs des stress
lancés. 

Quelques commandes pour manipuler les cgroups :
- Créer un cgroup : `cgcreate -g cpu:/MONCGROUP`
- Lancer un stress dans un cgroup : `cgcreate -g cpu:/MONCGROUP stress -c 1`
- Afficher les PIDs des processus lancés dans notre cgroup : `cat /sys/fs/cgroup/MONCGROUP/cgroup.procs`

### Tâche 1.3 - Puissance sur plusieurs programmes en parallèle
Nous avons commencé à voir qu'un même programme peut induire une consommation différente selon son contexte d'execution. Nous allons illustrer cela un peu plus en étudiant la 
consommation d'un stress selon qu'il est lancé seul ou en parallèle d'autres stress. Le scénario d'expérimentation est le suivant. 

1) Lancer un premier stress et étudier sa consommation énergétique. 
![Un stress lancé seul](./figures/P_0_alone.png)

2) Lancer un second stress en parallèle du premier. 
![Deux stress lancés en parallèle](./figures/P_0_et_P_1.png)

Qu'observez-vous vis à vis du profil de consommation du premier stress ?
Pour rappel, les stress ont des comportements très stables. Retrouve-t-on ce comportement lorsque du "bruit" est généré 
en parallèle de notre stress ?

Dans des environnements cloud, les services numériques déployés par les utilisateurs sont bien souvent mutualisés sur un nombre réduit de serveurs. 
Un utilisateur n'a donc pas de vision sur l'état du serveur sur lequel il est déployé : ses spécifications et l'évolution de sa charge due aux autres 
utilisateurs. De ce que vous observez sur ces expérimentations, que pouvez-vous dire des estimations de consommations fournies par ces sondes logicielles 
dans ces environnements cloud ? 

### Tâche 1.4 - Consommation énergétique d'un stress
Nous nous sommes intéressés ici qu'à la puissance estimée d'un stress selon son contexte d'execution. Nous avons vu notamment qu'elle diminue 
en fontion du nombre de stress lancé. Qu'en est-il de sa consommation énergétique ?

**Note :** pour rappel, la consommation énergétique en Joules correspond à la puissance (en Watts) multiplié par le temps. 

A partir d'une certaine charge, une contention sur les ressources serveurs commence à apparaitre. Cette contention emmene à une augmentation 
du temps d'execution. Cette augmentation compense-t-elle la réduction du coût énergétique à haute charge ? 

Il est possible de configurer stress pour lancer un nombre défini d'opérations, garantissant une même quantité de travail. En vous basant sur 
les scripts précédents, dressez la courbe de la consommation énergétique (en Joules) d'un stress en fonction du nombre de coeurs chargés. 
Observez-vous toujours une réduction de la consommation avec l'augmentation de la charge serveur ?

Nous allons maintenant nous intéresser à la capacité de scaphandre à correctement diviser la consommation énergétique d'un serveur sur plusieurs processus. Lancez un stress 
d'un nombre fixe d'opérations et estimez sa consommation en joules. Lancez en un autre et estimez sa consommation en joule. Lancez les deux en parallèle et estimez leurs 
consommation respectives. Pour deux stress A et B, obtenez-vous toujours une même relation d'ordre entre consommation "seule" de A puis de B et la consommation 
"en parallèle" de A et B ?

## Partie 2 - Comprendre la consommation énergétique d'un serveur
Nous avons vu dans la première partie que la consommation énergétique d'un programme (ici *stress*) fluctue en fonction de son environnement d'execution. 
Nous allons dans cette partie essayer de comprendre un peu mieux pourquoi.

### Tâche 2.1 - Profil de consommation d'un serveur 
Nous avons vu dans la tâche 1.2 qu'un même stress ne consommait pas autant d'énergie selon s'il était lancé sur un ou plusieurs coeurs en parallèle. Nous voulons
ici étudier l'évolution de la courbe de consommation de notre serveur en fonction du nombre de coeurs chargés par un stress. Nous nous intéresserons ici à la 
consommation globale du host, pas à la consommation individuelle estimée de chaque programme. 

Ecrire un script permettant d'illustrer la consommation de votre serveur en fonction du nombre de coeurs chargé par un stress. Dresser son profil de consommation 
de 0 à MAX coeurs. Comment charactériser la courbe de consommation de ce serveur ? Quel impact aura cette courbe de consommation sur le coût d'une application, selon 
qu'elle soit executée sur un serveur à vide ou un serveur déjà remplis ? 

Reproduire la construction de ce profil via différents stress. Qu'observez-vous ? Qu'en déduisez-vous sur la relation entre charge CPU et consommation énergétique ? 

### Tâche 2.2 - Impact de Turbo boost et hyperthreading sur la consommation énergétique
Les processeurs modernes embarque plusieurs fonctionnalités permettant d'optimiser leurs performances et leur consommation énergétique en fonction de leurs besoins. 
Nous allons étudier l'impact de deux de ces fonctionnalités sur le profil de consommation énergétique d'un serveur : turbo boost et hyperthreading. 

Pour rappel : 
- Turbo boost permets d'ajuster dynamiquement la fréquence des coeurs du processeur en fonction des besoins de calculs 
- Hyperthreading permets de faire fonctionner plusieurs threads en parallèle sur un même coeur (via un mécanisme de "coeurs virtuels")

Par défault ces deux mécanismes sont activés sur Grid5000. C'est en effet le type de configuration que l'on trouve activé par défault sur les serveurs car ils 
ont un intérêt significatif sur leurs performances. Nous allons nous intéresser ici à leur impact sur la courbe de consommation d'un serveur. 

Grid5000 permets d'activer et désactiver dynamiquement ces fonctionnalités. Vous trouverez comment faire dans la documentation présente ici : https://www.grid5000.fr/w/CPU_parameters#Setting_CPU_parameters:_Hyperthreading,_C-State,_P-State_and_Turboboost

Essayez de reproduire la construction du profil de consommation énergétique du serveur (Tâche 2.1) en désactivant hyperthreading et turbo boost. Qu'observez-vous ? 
Quelle est la différence entre la courbe que vous observez ici et celle que vous avez obtenu lors de la tâche 2.1 ? 
