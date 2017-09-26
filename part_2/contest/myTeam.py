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
from game import Directions
import game

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
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

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

        '''
        Your initialization code goes here, if you need any.
        '''
    def __init__(self, epsilon=0.05, gamma=0.8, alpha=0.2, **args):
        self.weights = util.Counter()
        self.QValues = util.Counter()
        self.epsilon = epsilon
        self.gamma = gamma
        self.alpha = alpha
        CaptureAgent.__init__(self, **args)
    
    def getQValue(self, state, action):
        sum = 0
        features = self.getFeatures(state, action)
        for feature, value in features.iteritems():
            sum += self.weights[feature] * value
        return sum
    
    def computeValueFromQValues(self, state, gameState):
        actions = gameState.getLegalActions(self.index)
        if actions is None or len(actions) == 0:
            return 0.0
        value = None
        for action in actions:
            q = self.getQValue(state, action)
            if value is None or value < q:
                value = q
        return value
    
    def computeActionFromQValues(self, state, gameState):
        actions = gameState.getLegalActions(self.index)
        if actions is None:
            return None
        value = None
        bestAction = None
        for action in actions:
            q = self.getQValue(state, action)
            if bestAction is None or value < q:
                value = q
                bestAction = [action]
            elif value == q:
                bestAction.append(action)
        return random.choice(bestAction)

    def chooseAction(self, state, gameState):
         # Pick Action
        legalActions = gameState.getLegalActions(self.index)
        action = None
        if legalActions is not None:
            if util.flipCoin(self.epsilon):
                action = random.choice(legalActions)
            else:
                action = self.computeActionFromQValues(state)

        return action
    
    def update(self, state, action, nextState, reward):
        maxNext = self.computeValueFromQValues(nextState)
        diff = reward + self.discount * maxNext - self.getQValue(state, action)
        features = self.featExtractor.getFeatures(state, action)
        for feature, value in features.iteritems():
            self.weights[feature] += self.alpha * diff * features[feature]

    def getReward(self, state, gameState):
        return self.getScore(gameState)

    def getFeatures(self, state, action):
        gameState = self.getCurrentObservation()
        nextState = gameState.generateSuccessor(self.index, action)
        food = self.getFood()
        walls = self.getWalls()
        oppo = self.getOpponents()
        oppoPos = [gameState.getAgentPosition(i) for i in oppo]
        
        features = util.Counter()
        
        next_x, next_y = nextState.getAgentPosition(self.index)
        
        features["bias"] = 1.0
        
        features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in oppoPos)

        # if there is no danger of ghosts then add the food feature
        if not features["#-of-ghosts-1-step-away"] and food[next_x][next_y]:
            features["eats-food"] = 1.0

        dist = closestFood((next_x, next_y), food, walls)
        if dist is not None:
            # make the distance a number less than one otherwise the update
            # will diverge wildly
            features["closest-food"] = float(dist) / (walls.width * walls.height)
        features.divideAll(10.0)
        return features
        
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
