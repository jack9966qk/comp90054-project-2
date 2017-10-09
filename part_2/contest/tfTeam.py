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

from tensorforce import Configuration
from tensorforce.agents import PPOAgent, DQNAgent
from tensorforce.core.networks import layered_network_builder
from tensorforce.core.networks import from_json

import reward

import tfShared

from featuresTool import featuresTool
import cPickle
import os
import numpy as np

NUM_TO_ACTION = ["South", "North", "East", "West", "Stop"]

def newTfAgent():
    ##### ADAPTED FROM TENSORFORCE BLOGPOST
    # https://reinforce.io/blog/introduction-to-tensorforce/

    network = from_json("tensorforceNetwork.json")

    # Define a state
    states = dict(shape=(8,), type='float')

    # Define an action (models internally assert whether
    # they support continuous and/or discrete control)
    actions = dict(continuous=False, num_actions=5)

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
    if os.path.exists("tensorforceModel/model.cpkt"):
        agent.model.saver.restore(agent.model.session, "tensorforceModel/model.cpkt")
    # if os.path.exists("tensorforceModel/checkpoint"):
    #     agent.model.saver.restore(agent.model.session, "tensorforceModel/")
    print("LOADED AGENT MODEL FROM FILE")

def saveModel(agent):
    return agent.model.saver.save(agent.model.session,
                                  "tensorforceModel/model.cpkt")

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
    agent = TensorForceAgent(firstIndex)
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

class TensorForceAgent(CaptureAgent):
    """
    This Pacman Agent acts as a Runner for the Tensorforce agent
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

        # initialisation
        self.prevScore = None
        self.prevState = None
        self.prevAction = None
        self.prevIsIllegal = None
        self.featuresTool = featuresTool(dict={})
        self.featuresTool.initGame(self, gameState)

    def chooseAction(self, gameState):
        if self.prevScore != None and self.mode != "Test":
            self.giveTfObservation(gameState, terminal=False)
        
        actionNum = self.tfAgent.act(self.makeTfState(gameState))
        tfAction = NUM_TO_ACTION[actionNum]

        # debug draw agent intention
        x, y = gameState.getAgentPosition(self.index)
        self.debugClear()
        if tfAction == "North":
            self.debugDraw([(x, y+1)], [0, 0, 1])
        elif tfAction == "South":
            self.debugDraw([(x, y-1)], [0, 0, 1])
        elif tfAction == "West":
            self.debugDraw([(x-1, y)], [0, 0, 1])
        elif tfAction == "East":
            self.debugDraw([(x+1, y)], [0, 0, 1])
        
        action = tfAction if tfAction in gameState.getLegalActions() else "Stop"

        tfShared.ACTION_NUMS.append(actionNum)

        # update current to prev
        self.prevScore = self.getScore(gameState)
        self.prevAction = action
        self.prevState = gameState
        self.prevIsIllegal = not tfAction in gameState.getLegalActions()

        return action

    def final(self, gameState):
        if self.prevScore != None and self.mode != "Test":
            self.giveTfObservation(gameState, terminal=True)
        self.tfAgent.reset()
        tfShared.EPISODES.append(self.getScore(gameState))
        print("Append")
        print("len from team", len(tfShared.EPISODES))
        CaptureAgent.final(self, gameState)

    #####################################################
    def giveTfObservation(self, gameState, terminal):
        reward = self.getReward(gameState, terminal)
        print("GIVE TFAGENT OBSERVATION WITH REWARD {}".format(reward))
        self.tfAgent.observe(reward, terminal)

    def getReward(self, gameState, terminal):
        totalReward = reward.getReward(self, self.prevState, self.prevAction, gameState)
        prevFoodDist = self.featuresTool.getClostestFoodDist(self, self.prevState, "Stop", self.prevState)
        currFoodDist = self.featuresTool.getClostestFoodDist(self, gameState, "Stop", gameState)
        totalReward += currFoodDist - prevFoodDist

        prevInvaderDist = min(
            self.featuresTool.getInvader1Dist(self, self.prevState, "Stop", self.prevState),
            self.featuresTool.getInvader2Dist(self, self.prevState, "Stop", self.prevState)
        )
        currInvaderDist = min(
            self.featuresTool.getInvader1Dist(self, gameState, "Stop", gameState),
            self.featuresTool.getInvader2Dist(self, gameState, "Stop", gameState)
        )
        if prevInvaderDist < 10000:
            totalReward += currInvaderDist - prevInvaderDist

        print("currFoodDist = {}, prevFoodDist = {}, currInvaderDist = {}, prevInvaderDist = {}".format(
            currFoodDist, prevFoodDist, currInvaderDist, prevInvaderDist
        ))

        return totalReward
        # if terminal: return self.getScore(gameState) * 1000
        # else: return self.getScore(gameState) - self.prevScore

    # def makeTfState(self, gameState):
    #     observation = np.zeros((32, 16, 4))
    #     # self pos
    #     x, y = gameState.getAgentPosition(self.index)
    #     observation[x-1, y-1, 0] = 1
    #     # food pos
    #     food = self.getFood(gameState)
    #     for x in range(32):
    #         for y in range(16):
    #             if food[x][y]:
    #                 observation[x-1, y-1, 1] = 1
    #     # opponent pos
    #     for opponentIdx in self.getOpponents(gameState):
    #         pos = gameState.getAgentPosition(opponentIdx)
    #         if pos:
    #             observation[pos[0]-1, pos[1]-1, 2] = 1
    #     # wall pos
    #     wall = gameState.getWalls()
    #     for x in range(32):
    #         for y in range(16):
    #             if wall[x][y]:
    #                 observation[x-1, y-1, 3] = 1
    #     return observation

    def makeTfState(self, gameState):
        return [
            self.featuresTool.getClostestFoodDist(self, gameState, "Stop", gameState),
            self.featuresTool.getTeamFoodLeft(self, gameState, "Stop", gameState),
            self.featuresTool.getGhost1Dist(self, gameState, "Stop", gameState),
            self.featuresTool.getGhost2Dist(self, gameState, "Stop", gameState),
            self.featuresTool.getCarry(self, gameState, "Stop", gameState),
            self.featuresTool.getHomeDist(self, gameState, "Stop", gameState),
            self.featuresTool.getIsPacman(self, gameState, "Stop", gameState),
            self.featuresTool.getSumOfFoodDists(self, gameState, "Stop", gameState)
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
