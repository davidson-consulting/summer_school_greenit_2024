import time
import os
import subprocess
import pathlib
import shutil
import json
import argparse
import matplotlib.pyplot as plt

def parseArguments ():
    parser = argparse.ArgumentParser ()
    parser.add_argument ("--func_name", default="sqrt")
    parser.add_argument ("--nb_ops", type=int, default=30000)
    parser.add_argument ("--estimate_dur", type=int, default=20)
    parser.add_argument ("--min_cpu", default=1)
    parser.add_argument ("--max_cpu", default=os.cpu_count ())

    return parser.parse_args ()

def get_pids_in_cgroup(cgroup):
    with open(f"{cgroup}/cgroup.procs", "r") as f:
        return f.read().split("\n")[:-1]


def jsonSplitLoad () :
    with open("/tmp/results.json", "r") as f:
        return json.load (f)

def plotResult (pids, power, power_host, nbCores) :
    plt.clf ()
    for p in pids :
        plt.plot ([power [i][str (p)] for i in range (len (power))], label=str (p))
    plt.plot (power_host, label="host")

    plt.legend ()
    plt.savefig (f".output/{nbCores}.png", dpi=400)

def exportResults (pids, nbCores):
    pathlib.Path(f".output/").mkdir(parents=True, exist_ok=True)

    power_host = []
    power = []

    for result in jsonSplitLoad () :
        power.append ({str (pid) : 0 for pid in pids})
        power_host.append (result["host"]["consumption"])
        for consumer in result["consumers"]:
            if str(consumer["pid"]) in pids:
                power [-1][str (consumer ["pid"])] += consumer["consumption"]

    with open(f".output/{nbCores}", "w+") as f:
        f.write(str(power))

    sums = [sum ([power [i][p] for i in range(len (power))]) for p in pids]
    maxes = [max ([power [i][p] for i in range(len (power))]) for p in pids]

    with open(f".output/{nbCores}_host", "w+") as f:
        f.write(str(power_host))

    plotResult (pids, power, power_host, nbCores)

    return (max (power_host), max (maxes), sum (power_host), max (sums))

def startScaphandre (nbCores, estimateDur):
    if os.path.isfile("/tmp/results.json"):
        os.remove("/tmp/results.json")
    pid = subprocess.Popen (["scaphandre", "json", "--max-top-consumers", "50", "-t", str (estimateDur), "-s", "0", "-n", "100000000",  "-f", "/tmp/results.json"])

    return pid

def stopScaphandre (scaph, pids, nbCores) :
    scaph.wait ()
    return exportResults (pids, nbCores)


def runExperiment (functionName, nbCores, nbOps, estimateDur):
    processes = []
    scaph = startScaphandre (nbCores, estimateDur)
    time.sleep (1)

    for _ in range (nbCores) :
        processes.append (subprocess.Popen (["cgexec", "-g", "cpu:/pg1", "stress-ng", "-c", "1", "--cpu-method", functionName, "--cpu-ops", str (nbOps)]))

    time.sleep (1)
    pids = get_pids_in_cgroup ("/sys/fs/cgroup/pg1")

    for process in processes :
        process.wait ()

    time.sleep (1)
    return stopScaphandre (scaph, pids, nbCores)


def main (arguments) :
    subprocess.run(["cgcreate", "-g", "cpu:pg1"])

    hostP = []
    processP = []
    hostE = []
    processE = []

    for nbCores in range (arguments.min_cpu, arguments.max_cpu + 1) :
        (host_power, process_power, host_energy, process_energy) = runExperiment (arguments.func_name, nbCores, arguments.nb_ops, arguments.estimate_dur)
        hostP.append (host_power)
        processP.append (process_power)

        hostE.append (host_energy)
        processE.append (process_energy)

    plt.clf ()
    plt.plot (hostP, label="host")
    plt.plot (processP, label="process")
    plt.legend ()
    plt.savefig (".output/power_curve.png", dpi=400)

    plt.clf ()
    plt.plot (hostE, label="host")
    plt.plot (processE, label="process")
    plt.legend ()
    plt.savefig (".output/energy_curve.png", dpi=400)

if __name__ == "__main__" :
    main (parseArguments ())
