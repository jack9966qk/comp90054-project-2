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

import os
import sys
teamName = os.path.split(os.path.dirname(os.path.abspath(__file__)))[1]
dir = "teams/{}/".format(teamName)
sys.path.append(dir)

from captureAgents import CaptureAgent
import random, time, util
from game import Directions, Actions
import game
import os
import moreUtil
import IOutil
import featuresTool
from MCT import MCT
from math import log, sqrt
from capture import AgentRules

WEIGHTS_FILENAME = 'WeightsDict.json'
DICTS_FILENAME = 'Fdict.json'
MODS_FILENAME = 'ModDict.json'
featuresTool = featuresTool.featuresTool()
PRINTF = False

WEIGHTS = {"score": 1000, "myFood": 2, "opponentFood": -5, "numInvaders": -200,
           "death": -1000, "distanceToFood": -50, "isPacman": 20, "carry": 100,
           "isGhost": 5, "invaderDistance": -100}
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
  
  
  firstAgent = eval(first)(firstIndex)
  secondAgent = eval(second)(secondIndex)
  
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
        self.steps = 10
        self.believePos = None
        
        featuresTool.initGame(self,gameState)
        
        '''
        Your initialization code goes here, if you need any.
        '''
        
        
    def chooseAction(self, gameState):
        
        # Pick Action
        opponents = [i for i in self.getOpponents(gameState) if gameState.getAgentPosition(i) != None]
        enemySimulation = len(opponents) > 0
        
        evalFunc = "moveForward"
        myFood = len(self.getFoodYouAreDefending(gameState).asList())
        if myFood <= 15:
            evalFunc = "defensive"
        elif enemySimulation:
            evalFunc = "realTime"
        
        rootNode = self.MCTS(gameState, 50, evalFunc)
        children = rootNode.getChild()
        """
        for child in children:
            v = child.getTotalValue() / child.getVisits()
            print v, child.getGameState().getAgentState(self.index).getDirection()
        """
        choice = max(children, key = lambda x: x.getTotalValue() / x.getVisits())
#            print choice.getTotalValue()/choice.getVisits()
        action = choice.getGameState().getAgentState(self.index).getDirection()
#        util.pause()
        
        return action
    
    def simulateDeadEnd(self, gameState, action, prevFood, step):
        
        # simulate whether a given action leads to a dead end
        if step == 0: 
            return False
        
        newState = gameState.generateSuccessor(self.index, action)
        # if there is food, return false
        currFood = len(self.getFood(newState).asList())
        if currFood < prevFood:
            return False
        actions = newState.getLegalActions(self.index)
        actions.remove(Directions.STOP)
        reverse = Directions.REVERSE[action]
        if reverse in actions:
            actions.remove(reverse)
        # if only stop and reverse and applicable, it is a dead end
        if len(actions) == 0:
            return True
        # repeat this process utill a given step
        for action in actions:
            if not self.simulateDeadEnd(newState, action, currFood, step-1):
                return False
        
        return True
        
    
    def MCTS(self, gameState, iteration, evalFunc):
        # Monte Carlo Tree Search
        # 1 tree traversal
        # 2 node expansion
        # 3 simulation
        # 4 backpropagation
        
        # build initial tree
        root = MCT(None, gameState.deepCopy())
        actions = gameState.getLegalActions(self.index)
        
        # remove some randomness by removing stop and reverse
        actions.remove(Directions.STOP)
        """
        myAction = gameState.getAgentState(self.index).getDirection()
        reverse = Directions.REVERSE[myAction]
        if reverse in actions and len(actions) > 1:
            actions.remove(reverse)
        """
        

        # remove action that leads to a dead end
        backup = list(actions)
        foodNum = len(self.getFood(gameState).asList())
        for action in actions:
            steps = self.steps
            if self.simulateDeadEnd(gameState, action, foodNum, steps):
                actions.remove(action)
        if len(actions) == 0:
            actions = backup
