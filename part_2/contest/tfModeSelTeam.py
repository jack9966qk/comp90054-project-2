# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import os, sys
from captureAgents import CaptureAgent
import random
import time
import util
from game import Directions
import game

from baselineTeam import OffensiveReflexAgent, DefensiveReflexAgent

from tensorforce import Configuration
from tensorforce.agents import DQFDAgent, DQNAgent
from tensorforce.core.networks import layered_network_builder
from tensorforce.core.networks import from_json

import tfBaseTeam
import tfShared

import features
import reward

TEAM_NAME = "tfModeSelTeam"
NUM_TO_MODE = ["backhome", "defense", "offense"]
MODES_TO_NUM = {"backhome": 0, "defense": 1, "defense1": 1, "defense2": 1, "offense": 2}

def newTfAgent():
    network = layered_network_builder([
        dict(type='dense', size=32),
        dict(type='dense', size=32)
    ])

    # Define a state
    states = dict(shape=(6,), type='float')

    # Define an action (models internally assert whether
    # they support continuous and/or discrete control)
    actions = dict(continuous=False, num_actions=3)

    # The agent is configured with a single configuration object
    agent_config = Configuration(
        batch_size=100,
        learning_rate=0.005,
        memory_capacity=2000,
        first_update=20,
        repeat_update=4,
        target_update_frequency=20,
        states=states,
        actions=actions,
        network=network,
    )
    agent = DQNAgent(config=agent_config)
    return agent

def loadModelIfExists(agent):
    tfBaseTeam.loadModelIfExists(agent, teamName=TEAM_NAME)

def saveModel(agent):
    tfBaseTeam.saveModel(agent, teamName=TEAM_NAME)    

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               useShared="False", mode="Test"):
    """
    This function should return a list of two agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.  isRed is True if the red team is being created, and
    will be False if the blue team is being created.

    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments ("first" and "second" are
    such arguments in the case of this function), which will come from
    the --redOpts and --blueOpts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """

    # The following line is an example only; feel free to change it.
    firstAgent = TensorForceModeSelAgent(firstIndex)
    secondAgent = TensorForceModeSelAgent(secondIndex)
    agents = [firstAgent, secondAgent]
    random.shuffle(agents)
    agent, teammate = agents

    if useShared == "True":
        print("USE GLOBAL AGENT")
        agent.tfAgent = tfShared.TF_AGENT
    else:
        agent.tfAgent = newTfAgent()
        loadModelIfExists(agent.tfAgent)

    agent.mode = mode
    if mode == "Test":
        print("SET MODE TO TEST")
    else:
        print("SET MODE TO TRAIN")

    teammate.tfAgent = newTfAgent()
    loadModelIfExists(teammate.tfAgent)
    teammate.mode = "Test"
    
    return [firstAgent, secondAgent]

##########
# Agents #
##########

class TensorForceModeSelAgent(tfBaseTeam.TensorForceAgent):
    """
    This Pacman Agent acts as a Runner for the Tensorforce agent
    """
    def chooseActionFromTfAgent(self, gameState):
        tfState = self.makeTfState(gameState)
        modeNum = self.tfAgent.act(tfState)
        mode = NUM_TO_MODE[modeNum]
        tfShared.ACTION_NUMS.append(mode)
        print("chose mode {}".format(mode))

        def evaluate(gameState, action, mode):
            nextState = gameState.generateSuccessor(self.index, action)
            v = 0
            if mode == "offense":
                v += -10000 * features.getFoodLeft(self, nextState)
                v += -100 * features.getClosestFoodDist(self, nextState)
            elif mode == "defense":
                v += -10000 * features.getHomeDist(self, nextState)
                v += -100 * features.getClosestInvaderDist(self, nextState)
            elif mode == "backhome":
                v += 100 * features.getTotalGhostDist(self, nextState)
                v += -100 * features.getHomeDist(self, nextState)
            return v

        actions = gameState.getLegalActions(self.index)
        values = [evaluate(gameState, a, mode) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        if "Stop" in bestActions: return "Stop"
        action = random.choice(bestActions)
        return action

    #####################################################
    def getReward(self, gameState, terminal):
        return reward.getReward(self, gameState, self.prevState, terminal)

    def makeTfState(self, gameState):
        return features.getFeatures(self, gameState)