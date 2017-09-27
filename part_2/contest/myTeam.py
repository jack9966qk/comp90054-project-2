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
        self.epsilon = 0.05
        self.gamma = 0.8
        self.alpha = 0.2
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
        reward = nextState.getScore() - state.getScore()
        reward -= 0.1 # time
        nx, ny = nextState.getAgentPosition(self.index)
        x, y = state.getAgentPosition(self.index)
        if (abs(nx - x) + abs(ny - y)) > 1: # check death
            reward -= 10
        isRed = state.isOnRedTeam(self.index)
        food = state.getBlueFood() if isRed else state.getRedFood()
        capsule = state.getBlueCapsules() if isRed else state.getRedCapsules()
        if food[nx][ny]:
            reward += 1 # eat food
        if (nx, ny) in capsule:
            reward += 5 # eat capsule
        if action == "stop":
            return -1
        return reward

    def getFeatures(self, gameState, action):
        nextState = gameState.generateSuccessor(self.index, action)
        myState = nextState.getAgentState(self.index)
        food = self.getFood(gameState)
        walls = gameState.getWalls()
        
        features = util.Counter()
        
        next_x, next_y = nextState.getAgentPosition(self.index)
        
        
        features["invaderDist"] = min(self.getInvadersDist(nextState))
        features["invaderNum"] = len(self.getInvadersDist(nextState))
        features["getHomeDist"] = self.getHomeDist(nextState)
        features["ghostDist"] = min(self.getGhostDist(nextState))
        features["isPacman"] = myState.isPacman
        
        features["bias"] = 1.0
        
        features['foodLeft'] = len(self.getFood(nextState).asList())

        features['carry'] = self.additionalState.carry[self.index]

        dist = closestFood((next_x, next_y), food, walls)
        if dist is not None:
            # make the distance a number less than one otherwise the update
            # will diverge wildly
            features["closest-food"] = float(dist) / (walls.width * walls.height)
        
        features.divideAll(10.0)
        return features
        
    def getInvadersDist(self,gameState):
        myState = gameState.getAgentState(self.index)
        myPos = myState.getPosition()
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
        if len(dists)==0 :
            dists = [-1]
        return dists
    
    def getHomeDist(self,gameState):
        middle = self.middle
        bestv = 999999
        myState = gameState.getAgentState(self.index)
        if not myState.isPacman: return 0
        pos1 = gameState.getAgentPosition(self.index)
        walls = gameState.getWalls().asList()
        
        for i in range(16):
            pos2 = (middle,i)
            if not pos2 in walls:
                tempv = self.getMazeDistance(pos1,pos2)
                bestv = min(bestv,tempv)
        
        return bestv
  
    def getGhostDist(self,gameState):
        myState = gameState.getAgentState(self.index)
        myPos = myState.getPosition()
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        invaders = [a for a in enemies if (not a.isPacman) and a.getPosition() != None]
        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
        if len(dists)==0 :
            dists = [-1]
    
        return dists
  
def closestFood(pos, food, walls):
    """
    closestFood -- this is similar to the function that we have
    worked on in the search project; here its all in one place
    """
    fringe = [(pos[0], pos[1], 0)]
    expanded = set()
    while fringe:
        pos_x, pos_y, dist = fringe.pop(0)
        if (pos_x, pos_y) in expanded:
            continue
        expanded.add((pos_x, pos_y))
        # if we find a food at this location then exit
        if food[pos_x][pos_y]:
            return dist
        # otherwise spread out from the location to its neighbours
        nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
        for nbr_x, nbr_y in nbrs:
            fringe.append((nbr_x, nbr_y, dist+1))
    # no food found
    return None
