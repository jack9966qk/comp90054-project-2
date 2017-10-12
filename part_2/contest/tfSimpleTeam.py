import os, sys
from captureAgents import CaptureAgent
import random
import time
import util
from game import Directions
import game

from baselineTeam import OffensiveReflexAgent, DefensiveReflexAgent

from tensorforce import Configuration
from tensorforce.agents import TRPOAgent
from tensorforce.core.networks import layered_network_builder
from tensorforce.core.networks import from_json

import tfBaseTeam
import tfShared

import features
import reward

TEAM_NAME = "tfSimpleTeam"
NUM_TO_ACTION = ["South", "North", "East", "West", "Stop"]

def newTfAgent():
    network = layered_network_builder([
        dict(type='dense', size=32),
        dict(type='dense', size=32)
    ])

    # Define a state
    states = dict(shape=(25,), type='float')

    # Define an action (models internally assert whether
    # they support continuous and/or discrete control)
    actions = dict(continuous=False, num_actions=3)

    # The agent is configured with a single configuration object
    agent_config = Configuration(
        states=states,
        actions=actions,
        network=network
    )
    agent = TRPOAgent(config=agent_config)
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
    firstAgent = TensorForceSimpleAgent(firstIndex)
    secondAgent = TensorForceSimpleAgent(secondIndex)
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

class TensorForceSimpleAgent(tfBaseTeam.TensorForceAgent):
    """
    This Pacman Agent acts as a Runner for the Tensorforce agent
    """
    #####################################################
    def getReward(self, gameState, terminal):
        return reward.getReward(self, gameState, self.prevState, terminal)

    def makeTfState(self, gameState):
        feat = []
        for action in NUM_TO_ACTION:
            if action not in gameState.getLegalActions(self.index):
                action = "Stop"
            successor = gameState.generateSuccessor(self.index, action)
            feat.extend([
                features.getCarry(self, successor),
                features.getClosestFoodDist(self, successor),
                features.getClosestGhostDist(self, successor),
                features.getClosestInvaderDist(self, successor),
                features.getHomeDist(self, successor)
            ])
        print(feat)
        return feat