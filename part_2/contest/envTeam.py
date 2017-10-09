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
import socket
import pickle
import numpy as np
import network

NUM_TO_ACTION = ["South", "North", "East", "West", "Stop"]


#################
# Team creation #
#################


def createTeam(firstIndex, secondIndex, isRed,
               first='EnvAgent', second='DummyAgent'):
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
    return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

def makeMatrixObservation(agent, gameState):
    observation = np.zeros((32, 16, 4))
    # self pos
    x, y = gameState.getAgentPosition(agent.index)
    observation[x-1, y-1, 0] = 1
    # food pos
    food = agent.getFood(gameState)
    for x in range(32):
        for y in range(16):
            if food[x][y]:
                observation[x-1, y-1, 1] = 1
    # opponent pos
    for opponentIdx in agent.getOpponents(gameState):
        pos = gameState.getAgentPosition(opponentIdx)
        if pos:
            observation[pos[0]-1, pos[1]-1, 2] = 1
    # wall pos
    wall = gameState.getWalls()
    food = agent.getFood(gameState)
    for x in range(32):
        for y in range(16):
            if wall[x][y]:
                observation[x-1, y-1, 3] = 1
    return observation

class EnvAgent(CaptureAgent):
    
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
        self.socket = socket.socket()
        # print("AGENT CONNECTING TO ENV")
        self.socket.connect(("localhost", 2333))
        observation = makeMatrixObservation(self, gameState)
        # print("AGENT SENDING INITIAL OBSERVATION")
        network.send(self.socket, observation)
        self.prevAction = None

    def chooseAction(self, gameState):
        if self.prevAction:
            if self.prevAction: self.sendResult(gameState, False)
        actionNum = network.receive(self.socket)
        action = NUM_TO_ACTION[actionNum]
        legal = gameState.getLegalActions()
        self.prevAction = action
        if action not in legal:
            action = "Stop"
        return action

    def getReward(self, state, action, nextState):
        nx, ny = nextState.getAgentPosition(self.index)
        x, y = state.getAgentPosition(self.index)
        if (abs(nx - x) + abs(ny - y)) > 1: # check death
            return -10
        if (nx, ny) == (x, y):
            return -1
        isRed = state.isOnRedTeam(self.index)
        food = state.getBlueFood() if isRed else state.getRedFood()
        capsule = state.getBlueCapsules() if isRed else state.getRedCapsules()
        if food[nx][ny]:
            return 1 # eat food
        if (nx, ny) in capsule:
            return 5 # eat capsule
        return 0

    def final(self, gameState):
        # print("AGENT FINAL")
        if self.prevAction: self.sendResult(gameState, True)
        self.socket.close()
        CaptureAgent.final(self, gameState)
            
        
    def sendResult(self, gameState, done):
        # print("AGENT SENDING RESULT")
        reward = self.getReward(self.getPreviousObservation(), self.prevAction, gameState)
        observation = makeMatrixObservation(self, gameState)
        network.send(self.socket, (observation, reward, done, {}))


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
