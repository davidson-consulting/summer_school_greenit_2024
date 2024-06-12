
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
# Parse le argument de ligne de commande
# @returns: les arguments
#
def parseArguments ():
    parser = argparse.ArgumentParser ()
    parser.add_argument ("--func_name", default="sqrt")
    parser.add_argument ("--nb_cores", default=int (os.cpu_count () / 2), type=int)
    parser.add_argument ("--scenario", default="scenario.json")
    parser.add_argument ("--duration", default=10, type=int)

    return parser.parse_args ()


#
# Les stress sont lancé dans un cgroup (via cgexec) Les cgroups servent à
# regrouper des process dans des groupes pour monitorer/capper les ressources
# auquels ils ont accés Dans notre cas, il nous serve à retrouver les PID des
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
# Plot les résultat
# @params:
#    - power_app: la consommation (puissance) de l'application 'baseline'
#    - noise: la consommation (puissance) du scénario de bruit
#    - host: la consommation (puissance) de la machine hote
#
def plotResult (power_app, power_host, noise) :
    plt.clf ()
    plt.plot (power_app, label="observed")
    plt.plot (noise, label="noise")
    plt.plot (power_host, label="host")

    plt.legend ()
    plt.savefig (f".output/timeline.png", dpi=400)

#
# Lis les résultats et génère les courbes de consommation et d'estimation
# @params:
#    - pids: la liste de PID de l'application baseline
#
def exportResults (pids):
    pathlib.Path(f".output/").mkdir(parents=True, exist_ok=True)

    power_host = []
    power_procs = []
    noise = []

    #
    # TODO: Les résultats fourni par scaphandre fournissent une liste de consommation (puissance)
    # 1. Remplir le tableau power_host avec la consommation observé sur l'hote par timestamp
    # 2. Remplir le tableau power_procs avec la consommation des processus dans "pids"
    # 3. Remplir le tableau noise avec la consommation des processus "stress" qui ne sont pas dans "pids"
    # 4. Générer les plots des courbes de consommation
    # 5. Afficher la consommation maximal de l'hote, et la consommation maximal du processus le plus consommateur
    #

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
# Démarre l'application 'baseline' que l'on va perturber via un scénario de bruit
# Cette application 'baseline' est un ensemble de stress sur n core pour un nombre donnée d'operations
# @params:
#    - functionName: le nom de la fonction a lancer
#    - nbCores: le nombre de core utilisé
#    - nbOps: le nombre d'operation à effectuer
#
# @returns:
#    - [0] : la liste de PID de l'application baseline
#    - [1] : les process (python) pour attendre la fin des stress
def startBaselineLoad (functionName, nbCores, duration):
    #
    # TODO: lancer les stress de l'application baseline et retourner leurs PIDs
    #

    return []

#
# Lance une experimentation (application 'baseline', puis lecture du scenario)
# @params:
#    - baselineFunction: le nom de la fonction a lancer dans l'application baseline
#    - nbCores: le nombre de core utilisé par l'app baseline
#    - duration: la duree de l'application baseline
#    - scenario: liste de dictionnaire décrivant un scénario (ex: [{'function_name' : 'sqrt', 'nb_cores' : 4, 'duration' : 10}])
#
def runExperiment (baselineFunction, nbCores, duration, scenario):
    #
    # TODO:
    # 1. Lancer scaphandre
    # 2. Lancer l'application 'baseline'
    # 3. Jouer le scenario
    #

    for l in scenario :
        print ("Next scenar", l)
        scenarioPR = []
        name = l ["function_name"]
        cores = l ["nb_cores"]
        dur = l ["duration"]
        # TODO: Lancer les stress de bruit, attendre la durée défini, et stopper les processus de bruit

    #
    # 4. Attendre la fin de l'application 'baseline
    # 5. Arreter l'xp et on export les résultat
    #


def main (arguments) :
    # Création d'un cgroup pour retrouver les PID de l'application 'baseline'
    subprocess.run(["cgcreate", "-g", "cpu:pg1"])

    with open (arguments.scenario, "r") as f:
        scenario = json.load (f) # Lecture du scenario
        runExperiment (arguments.func_name, arguments.nb_cores, arguments.duration, scenario)

if __name__ == "__main__" :
    main (parseArguments ())
