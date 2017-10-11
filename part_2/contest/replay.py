import os
import sys
import pickle
from subprocess import call
import os
import cPickle
import time
import textDisplay
from capture import CaptureRules

import features
import reward

def recoverFromReplay(replay):
    sequence = []
    gameStates = []
    actions = []
    display = textDisplay.NullGraphics()
    rules = CaptureRules()
    game = rules.newGame(replay["layout"], replay["agents"], display, replay["length"], False, False)
    state = game.state
    
    for idx, action in replay["actions"]:
        agent = replay["agents"][idx]
        observation = state.makeObservation(agent.index)
        sequence.append((observation, action, agent))
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

def replayDataGenerator(dir):
    for replayFilename in os.listdir(dir):
        if replayFilename.endswith("cpickle"):
            with open(dir + "/" + replayFilename) as f:
                replay = cPickle.load(f)
                yield recoverFromReplay(replay)

def addLabels(data, discount=0.95):
    for seq in data:
        episodes = addLabelsOneSeq(seq, discount=discount)
        for ep in episodes:
            for step in ep:
                yield step

def addLabelsOneSeq(seq, discount=0.95):
    episodes = []
    agents = { ag for _, _, ag, _, _ in seq }
    for agent in agents:
        ep = []
        agent_seq = [(s, a, ag, f, m) for s, a, ag, f, m in seq if ag.index == agent.index]
        vals = [0 for _ in agent_seq]
        terminal = True
        for i in list(range(len(agent_seq)-1))[::-1]:
            state, action, agent, features = agent_seq[i]
            nextState = agent_seq[i+1][0]
            r = reward.getReward(agent, nextState, state, terminal)
            qVal = r + discount * vals[i+1]
            vals[i] = qVal
            ep.append((state, action, agent, features, qVal))
            terminal = False
        episodes.append(ep[::-1])
    print(episodes)
    return episodes

def makeTrainingSet(instances):
    print "making training Set..."
    _, actions, _, features, mod, labels = zip(*instances)
    nfeatrues = [features[i].append(mod[i]) for i in range(len(features))]
    return features, actions, labels

def addFeatures(replayData):
    for seq in replayData: yield addFeaturesOneGame(seq)

def addFeaturesOneGame(sequence):
    states, actions, agents = zip(*sequence)
    # extract features
    features = extractFeatures(states, actions, agents)
    return zip(states, actions, agents, features)

def extractFeatures(states, actions, agents):
    return [ features.getFeatures(ag, s) for s, a, ag in zip(states, actions, agents)]