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

# Nombre d'operation à effectuer Ce nombre d'operation permet de garantir que la
# fonction de stress effectue toujours le même travail, même lancé en parallèle
# avec d'autre charges
NB_OPS = 30000

#
# Parse le argument de ligne de commande
# @returns: les arguments
#
def parseArguments ():
    parser = argparse.ArgumentParser ()
    parser.add_argument ("--func_name", default=DEFAULT_FUNC)
    parser.add_argument ("--nb_ops", type=int, default=NB_OPS)
    parser.add_argument ("--min_cpu", default=1, type=int)
    parser.add_argument ("--max_cpu", default=os.cpu_count (), type=int)

    return parser.parse_args ()

#
# Les stress sont lancés dans un cgroup (via cgexec) Les cgroups servent à
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
#    - [2] : la consmmation d'énergie observé sur l'hote
#    - [3] : la consmmation d'energie du stress le plus consommateur
#
def exportResults (pids, imageName):
    pathlib.Path(f".output/").mkdir(parents=True, exist_ok=True)

    power_host = []
    power_procs = []

    for result in loadScaphandreResults () :
        power_procs.append ({str (pid) : 0 for pid in pids})

        # scaphandre retourne les résultat en micro watts
        power_host.append (result["host"]["consumption"] / 1000000)
        for consumer in result["consumers"]:
            if str(consumer["pid"]) in pids:
                power_procs [-1][str (consumer ["pid"])] += (consumer["consumption"] / 1000000)

    plotResult (pids, power_procs, power_host, imageName)

    # 1 joule c'est 1W pendant 1 seconde, donc on doit diviser par la fréquence pour correctement integrer la courbe
    energy_procs = [sum ([power_procs [i][p] for i in range(len (power_procs))])  for p in pids]
    power_max_procs = [max ([power_procs [i][p] for i in range(len (power_procs))])  for p in pids]
    energy_host = sum (power_host)

    return (max (power_host), max (power_max_procs), energy_host, max (energy_procs))


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
# Arrête scaphandre, et export les résultats
# @params:
#    - scaph: le process de scaphandre (cf. startScaphandre)
#    - pids: la liste de PIDS observés
#    - imageName: le nom de l'image dans laquel faire l'export
#
# @returns:
#    - [0] : la consommation (puissance) maximal observé sur l'hote
#    - [1] : la consommation (puissance) maximal du stress le plus consommateur
#    - [2] : la consmmation d'énergie observé sur l'hote
#    - [3] : la consmmation d'energie du stress le plus consommateur
#
def stopScaphandre (scaph, pids, imageName) :
    scaph.kill ()
    return exportResults (pids, imageName)

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
#    - [2] : la consmmation d'énergie observé sur l'hote
#    - [3] : la consmmation d'energie du stress le plus consommateur
#
def runExperiment (functionName, nbCores, nbOps):
    processes = []
    scaph = startScaphandre ()
    time.sleep (1)

    for _ in range (nbCores) :
        processes.append (subprocess.Popen (["cgexec", "-g", "cpu:/pg1", "stress-ng", "-c", "1", "--cpu-method", functionName, "--cpu-ops", str (nbOps)]))

    time.sleep (1)
    pids = get_pids_in_cgroup ("pg1")

    for process in processes :
        process.wait ()

    time.sleep (1)
    return stopScaphandre (scaph, pids, str (nbCores))


def main (arguments) :
    # Creation du cgroup, pour pouvoir lister les PIDS que l'on va lancer
    subprocess.run(["cgcreate", "-g", "cpu:pg1"])

    hostP = []
    processP = []
    hostE = []
    processE = []

    # En faisant monter la charge de 1 à n cores
    for nbCores in range (arguments.min_cpu, arguments.max_cpu + 1) :
        (host_power, process_power, host_energy, process_energy) = runExperiment (arguments.func_name, nbCores, arguments.nb_ops)
        hostP.append (host_power)
        processP.append (process_power)

        hostE.append (host_energy)
        processE.append (process_energy)

    print ("Host power : ", hostP)
    print ("Process power : ", processP)
    print ("Host energy : ", hostE)
    print ("Process energy : ", processE)

    # On plot la courbe de consommation (puissance) en fonction du nombre de cores
    plt.clf ()
    plt.plot (hostP, label="host")
    plt.plot (processP, label="process")
    plt.legend ()
    plt.savefig (".output/power_curve.png", dpi=400)

    # On plot la courbe de consommation (energie) en fonction du nombre de cores
    plt.clf ()
    plt.plot (hostE, label="host")
    plt.plot (processE, label="process")
    plt.legend ()
    plt.savefig (".output/energy_curve.png", dpi=400)



# Python...
if __name__ == "__main__" :
    main (parseArguments ())
