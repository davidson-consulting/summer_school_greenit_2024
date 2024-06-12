
import time
import os
import subprocess
import pathlib
import shutil
import json
import argparse
import matplotlib.pyplot as plt

# Fonction de stress lancé par défaut
DEFAULT_FUNC = "sqrt"

#
# Parse les arguments de ligne de commande
# @returns: les arguments
#
def parseArguments ():
    parser = argparse.ArgumentParser ()
    parser.add_argument ("--func_name", default=DEFAULT_FUNC)
    parser.add_argument ("--duration", type=int, default=5)
    parser.add_argument ("--min_cpu", default=1, type=int)
    parser.add_argument ("--max_cpu", default=os.cpu_count (), type=int)

    return parser.parse_args ()

#
# Les stress sont lancés dans un cgroup (via cgexec) Les cgroups servent à
# regrouper des process dans des groupes pour monitorer/capper les ressources
# auquels ils ont accès. Dans notre cas, ils nous servent à retrouver les PID des
# processus, pour retrouver leurs consommations dans scaphandre
#
# @params:
#    - cgroup: le nom du cgroup (ex: "pg1")
# @returns: la liste des PID du cgroup 'cgroup'
#
def get_pids_in_cgroup(cgroup):
    with open(f"/sys/fs/cgroup/{cgroup}/cgroup.procs", "r") as f:
        return f.read().split("\n")[:-1]

#
# Charge le fichier de traces crée par scaphandre
# @returns: le dictionnaire contenant les traces chargées
#
def loadScaphandreResults () :
    with open("/tmp/results.json", "r") as f:
        return json.load (f)

#
# Plot les résultats
# @params:
#    - pids: la liste des PID (pour filtrer les process interessant)
#    - power_procs: une liste de dictionnaire, un par timestamp, chaque dictionnaire associe un pid à une puissance (ex: [{1 : 100, 2 : 200}, {1 : 120, 2 : 180}, ...])
#    - power_host: une liste de puissance, une par timestamp
#    - imageName: le nom de l'image dans laquelle va être stocker le resultat (i.e. .output/imageName.png)
#
def plotResult (pids, power_procs, power_host, imageName) :
    plt.clf ()
    for p in pids :
        plt.plot ([power_procs [i][str (p)] for i in range (len (power_procs))], label=str (p))
    plt.plot (power_host, label="host")

    plt.legend ()
    plt.savefig (f".output/{imageName}.png", dpi=400)

#
# Lis les résultats et génère les courbes de consommation et d'estimation
# @params:
#    - pids: la liste des PIDS observés
#    - imageName: le nom de l'image dans laquel on va exporter (.output/imageName.png)
# @returns:
#    - [0] : la consommation (puissance) maximal observé sur l'hote
#    - [1] : la consommation (puissance) maximal du stress le plus consommateur
#
def exportResults (pids, imageName):
    pathlib.Path(f".output/").mkdir(parents=True, exist_ok=True)

    power_host = []
    power_procs = []

    #
    # TODO: Les résultats fourni par scaphandre fournisse une liste de consommation (puissance)
    # 1. Remplir le tableau power_host avec la consommation observé sur l'hote par timestamp
    # 2. Remplir le tableau power_procs avec la consommation des processus dans "pids"
    #

    # Retrouver la consommation maximale de l'hote, et la consommation maximal du processus le plus consommateur
    return (0, 0)

#
# Démarre scaphandre
# @returns: Le process de scaphandre
# @info: les résultats sont ecris dans /tmp/results.json
#
def startScaphandre ():
    if os.path.isfile("/tmp/results.json"):
        os.remove("/tmp/results.json")

    return subprocess.Popen (["scaphandre", "json", "--max-top-consumers", "50", "-s", "1", "-f", "/tmp/results.json"])

#
# Lance une experience
# @params:
#    - functionName: le nom de la fonction stress à lancer
#    - nbCores: le nombre de process à lancer (pour charger n cores)
#    - nbOps: le nombre d'operation que doit faire chaque stress
#
# @returns:
#    - [0] : la consommation (puissance) maximal observé sur l'hote
#    - [1] : la consommation (puissance) maximal du stress le plus consommateur
#
def runExperiment (functionName, nbCores, nbOps, duration):
    #
    #  TODO :
    #  1. Lancer scaphandre
    #  2. Lancer nbCores stress dans le cgroup cpu:/pg1
    #  3. Récuperer leurs PID
    #  4. Stopper scaphandre,
    #  5. exporter les résultats
    #

    return (0, 0)


def main (arguments) :
    # Creation du cgroup, pour pouvoir lister les PIDS que l'on va lancer
    subprocess.run(["cgcreate", "-g", "cpu:pg1"])

    hostP = []
    processP = []

    # En faisant monter la charge de 1 à n cores
    for nbCores in range (arguments.min_cpu, arguments.max_cpu + 1) :
        #
        # TODO:
        # 1. lancer les experiences de 1 à N cores
        # 2. récuperer le consommation (puissance) de l'hote et du processus le plus cher
        #
        pass

    print ("Host power : ", hostP)
    print ("Process power : ", processP)


    #
    # TODO: Générer le plot de la consommation puissance en fonction du nombre de coeur
    #
    #


# Python...
if __name__ == "__main__" :
    main (parseArguments ())
