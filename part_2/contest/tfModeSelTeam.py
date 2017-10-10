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


from captureAgents import CaptureAgent
import random
import time
import util
from game import Directions
import game

from baselineTeam import OffensiveReflexAgent, DefensiveReflexAgent

import tfTeam
from tensorforce import Configuration
from tensorforce.agents import PPOAgent, DQNAgent
from tensorforce.core.networks import layered_network_builder
from tensorforce.core.networks import from_json

import reward

import tfShared

import os, sys
# teamName = os.path.split(os.path.dirname(os.path.abspath(__file__)))[1]
# dir = "teams/{}/".format(teamName)
dir = "teams/modeSwitchTeam/"
sys.path.append(dir)

from featuresTool import featuresTool
import numpy as np
import json

TEAM_NAME = "tfModeSelTeam"
NUM_TO_MODE = ["backhome", "defense1", "defense2", "offense"]

def newTfAgent():
    ##### ADAPTED FROM TENSORFORCE BLOGPOST
    # https://reinforce.io/blog/introduction-to-tensorforce/

    network = from_json("tfDense.json")

    # Define a state
    states = dict(shape=(10,), type='float')

    # Define an action (models internally assert whether
    # they support continuous and/or discrete control)
    actions = dict(continuous=False, num_actions=4)

    # The agent is configured with a single configuration object
    agent_config = Configuration(
        batch_size=8,
        learning_rate=0.001,
        memory_capacity=800,
        first_update=80,
        repeat_update=4,
        target_update_frequency=20,
        states=states,
        actions=actions,
        network=network
    )
    agent = DQNAgent(config=agent_config)
    return agent

def loadModelIfExists(agent):
    if os.path.exists("tensorforceModeSelModel/model.cpkt"):
        agent.model.saver.restore(agent.model.session, "tensorforceModeSelModel/model.cpkt")
    print("LOADED AGENT MODEL FROM FILE")

def saveModel(agent):
    return agent.model.saver.save(agent.model.session,
                                  "tensorforceModeSelModel/model.cpkt")

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
    agent = TensorForceModeSelAgent(firstIndex)
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
    return [agent, DummyAgent(secondIndex)]

##########
# Agents #
##########

class TensorForceModeSelAgent(tfTeam.TensorForceAgent):
    """
    This Pacman Agent acts as a Runner for the Tensorforce agent
    """
    def registerInitialState(self, gameState):
        tfTeam.TensorForceAgent.registerInitialState(self, gameState)
        with open(dir + "WeightsDict.json", "r") as f:
            self.weightsDict = json.load(f)

    def chooseActionFromTfAgent(self, gameState):
        tfState = self.makeTfState(gameState)
        modeNum = self.tfAgent.act(tfState)
        mode = NUM_TO_MODE[modeNum]
        tfShared.ACTION_NUMS.append(mode)

        print("chose mode {}".format(mode))

        def evaluate(gameState,action):
            features = self.featuresTool.getFeatures(self,gameState,action)
            weights = self.weightsDict[mode]
            return features * weights

        actions = gameState.getLegalActions(self.index)
        actions.remove("Stop")
        values = [evaluate(gameState, a) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        action = random.choice(bestActions)
        return action

    #####################################################
    def getReward(self, gameState, terminal):
        if terminal:
            if self.getScore(gameState) == 0:
                return -1000
            else: return self.getScore(gameState) * 1000
        else:
            r = (self.getScore(gameState) - self.prevScore) * 50
            x, y = gameState.getAgentPosition(self.index)
            if self.getFood(self.getPreviousObservation())[x][y]:
                # ate food
                r += 5
            if self.prevIsIllegal:
                # had invalid action in last step
                r -= 5
            prevX, prevY = self.getPreviousObservation().getAgentPosition(self.index)
            if (abs(prevX - x) + (prevY - y)) > 1:
                # ate by opponent
                r -= 10
            r -= 1 # time
            print("reward: {}".format(r))
            return r

    def makeTfState(self, gameState):
        return [
            self.featuresTool.getClostestFoodDist(self, gameState, "Stop", gameState),
            self.featuresTool.getTeamFoodLeft(self, gameState, "Stop", gameState),
            self.featuresTool.getGhost1Dist(self, gameState, "Stop", gameState),
            self.featuresTool.getGhost2Dist(self, gameState, "Stop", gameState),
            self.featuresTool.getCarry(self, gameState, "Stop", gameState),
            self.featuresTool.getHomeDist(self, gameState, "Stop", gameState),
            self.featuresTool.getIsPacman(self, gameState, "Stop", gameState),
            self.featuresTool.getSumOfFoodDists(self, gameState, "Stop", gameState),
            self.featuresTool.getHasInvader1(self, gameState, "Stop", gameState),
            self.featuresTool.getHasInvader2(self, gameState, "Stop", gameState)
        ]


class DummyAgent(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at baselineTeam.py for more details about how to
    create an agent as this is the bare minimum.
    """

    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the
        agent to populate useful fields (such as what team
        we're on).

        A distanceCalculator instance caches the maze distances
        between each pair of positions, so your agents can use:
        self.distancer.getDistance(p1, p2)

        IMPORTANT: This method may run for at most 15 seconds.
        """

        '''
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.registerInitialState in captureAgents.py.
        '''
        CaptureAgent.registerInitialState(self, gameState)

        '''
        Your initialization code goes here, if you need any.
        '''

    def chooseAction(self, gameState):
        """
        Picks among actions randomly.
        """
        actions = gameState.getLegalActions(self.index)

        '''
    You should change this in your own agent.
    '''

        return random.choice(actions)
