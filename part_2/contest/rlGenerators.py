import cPickle

from rlMain import recoverFromReplay
from rlTrain import extractFeatures

import os, sys

dir = "teams/modSelection/"
sys.path.append(dir)
import reward

def replayDataGenerator(dir):
    for replayFilename in os.listdir(dir):
        if replayFilename.endswith("cpickle"):
            with open(dir + "/" + replayFilename) as f:
                replay = cPickle.load(f)
                yield recoverFromReplay(replay)

def addFeatures(replayData):
    for seq in replayData: yield addFeaturesOneGame(seq)

def addFeaturesOneGame(sequence):
    states, actions, agents = zip(*sequence)
    features, mods = extractFeatures(states, actions, agents)
    return zip(states, actions, agents, features, mods)

def addLabels(data, discount=0.95):
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
                yield (state, action, agent, features, mod, qVal)
