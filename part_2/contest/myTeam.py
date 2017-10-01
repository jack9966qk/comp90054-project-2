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
import featuresTool

#WEIGHTS_FILENAME = "trainedWeights.pickle"
WEIGHTS_FILENAME = 'rlWeights.json'
trainSet = []
labelSet = []
fdict = [
'ClostFoodDistance',
'FoodLeft'
]
featuresTool = featuresTool.featuresTool(usemodel = True)

# read from file if exist
#if os.path.exists(WEIGHTS_FILENAME):
#    WEIGHTS = loadWeightsJson(WEIGHTS_FILENAME)
#else:
#    WEIGHTS = util.Counter()

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
        
        
        #self.weights = WEIGHTS
        self.QValues = util.Counter()
        #self.epsilon = 0.2
        self.epsilon = 0
        self.gamma = 0.8
        self.alpha = 0.05
        self.discount = 0.9
        
        self.weights = util.Counter()
        featuresTool.initGame(self,gameState)
        #print WEIGHTS
        #for i in range(len(featuresTool.dict)):
        #    self.weights[featuresTool.dict[i]] = WEIGHTS[i]
        
        #util.pause
        '''
        Your initialization code goes here, if you need any.
        '''

        
    def evaluate(self,gameState,action):
        #features = self.getFeatures(gameState, action)
        features = featuresTool.getFeatures(self,gameState,action)
        #weights = self.weights
        #print features
        #return features * weights
        return featuresTool.evaluate(features)
        
    def chooseAction(self, gameState):
        # Pick Action
        prev = self.getPreviousObservation()
        #if prev:
        #    reward = self.getReward(prev, self.lastAction, gameState)
#            self.update(prev, self.lastAction, gameState, reward)
        #else:
        #    reward = 0
        
        actions = gameState.getLegalActions(self.index)
        actions.remove("Stop")
        values = [self.evaluate(gameState, a) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        
        
        if util.flipCoin(self.epsilon):
            action = random.choice(actions)
        else:
            action = random.choice(bestActions)
        #featuresTool.update(self,gameState,action)
        self.lastAction = action
        #features1 = self.getFeatures(gameState,action,sel = True)
        #tfeatures = featuresTool.getFeatures(self,gameState,action)
        #print zip(actions, values)
        #print action
        #print features1
        #print tfeatures
        #util.pause()
        #trainSet.append(moreUtil.getTrainSet(features1))
        #labelSet.append(reward)
        return action
    
        
    def setAdditionalState(self, additionalState):
        self.additionalState = additionalState

    def final(self, gameState):
        CaptureAgent.final(self, gameState)
        # save updated weights to file
        moreUtil.saveSet(trainSet,labelSet)
     #   saveWeightsJson(WEIGHTS, WEIGHTS_FILENAME)

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

    def getFeatures(self, gameState, action,sel = False):
        nextState = gameState.generateSuccessor(self.index, action)
        features = util.Counter()
        if sel : nextState = gameState
        features["invaderDist"] = moreUtil.getInvaderDistFeature(self, nextState)
#        features["invaderNum"] = moreUtil.getInvaderNumFeature(self, nextState)
        features["getHomeDist"] = moreUtil.getHomeDistFeature(self, nextState)
        features["ghostDist"] = moreUtil.getGhostDistFeature(self, nextState)
        features["isPacman"] = moreUtil.getIsPacmanFeature(self, nextState)
        features['foodLeft'] = moreUtil.getFoodLeftFeature(self, nextState)
        features['carry'] = moreUtil.getCarryFeature(self)
        features["closest-food"] = moreUtil.getClosestFoodFeature(self, gameState, nextState)
        #features["opponentMinDist1"] = moreUtil.getopponentMinDist(self,gameState)
        
        features["bias"] = 1.0
        
        #features.divideAll(10.0)
        return features

    

  
