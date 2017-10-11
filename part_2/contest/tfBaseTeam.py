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
from tensorforce.agents import PPOAgent, DQNAgent
from tensorforce.core.networks import layered_network_builder
from tensorforce.core.networks import from_json

import reward
import features

import tfShared
import cPickle
import os
import numpy as np

TEAM_NAME = "tfTeam"
NUM_TO_ACTION = ["South", "North", "East", "West", "Stop"]

def newTfAgent():
    ##### ADAPTED FROM TENSORFORCE BLOGPOST
    # https://reinforce.io/blog/introduction-to-tensorforce/

    network = from_json("tfDense.json")

    # Define a state
    states = dict(shape=(6,), type='float')

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

def loadModelIfExists(agent, teamName=TEAM_NAME):
    if os.path.exists("{}/model.cpkt".format(teamName)):
        agent.model.saver.restore(agent.model.session, "{}}/model.cpkt".format(teamName))
    print("LOADED AGENT MODEL FROM FILE")

def saveModel(agent, teamName=TEAM_NAME):
    return agent.model.saver.save(agent.model.session,
                                  "{}/model.cpkt".format(teamName))

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

    def chooseAction(self, gameState):
        # give tfAgent the last observation
        if self.prevScore != None and self.mode != "Test":
            self.giveTfObservation(gameState, terminal=False)

        # choose the action using tfAgent        
        tfAction = self.chooseActionFromTfAgent(gameState)

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
        
        # avoid illegal moves
        action = tfAction if tfAction in gameState.getLegalActions() else "Stop"

        # record choosed action to global var
        tfShared.ACTION_NUMS.append(tfAction)

        # update current to prev
        self.prevScore = self.getScore(gameState)
        self.prevAction = action
        self.prevState = gameState
        self.prevIsIllegal = not tfAction in gameState.getLegalActions()

        return action

    def chooseActionFromTfAgent(self, gameState):
        tfState = self.makeTfState(gameState)
        actionNum = self.tfAgent.act(tfState)
        tfAction = NUM_TO_ACTION[actionNum]
        return tfAction

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
        return reward.getReward(self, gameState, self.prevState, terminal)

    def makeTfState(self, gameState):
        return features.getFeatures(self, gameState)


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
