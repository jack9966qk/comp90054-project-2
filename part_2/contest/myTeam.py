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
import random, time, util
from game import Directions, Actions
import game
import os
from weightIO import *
import moreUtil
from additionalState import AdditionalState

WEIGHTS_FILENAME = "trainedWeights.pickle"

# read from file if exist
if os.path.exists(WEIGHTS_FILENAME):
    WEIGHTS = loadWeightsJson(WEIGHTS_FILENAME)
else:
    WEIGHTS = util.Counter()

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DummyAgent', second = 'DummyAgent'):
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
  additionalState = AdditionalState(isRed, [firstIndex, secondIndex])
  firstAgent = eval(first)(firstIndex)
  secondAgent = eval(second)(secondIndex)
  firstAgent.setAdditionalState(additionalState)
  secondAgent.setAdditionalState(additionalState)
  return [firstAgent, secondAgent]

##########
# Agents #
##########

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
        self.start = gameState.getAgentPosition(self.index)

        self.walls = gameState.getWalls()
        self.size = (self.walls.width,self.walls.height)
        self.middle = (self.size[0]/2) - (self.start[0]%2)
        
        self.weights = WEIGHTS
        self.QValues = util.Counter()
        self.epsilon = 0.2
        self.gamma = 0.8
        self.alpha = 0.05
        self.discount = 0.9
        '''
        Your initialization code goes here, if you need any.
        '''

    def getQValue(self, gameState, action):
        sum = 0
        features = self.getFeatures(gameState, action)
        for feature, value in features.iteritems():
            sum += self.weights[feature] * value
        return sum
    
    def computeValueFromQValues(self, gameState):
        actions = gameState.getLegalActions(self.index)
        if actions is None or len(actions) == 0:
            return 0.0
        value = None
        for action in actions:
            q = self.getQValue(gameState, action)
            if value is None or value < q:
                value = q
        return value
    
    def computeActionFromQValues(self, gameState):
        actions = gameState.getLegalActions(self.index)
        if actions is None:
            return None
        value = None
        bestAction = None
        for action in actions:
            q = self.getQValue(gameState, action)
            if bestAction is None or value < q:
                value = q
                bestAction = [action]
            elif value == q:
                bestAction.append(action)
        return random.choice(bestAction)

    def chooseAction(self, gameState):
        # Pick Action
        prev = self.getPreviousObservation()
        if prev:
            reward = self.getReward(prev, self.lastAction, gameState)
            self.update(prev, self.lastAction, gameState, reward)
        legalActions = gameState.getLegalActions(self.index)
        action = None
        if legalActions is not None:
            if util.flipCoin(self.epsilon):
                action = random.choice(legalActions)
            else:
                action = self.computeActionFromQValues(gameState)
        self.lastAction = action
        self.additionalState.update(gameState, self.index, action)
        return action
    
    def update(self, state, action, nextState, reward):
        maxNext = self.computeValueFromQValues(nextState)
        diff = reward + self.discount * maxNext - self.getQValue(state, action)
        features = self.getFeatures(state, action)
#        print features['invaderNum']
        for feature, value in features.iteritems():
            self.weights[feature] += self.alpha * diff * features[feature]
        
    def setAdditionalState(self, additionalState):
        self.additionalState = additionalState

    def final(self, gameState):
        CaptureAgent.final(self, gameState)
        # save updated weights to file
        saveWeightsJson(WEIGHTS, WEIGHTS_FILENAME)

    # def getReward(self, gameState):
    #     return self.getScore(gameState)
    def getReward(self, state, action, nextState):
        nx, ny = nextState.getAgentPosition(self.index)
        x, y = state.getAgentPosition(self.index)
        
        if (abs(nx - x) + abs(ny - y)) > 1: # check death
            return -10
        
        if (nx, ny) == (x, y): # no move
            return -1
        
        enemies = [state.getAgentState(i) for i in self.getOpponents(state)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        positions = [a.getPosition() for a in invaders]
        if len(positions) > 0 and not state.getAgentState(self.index).isPacman:
            for position in positions:
                if (nx, ny) == position: return 5 # chase invaders
        
        features = self.getFeatures(state, action)
        if state.getAgentState(self.index).isPacman and not nextState.getAgentState(self.index).isPacman and features['carry'] > 0:
            return features['carry'] * 20
        
        isRed = state.isOnRedTeam(self.index)
        food = state.getBlueFood() if isRed else state.getRedFood()
        capsule = state.getBlueCapsules() if isRed else state.getRedCapsules()
        if food[nx][ny]:
            return 1 # eat food
        if (nx, ny) in capsule:
            return 3 # eat capsule
        return -5

    def getFeatures(self, gameState, action):
        nextState = gameState.generateSuccessor(self.index, action)
        features = util.Counter()
        
        features["invaderDist"] = moreUtil.getInvaderDistFeature(self, nextState)
#        features["invaderNum"] = moreUtil.getInvaderNumFeature(self, nextState)
        features["getHomeDist"] = moreUtil.getHomeDistFeature(self, nextState)
        features["ghostDist"] = moreUtil.getGhostDistFeature(self, nextState)
        features["isPacman"] = moreUtil.getIsPacmanFeature(self, nextState)
        features['foodLeft'] = moreUtil.getFoodLeftFeature(self, nextState)
        features['carry'] = moreUtil.getCarryFeature(self)
        features["closest-food"] = moreUtil.getClosestFoodFeature(self, gameState, nextState)

        features["bias"] = 1.0
        
        features.divideAll(10.0)
        return features

    

  
