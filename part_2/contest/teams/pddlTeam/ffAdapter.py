import os
import subprocess
import sys

teamName = os.path.split(os.path.dirname(os.path.abspath(__file__)))[1]
dir = "teams/{}/".format(teamName)

def plan(domainFile, problem):
    if not os.path.exists(dir + "tmp"):
        os.makedirs(dir + "tmp")
    if os.path.exists(dir + "tmp/output"):
        os.remove(dir + "tmp/output")
    with open(dir + "tmp/problem.pddl", "w") as problemFile:
        problemFile.write(problem)
    command = './ff --domain {} --problem {}tmp/problem.pddl --output {}tmp/output'.format(domainFile, dir, dir)
    subprocess.call(command, shell=True)
    if not os.path.exists(dir + "tmp/output"):
        return None
    else:
        with open(dir + "tmp/output") as planFile:
            return [line for line in planFile.readlines() if not line.startswith(";")]