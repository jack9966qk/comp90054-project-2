dir = "teams/"
t1 = "baselineTeam"
t2 = "modSelection"
dirt1 = dir+t1+'/'
dirt2 = dir+t2+'/'

import os
import sys
teamName = t2
dir = "teams/{}/".format(teamName)
sys.path.append(dir)


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
import IOutil
#from Team1 import Team1

WEIGHT_FILENAME = "rlWeights.json"

def recoverFromReplay(replay):
    sequence = []
    gameStates = []
    actions = []
    display = textDisplay.NullGraphics()
    rules = CaptureRules()
    game = rules.newGame(replay["layout"], replay["agents"], display, replay["length"], False, False)
    state = game.state
    # print("AGENT POSITION")
    # print(state.getAgentPosition(0))
    # print(state.getAgentPosition(1))
    # print(state.getAgentPosition(2))
    # print(state.getAgentPosition(3))
    
    for idx, action in replay["actions"]:
        agent = replay["agents"][idx]

        observation = state.makeObservation(agent.index)
        # print(idx)
        # print("AGENT POSITION")
        sequence.append((observation, action, agent))
        # print(observation.getAgentPosition(0))
        # print(observation.getAgentPosition(1))
        # print(observation.getAgentPosition(2))
        # print(observation.getAgentPosition(3))
        # print("AGENT DISTANCES")
        # print(observation.getAgentDistances())
        # state = state.makeObservation(agent.index)
        

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
    
    for a in replay["agents"]:
        sequence.append((outcome(a.index in redIndices, winner), None, a))
    return sequence

# single threaded game simulation, writes replay file to directory
def runGames(redTeam, blueTeam, dir, numGames, prefix):
    call(["python", "./capture.py",
          "-r", redTeam, "-b", blueTeam, "-l", "RANDOM",
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
    return dir

def loadReplayFiles(dir):
    data = []
    for replayFilename in os.listdir(dir):
        if replayFilename.endswith("cpickle"):
            with open(dir + "/" + replayFilename) as f:
                replay = cPickle.load(f)
                data.append( recoverFromReplay(replay) )
    return data

def addLabels(data, discount=0.95):
    print "adding labels..."
    instances = []
    for seq in data:
        agents = { ag for _, _, ag, _, _ in seq }
        for agent in agents:
            agent_seq = [(s, a, ag, f, m) for s, a, ag, f, m in seq if ag.index == agent.index]
            vals = [0 for _ in agent_seq]
            for i in list(range(len(agent_seq)-1))[::-1]:
                state, action, agent, features, mod = agent_seq[i]
                nextState = agent_seq[i+1][0]
                r = reward.getReward(agent, state, action, nextState)
                qVal = r + discount * vals[i+1]
                #qVal = mod
                vals[i] = qVal
                instances.append((state, action, agent, features, mod, qVal))
    return instances

def makeTrainingSet(instances):
    print "making training Set..."
    _, actions, _, features, mod, labels = zip(*instances)
    nfeatrues = [features[i].append(mod[i]) for i in range(len(features))]
    return features, actions, labels

def addFeatures(replayData):
    print "adding featrues..."
    return [addFeaturesOneGame(seq) for seq in replayData]

def addFeaturesOneGame(sequence):
    states, actions, agents = zip(*sequence)
    features, mods = extractFeatures(states, actions, agents)
    return zip(states, actions, agents, features, mods)

if __name__ == "__main__":
    imp.load_source("player0", dirt1+"myTeam.py")
    imp.load_source("player1", dirt2+"myTeam.py")
    
    #dir = simulateGames(dirt2+"myTeam", dirt1+"myTeam", numGamesPerRun=1, numRuns=10)
    # all games finished, load data from replay files
    #dir = "replay/Oct-03-14-00-15" #100
    dir = "replay/Oct-04-18-12-14" #10
    #dir = "replay/Oct-04-18-08-42" #1
    replayData = loadReplayFiles(dir)
    replayDataWithFeat = addFeatures(replayData)
    instances = addLabels(replayDataWithFeat)
    features, actions, labels = makeTrainingSet(instances)
    
    IOutil.saveFile("tfeatures.json",features)
    IOutil.saveFile("tactions.json",actions)
    IOutil.saveFile("tlabels.json",labels)
    
    #features = IOutil.loadFile("tfeatures.json")
    #actions = IOutil.loadFile("tactions.json")
    #labels = IOutil.loadFile("tlabels.json") 
    #weight = train(features, actions, labels)
    weight = train(features, actions, labels,model ="MLP")

# # save weight
  #  IOutil.saveFile(WEIGHT_FILENAME,weight)
   # with open(WEIGHT_FILENAME, 'w') as f:
   #     pickle.dump(weight, f)
