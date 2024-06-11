
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

    for result in loadScaphandreResults () :
        power_procs.append (0)
        noise.append (0)

        # scaphandre retourne les résultats en micro watts
        power_host.append (result["host"]["consumption"] / 1000000)

        for consumer in result["consumers"]:
            if str(consumer["pid"]) in pids:
                power_procs [-1] += (consumer ["consumption"] / 1000000)
            elif ("stress" in str (consumer ["exe"])):
                noise [-1] += (consumer ["consumption"] / 1000000)

    plotResult (power_procs, power_host, noise)

    print ("Power conso max host : ", max (power_host), "W")
    print ("Power conso max procs : ", max (power_procs), "W")

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
    processes = []
    for _ in range (nbCores) :
        processes.append (subprocess.Popen (["cgexec", "-g", "cpu:/pg1", "stress-ng", "-c", "1", "--cpu-method", functionName, "-t", str (duration)]))

    time.sleep (1)
    pids = get_pids_in_cgroup ("pg1")
    print (pids)
    return (pids, processes)


#
# Lance une experimentation (application 'baseline', puis lecture du scenario)
# @params:
#    - baselineFunction: le nom de la fonction a lancer dans l'application baseline
#    - nbCores: le nombre de core utilisé par l'app baseline
#    - duration: la duree de l'application baseline
#    - scenario: liste de dictionnaire décrivant un scénario (ex: [{'function_name' : 'sqrt', 'nb_cores' : 4, 'duration' : 10}])
#
def runExperiment (baselineFunction, nbCores, duration, scenario):
    processes = []
    scaph = startScaphandre ()
    time.sleep (1)

    (pids, processes) = startBaselineLoad (baselineFunction, nbCores, duration)

    for l in scenario :
        print ("Next scenar", l)
        scenarioPR = []
        name = l ["function_name"]
        cores = l ["nb_cores"]
        dur = l ["duration"]
        # Lance les stress de bruit
        for _ in range (cores) :
            scenarioPR.append (subprocess.Popen (["stress-ng", "-c", "1", "--cpu-method", str (name), "-t", str (dur)]))

        time.sleep (dur)
        # arrete les stress de bruit après 'dur' secondes
        for p in scenarioPR :
            p.kill ()

    # On attend la fin de l'application nominal
    for p in processes :
        p.wait ()

    time.sleep (2)

    # On arrete l'xp et on export les résultat
    scaph.kill ()
    exportResults (pids)

def main (arguments) :
    # Création d'un cgroup pour retrouver les PID de l'application 'baseline'
    subprocess.run(["cgcreate", "-g", "cpu:pg1"])

    with open (arguments.scenario, "r") as f:
        scenario = json.load (f) # Lecture du scenario
        runExperiment (arguments.func_name, arguments.nb_cores, arguments.duration, scenario)

if __name__ == "__main__" :
    main (parseArguments ())
