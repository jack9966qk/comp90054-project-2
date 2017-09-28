import pickle
from subprocess import call
import os
import cPickle
import time
import textDisplay
from capture import CaptureRules

WEIGHT_FILENAME = "rlWeights.pickle"

def recoverFromReplay(replay):
    sequences = {}
    for agent in replay["agents"]:
        print(agent.index)
        sequences[agent.index] = []
    print(sequences)
    gameStates = []
    actions = []
    display = textDisplay.NullGraphics()
    rules = CaptureRules()
    game = rules.newGame(replay["layout"], replay["agents"], display, replay["length"], False, False)
    state = game.state
    for idx, action in replay["actions"]:
        sequences[idx].append((state, action))
        state = state.generateSuccessor(idx, action)
        rules.process(state, game)
    # TODO final state for each agent
    return sequences, replay["agents"]

def simulateGames(redTeam, blueTeam, numGames=1):
    dir = "replay/" + time.strftime("%b-%d-%H-%M-%S", time.localtime(time.time()))
    if not os.path.exists(dir):
        os.mkdir(dir)
    call(["python", "./capture.py",
          "-r", redTeam, "-b", blueTeam,
          "-q", "-n", str(numGames), "--record={}/replay".format(dir)])
    # call(["python", "./capture.py",
    #       "-r", "recorderTeam", "-b", "recorderTeam",
    #       "-q", "-n", str(numGames)])
    data = []
    for replayFilename in os.listdir(dir):
        if replayFilename.endswith("cpickle"):
            with open(dir + "/" + replayFilename) as f:
                replay = cPickle.load(f)
                data.append( recoverFromReplay(replay) )
    return data

data = simulateGames("baselineTeam", "baselineTeam", numGames=1)

# weight = ...
# redTeam = "baselineTeam"
# blueTeam = "baselineTeam"
# rawData = simulateGames(redTeam, blueTeam, numGames=1)

# labels = getLabels(rawData)
# features = extractFeatures(rawData)
# weight = train(features, labels)
# with open(WEIGHT_FILENAME, 'w') as f:
#     pickle.dump(weight, f)
