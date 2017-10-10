from tfModeSelTeam import loadModelIfExists, saveModel, newTfAgent, TEAM_NAME
import tfShared
from capture import readCommand, runGames
import os

from collections import defaultdict
import numpy as np

import csv

# initialise shared variables
tfShared.TF_AGENT = newTfAgent()
loadModelIfExists(tfShared.TF_AGENT)
tfShared.EPISODES = []
tfShared.ACTION_NUMS = []

# path = saveModel(tfShared.TF_AGENT)
# loadModelIfExists(tfShared.TF_AGENT)
# tfShared.TF_AGENT.load_model("tensorforceModel/")

# exit()

logFile = open("{}_log.csv".format(TEAM_NAME, "w")
logWriter = csv.writer(logFile)
logWriter.writerow(["finishedGames", "avg score last 100", "wins of last 100", "loses of last 100", "actionFreq"])

# main loop
for i in xrange(50):
    # run games
    cmdString = "-r tfCnnTeam -b {} -Q -l layouts/tinyCaptureSuperEasy.lay --redOpts=useShared=True,mode=Train -n 100".format(TEAM_NAME).split()
    options = readCommand(cmdString)
    runGames(**options)

    # after each 100 runs, save checkpoint and visualise one game
    saveModel(tfShared.TF_AGENT)
    last100 = tfShared.EPISODES[-100:]
    gamesLost = len([1 for s in last100 if s < 0])
    gamesWon = len([1 for s in last100 if s > 0])
    print("Lost {} of last 100 games".format(gamesLost))

    actionNumFreq = defaultdict(int)
    for n in tfShared.ACTION_NUMS:
        actionNumFreq[n] += 1
    print("Action frequency: {}".format(actionNumFreq))

    print("len from multigame", len(tfShared.EPISODES))
    # cmdString = "-r tfCnnTeam -l layouts/tinyCapture.lay --redOpts=useShared=True,mode=Train".split()
    # options = readCommand(cmdString)
    # runGames(**options)
    logWriter.writerow([str((i+1) * 100), str(np.mean(last100)), str(gamesWon), str(gamesLost), str(actionNumFreq)])
    logFile.flush()

    print("finished {} games".format((i+1)*100))

logFile.close()
# save final model
saveModel(tfShared.TF_AGENT)
