import os
import subprocess

def plan(domainFile, problem):
    with open("tmp/problem.pddl", "w") as problemFile:
        problemFile.write(problem)
    subprocess.call('fast-downward/fast-downward.py {}'.format(domainFile) +
        'tmp/problem.pddl --search "astar(lmcut())"')
    if not os.path.exists("fast-downward/sas-plan"):
        return None
    else:
        with open("fast-downward/sas-plan") as planFile:
            return planFile.readline()