#        print actions
        
        successors = [gameState.generateSuccessor(self.index, a) for a in actions]
        children = [MCT(root, s) for s in successors]
        root.addChild(children)
        
        while iteration > 0:
            curr = root
            
            while len(curr.getChild()) != 0:
                # while current node is not a leaf node
                # choose a child node that maximises UCB1 score as current node
                children = curr.getChild()
                maxScore = None
                maxChild = None
                for node in children:
                    score = self.UCB1(node)
                    if maxScore is None or score > maxScore:
                        maxScore = score
                        maxChild = node
                curr = maxChild
            
            # current node is a leaf node
            if curr.getVisits() == 0: 
                # never been visited before
                # rollout directly
                pass
            else:
                # if visited before, expand this node
                # add new node per legal action and pick one as current node
                
                # simulate opponent if observable
                # opponent would choose an action that minimise our value
                state = curr.getGameState().deepCopy()
                opponents = [i for i in self.getOpponents(state) if state.getAgentPosition(i) != None]
                if len(opponents) > 0:
                    op = opponents[0]
                    opLegalAction = state.getLegalActions(op)
                    opLegalAction.remove(Directions.STOP)
                    minScore = 9999999
                    opState = None
                    l = []
                    for a in opLegalAction:
                        tempState = state.deepCopy()
                        AgentRules.applyAction(tempState, a, op)
                        tempScore = self.evaluateSimulation(tempState, state, evalFunc)
                        if tempScore < minScore:
                            minScore = tempScore
                            l = [tempState]
                        elif tempScore == minScore:
                            l.append(tempState)
                    opState = random.choice(l)
                    actions = opState.getLegalActions(self.index)
                    actions.remove(Directions.STOP)
                    successors = [opState.generateSuccessor(self.index, a) for a in actions]
                    children = [MCT(curr, s) for s in successors]
                else:
                    # if opponent not observable, simulate agent self
                    actions = state.getLegalActions(self.index)
                    actions.remove(Directions.STOP)
                    successors = [state.generateSuccessor(self.index, a) for a in actions]
                    children = [MCT(curr, s) for s in successors]
                    curr.addChild(children)

                curr = random.choice(children)
            
            simulatedState = self.simulate(curr.getGameState())
            stateValue = self.evaluateSimulation(simulatedState, gameState, evalFunc)
            self.backprop(curr, stateValue)
            iteration -= 1
        
        return root
    
    
    def simulate(self, gameState):
        # simulate game for a given number of steps
        fakeState = gameState.deepCopy()
        opponents = [i for i in self.getOpponents(fakeState) if fakeState.getAgentPosition(i) != None]
        step = self.steps
        
        while step > 0:
            # reduce randomness by remove some actions
            myActions = fakeState.getLegalActions(self.index)
            # prevent standing by
            myActions.remove(Directions.STOP)
            # prevent keeping moving back and forth
            reverse = Directions.REVERSE[fakeState.getAgentState(self.index).getDirection()]
            if reverse in myActions and len(myActions) > 1:
                myActions.remove(reverse)
            myAction = random.choice(myActions)
            fakeState = fakeState.generateSuccessor(self.index, myAction)
            
            # simulate opponents randomly
            opActions = []
            for op in opponents:
                opLegalAction = fakeState.getLegalActions(op)
                opLegalAction.remove(Directions.STOP)
                opActions.append(opLegalAction)
            for actions, op in zip(opActions, opponents):
                AgentRules.applyAction(fakeState, random.choice(actions), op)

            step -= 1
        
        # return the game state after simulation
        return fakeState
    
    
    def UCB1(self, node):
        # C is a hyperparameter needs to be tuned
        # UCB1 = avgV + C * sqrt (ln(N) / n)
        C = sqrt(2)
        n = node.getVisits()
        if n == 0:
            ucb1 = float("inf")
        else:
            avgValue = node.getTotalValue() / node.getVisits()
            ucb1 = avgValue + C * sqrt(log(node.getParent().getVisits()) / n)
        return ucb1
    
    
    def backprop(self, node, value):
        # backpropagation step
        if node is not None:
            node.visit()
            node.updateValue(value)
            self.backprop(node.getParent(), value)
    
    def evaluateSimulation(self, gameState, originalState, evalFunc):
        # evaluate the value for simulated state
        if evalFunc == "realTime":
            features = self.getRealTimeFeature(gameState, originalState)
        elif evalFunc == "moveForward":
            features = self.moveForwardFeature(gameState)
        elif evalFunc == "defensive":
            features = self.defensiveFeature(gameState, originalState)
        weights = WEIGHTS
        return features * weights
    
    def getRealTimeFeature(self, gameState, originalState):
        
        # features that represent a simulated game state
        features = util.Counter()
        features["score"] = self.getScore(gameState)
        features["myFood"] = len(self.getFoodYouAreDefending(gameState).asList())
        features["carry"] = gameState.getAgentState(self.index).numCarrying
        
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        features["numInvaders"] = len(invaders)
        
        originalPosition = originalState.getAgentState(self.index).getPosition()
        simulatePosition = gameState.getAgentState(self.index).getPosition()
        features["death"] = self.getMazeDistance(originalPosition, simulatePosition) > self.steps
#        if features["death"]: print "die"
        
        return features
    
    def moveForwardFeature(self, gameState):
        
        # features that decide where to move
        features = util.Counter()
        
        myPos = gameState.getAgentState(self.index).getPosition()
        minDistance = min([self.getMazeDistance(myPos, food) for food in self.getFood(gameState).asList()])
        features["distanceToFood"] = minDistance
#        print features["distanceToFood"]
        features["opponentFood"] = len(self.getFood(gameState).asList())
        features["carry"] = gameState.getAgentState(self.index).numCarrying
        
        features["isPacman"] = 1 if gameState.getAgentState(self.index).isPacman else 0
        
        return features
    
    def defensiveFeature(self, gameState, originalState):
        
        # features for defense
        features = util.Counter()
        
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        prevState = self.getPreviousObservation()
        prevFood = self.getFoodYouAreDefending(prevState).asList()
        currentFood = self.getFoodYouAreDefending(originalState).asList()
        
        myPos = gameState.getAgentState(self.index).getPosition()
        if self.believePos == None:
            self.believePos = random.choice(currentFood)
        if len(invaders) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            features["invaderDistance"] = min(dists)
        elif len(prevFood) > len(currentFood):
            # if there is food being eaten and opponent unobservable
            # opponent position is where food vanishes
            invaderPos = [food for food in prevFood if food not in currentFood]
            self.believePos = invaderPos[0]
            features["invaderDistance"] = self.getMazeDistance(myPos, self.believePos)
        else:
            features["invaderDistance"] = self.getMazeDistance(myPos, self.believePos)
#        print features["invaderDistance"]
        
        features["myFood"] = len(self.getFoodYouAreDefending(gameState).asList())
        features["isGhost"] = 0 if gameState.getAgentState(self.index).isPacman else 1
        
        return features
    
        

    def final(self, gameState):
        CaptureAgent.final(self, gameState)
        # save updated weights to file



    

  
