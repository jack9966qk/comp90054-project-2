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

from tensorforce import Configuration
from tensorforce.agents import PPOAgent, DQNAgent
from tensorforce.core.networks import layered_network_builder
from tensorforce.core.networks import from_json

from baselineTeam import OffensiveReflexAgent, DefensiveReflexAgent
import random

from itertools import product

import moreUtil
import tfTeam
import tfShared
import numpy as np

NUM_TO_ACTION = ["South", "North", "East", "West", "Stop"]

def newTfAgent():
    ##### ADAPTED FROM TENSORFORCE BLOGPOST
    # https://reinforce.io/blog/introduction-to-tensorforce/

    network = from_json("tfCNN.json")

    # Define a state
    states = dict(shape=(7, 20, 12), type='float')

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
    agent = TensorForceCnnAgent(firstIndex)
    if useShared == "True":
        print("USE GLOBAL AGENT")
        agent.tfAgent = tfShared.TF_AGENT
    else:
        agent.tfAgent = newTfAgent()
        tfTeam.loadModelIfExists(agent.tfAgent)

    agent.mode = mode
    if mode == "Test":
        print("SET MODE TO TEST")
    else:
        print("SET MODE TO TRAIN")

    # baselineAgent = random.choice([DefensiveReflexAgent(secondIndex), OffensiveReflexAgent(secondIndex)])
    # return [agent, baselineAgent]
    return [agent, DummyAgent(secondIndex)]

##########
# Agents #
##########

class TensorForceCnnAgent(tfTeam.TensorForceAgent):
    """
    This Pacman Agent acts as a Runner for the Tensorforce agent
    """
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
        observation = np.zeros((7, 20, 12))

        homeLo, homeHi = moreUtil.getHomeArea(gameState, self.red)

        def posToIdx(pos):
            x, y = pos
            return moreUtil.getLayoutSize(gameState)[1] - y - 1, x

        allPos = list(product(range(20), range(7)))

        # self ghost/pacman pos [x, y, 0], [x, y, 1]
        x, y = posToIdx( gameState.getAgentPosition(self.index) )
        # print("self at {}, {}".format(x, y))
        if homeLo <= x <= homeHi:
            observation[x , y, 0] = 1
        else:
            observation[x , y, 1] = 1
        
        # teammate ghost/pacman pos [x, y, 2], [x, y, 3]
        for m in self.featuresTool.mate:
            print(self.featuresTool.probMap[m])
            x, y = posToIdx( self.featuresTool.probMap[m][0] )
            if homeLo <= x <= homeHi:
                observation[x, y, 2] = 1
            else:
                observation[x, y, 3] = 1
        
        # opponent invader/ghost/scaredGhost pos [x, y, 4], [x, y, 5], [x, y, 6]
        for o in self.featuresTool.opp:
            x, y = posToIdx( self.featuresTool.probMap[o][0] )
            if homeLo <= x <= homeHi:
                observation[x, y, 4] = 1
            else:
                observation[x, y, 5] = 2
            # TODO scared
        
        # food pos [x, y, 7]
        food = self.getFood(gameState)
        for pos in allPos:
            # print(pos)
            if food[pos[0]][pos[1]]:
                x, y = posToIdx( pos )
                observation[x, y, 7] = 1

        # food defending pos [x, y, 8]
        foodDef = self.getFoodYouAreDefending(gameState)
        for pos in allPos:
            if foodDef[pos[0]][pos[1]]:
                x, y = posToIdx( pos )
                observation[x, y, 8] = 1

        # wall pos [x, y, 9]
        wall = gameState.getWalls()
        for pos in allPos:
            if wall[pos[0]][pos[1]]:
                x, y = posToIdx( pos )
                observation[x, y, 9] = 1

        # capsule pos [x, y, 10]
        # print(self.getCapsules(gameState))
        for pos in self.getCapsules(gameState):
            x, y = posToIdx( pos )
            observation[x, y, 10] = 1

        for pos in allPos:
            x, y = posToIdx(pos)
            if homeLo <= pos[0] <= homeHi:
                observation[x, y, 11] = 1
            else:
                observation[x, y, 11] = -1

        # for i in range(11):
        #     print(i)
        #     print(observation[:, :, i])
        #     print()

        return observation


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
