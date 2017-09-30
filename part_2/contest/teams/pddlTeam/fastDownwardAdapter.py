import os
import subprocess
import sys

teamName = os.path.split(os.path.dirname(os.path.abspath(__file__)))[1]
dir = "teams/{}/".format(teamName)
sys.path.append(dir)

def plan(domainFile, problem):
    if os.path.exists(dir + "sas_plan"):
        os.remove(dir + "sas_plan")
    if not os.path.exists(dir + "/tmp"):
        os.makedirs(dir + "tmp")
    with open(dir + "tmp/problem.pddl", "w") as problemFile:
        problemFile.write(problem)
    command = 'fast-downward/fast-downward.py {} {}tmp/problem.pddl --heuristic "hff=ff()" --search "lazy_greedy([hff])"'.format(domainFile, dir)
    print(command)
    subprocess.call(command, shell=True)
    if not os.path.exists("sas_plan"):
        return None
    else:
        with open("sas_plan") as planFile:
            return [line for line in planFile.readlines() if not line.startswith(";")]