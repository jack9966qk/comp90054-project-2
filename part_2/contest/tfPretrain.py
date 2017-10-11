from recorder import loadRecord
import imp
import os
import sys

from capture import GameState

dir = "teams/modeSwitchTeam/"
sys.path.append(dir)

from myTeam import DummyAgent

imp.load_source("player0", "teams/modeSwitchTeam/myTeam.py")
imp.load_source("player1", "teams/modeSwitchTeam/myTeam.py")

import features

from tfDqfdModeSelTeam import MODES_TO_NUM, newTfAgent, saveModel

print("preparing demonstrations...")

demonstrations = []

dir = "episodes/"
for fileName in os.listdir(dir):
    if fileName.endswith("cpickle"):
        print("loading {}...".format(fileName))
        record = loadRecord("episodes/{}".format(fileName))
        for r in record:
            demo = dict(state=features.getFeatures(r["agent"], r["currentState"]),
                action=MODES_TO_NUM[r["extra"]["mode"]],
                reward=r["reward"],
                terminal=r["terminal"],
                internal=[])
            demonstrations.append(demo)

print("importing demonstrations...")
agent = newTfAgent()
agent.import_demonstrations(demonstrations)

nSteps = 1000
print("start pretrain with {} steps".format(nSteps))
agent.pretrain(steps=nSteps)

saveModel(agent)