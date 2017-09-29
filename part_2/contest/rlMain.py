import pickle
from subprocess import call
import os
import cPickle
import time
import textDisplay
import reward
from capture import CaptureRules
from rlTrain import extractFeatures, train
import imp
from multiprocessing import Pool
from functools import partial



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
    # final state for each agent
    winner = None
    if state.data.score < 0: winner = "Blue"
    if state.data.score > 0: winner = "Red"
    redIndices = state.getRedTeamIndices()
    blueIndices = state.getBlueTeamIndices()
    def outcome(isRed, winner):
        if not winner: return "Tie"
        if isRed:
            return "Win" if winner == "Red" else "Lose"
        else:
            return "Win" if winner == "Blue" else "Lose"
    for i in redIndices: sequences[i].append(outcome(True, winner))
    for i in blueIndices: sequences[i].append(outcome(False, winner))
    return sequences, replay["agents"]

# single threaded game simulation, writes replay file to directory
def runGames(redTeam, blueTeam, dir, numGames, prefix):
    call(["python", "./capture.py",
          "-r", redTeam, "-b", blueTeam,
          "-q", "-n", str(numGames), "--record={}/{}replay".format(dir, prefix)])
    print("{} finished".format(prefix))

def simulateGames(redTeam, blueTeam, numRuns=1, numGamesPerRun=1, numProcesses=20):
    
    dir = "replay/" + time.strftime("%b-%d-%H-%M-%S", time.localtime(time.time()))
    if not os.path.exists(dir):
        os.mkdir(dir)
    
    pool = Pool(processes=numProcesses)
    runFunc = partial(runGames, redTeam, blueTeam, dir, numGamesPerRun)

    argsIter = [ "run{:2d}_".format(i) for i in range(numRuns) ]
    for args in argsIter: print(args)
    for i in pool.imap_unordered(runFunc, argsIter):
        print(i)
    # pool.join()
    print("all runs finished")

    # all games finished, load data from replay file
    data = []
    for replayFilename in os.listdir(dir):
        if replayFilename.endswith("cpickle"):
            with open(dir + "/" + replayFilename) as f:
                replay = cPickle.load(f)
                data.append( recoverFromReplay(replay) )
    return data

def addLabels(data, discount=0.9):
    instances = []
    for game in data:
        seqs, agents = game
        for agent in agents:
            idx = agent.index
            seq = seqs[idx]
            vals = [0 for _ in seq]
            for i in range(len(seq)-2, -1, -1):
                state, action = seq[i]
                nextState = seq[i+1] if seq[i+1] in ["Tie", "Win", "Lose"] else seq[i+1][0]
                r = reward.getReward(agent, state, action, nextState)
                qVal = r + discount * vals[i+1]
                vals[i] = qVal
                instances.append((state, action, nextState, agent, qVal))
    return instances

def makeTrainingSet(instances):
    features = [extractFeatures(s, a, ns, ag) for s, a, ns, ag, _ in instances]
    actions = [act for _, act, _, _, _ in instances]
    labels = [qVal for _, _, _, _, qVal in instances]
    return features, actions, labels


imp.load_source("player0", "baselineTeam.py")
imp.load_source("player1", "baselineTeam.py")

data = simulateGames("baselineTeam", "baselineTeam", numGamesPerRun=20, numRuns=20)
instances = addLabels(data)
features, actions, labels = makeTrainingSet(instances)
weight = train(features, actions, labels)

# # save weight
# with open(WEIGHT_FILENAME, 'w') as f:
#     pickle.dump(weight, f)
