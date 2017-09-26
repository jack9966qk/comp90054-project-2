import os
import subprocess

def plan(domainFile, problem):
    if os.path.exists("sas_plan"):
        os.remove("sas_plan")
    if not os.path.exists("tmp"):
        os.makedirs("tmp")
    with open("tmp/problem.pddl", "w") as problemFile:
        problemFile.write(problem)
    command = 'fast-downward/fast-downward.py {} tmp/problem.pddl --heuristic "hff=ff()" --search "lazy_greedy([hff])"'.format(domainFile)
    print(command)
    subprocess.call(command, shell=True)
    if not os.path.exists("sas_plan"):
        return None
    else:
        with open("sas_plan") as planFile:
            return planFile.readline().strip()