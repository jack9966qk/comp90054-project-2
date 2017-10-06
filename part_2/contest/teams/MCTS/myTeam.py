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

WEIGHTS = {"score": 1000, "myFood": 2, "opponentFood": -5, "numInvaders": -10, "death": -100}

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
        
        self.weightsDict = self.loadWeightDict()
        featuresTool.initGame(self,gameState)
        
        IOutil.saveFile(WEIGHTS_FILENAME,self.weightsDict)
        '''
        Your initialization code goes here, if you need any.
        '''
    
    def loadWeightDict(self):
        weights = IOutil.loadFile(WEIGHTS_FILENAME)
        Fdict = IOutil.loadFile(DICTS_FILENAME)
        Mdict = IOutil.loadFile(MODS_FILENAME)
        weight = util.Counter()
        for line in Fdict:
            weight[line] = 0
        for mod in Mdict:
            if weights.has_key(mod):
                weights[mod]=weight+weights[mod]
            else:
                weights[mod]=weight+util.Counter()
        return weights
        
    def evaluate(self,gameState,action):
        
        features = featuresTool.getFeatures(self,gameState,action)
        sfeatures = featuresTool.getFeatures(self,gameState,"Stop")
        mode = featuresTool.getMod(self,sfeatures,gameState)
        weights = self.weightsDict[mode]
        return features * weights
        
        
    def chooseAction(self, gameState):
        
        # Pick Action
        opponents = [i for i in self.getOpponents(gameState) if gameState.getAgentPosition(i) != None]
        
        if len(opponents) > 0:
            rootNode = self.MCTS(gameState, 30)
            children = rootNode.getChild()
            choice = max(children, key = lambda x: x.getTotalValue() / x.getVisits())
#            print choice.getTotalValue()/choice.getVisits()
            action = choice.getGameState().getAgentState(self.index).getDirection()
        else:
            actions = gameState.getLegalActions(self.index)
            actions.remove("Stop")
            values = [self.evaluate(gameState, a) for a in actions]
            maxValue = max(values)
            bestActions = [a for a, v in zip(actions, values) if v == maxValue]
            action = random.choice(bestActions)
        
        return action
    
    def MCTS(self, gameState, iteration):
        # 1 tree traversal
        # 2 node expansion
        # 3 simulation
        # 4 backpropagation
        
        # build initial tree
        root = MCT(None, gameState.deepCopy())
        actions = gameState.getLegalActions(self.index)
        actions.remove(Directions.STOP)
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
                # opponent would choose action that minimise our value
                state = curr.getGameState().deepCopy()
                opponents = [i for i in self.getOpponents(s) if s.getAgentPosition(i) != None]
                if len(opponents) > 0:
                    op = opponents[0]
                    opLegalAction = state.getLegalActions(op)
                    opLegalAction.remove(Directions.STOP)
                    minScore = 9999999
                    opState = None
                    for a in opLegalAction:
                        tempState = state.deepCopy()
                        AgentRules.applyAction(tempState, a, op)
                        tempScore = self.evaluateSimulation(tempState, state)
                        if tempScore < minScore:
                            minScore = tempScore
                            opState = tempState
                    actions = opState.getLegalActions(self.index)
                    actions.remove(Directions.STOP)
                    successors = [opState.generateSuccessor(self.index, a) for a in actions]
                    children = [MCT(curr, s) for s in successors]
                else:
                    actions = state.getLegalActions(self.index)
                    actions.remove(Directions.STOP)
                    successors = [state.generateSuccessor(self.index, a) for a in actions]
                    children = [MCT(curr, s) for s in successors]
                    curr.addChild(children)

                curr = random.choice(children)
            
            simulatedState = self.simulate(curr.getGameState())
            stateValue = self.evaluateSimulation(simulatedState, gameState)
            self.backprop(curr, stateValue)
            iteration -= 1
        
        return root
    
    
    def simulate(self, gameState):
        # simulate game for a given number of steps
        fakeState = gameState.deepCopy()
#        opponents = self.getOpponents(fakeState)
        opponents = [i for i in self.getOpponents(fakeState) if fakeState.getAgentPosition(i) != None]
        step = self.steps
        
        while step > 0:
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
        
        return fakeState
    
    
    def UCB1(self, node):
        # C is a hyperparameter needs to be tuned
        # UCB1 = avgV + C * sqrt (ln(N) / n)
        C = 0.5
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
    
    def evaluateSimulation(self, gameState, originalState):
        # evaluate the value for simulated state
        features = self.getSimulateFeature(gameState, originalState)
        weights = WEIGHTS
        return features * weights
    
    def getSimulateFeature(self, gameState, originalState):
        
        # features that represent a simulated game state
        features = util.Counter()
        features["score"] = self.getScore(gameState)
        features["myFood"] = len(self.getFoodYouAreDefending(gameState).asList())
        features["opponentFood"] = len(self.getFood(gameState).asList())
        
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        features["numInvaders"] = len(invaders)
        
        originalPosition = originalState.getAgentState(self.index).getPosition()
        simulatePosition = gameState.getAgentState(self.index).getPosition()
        features["death"] = self.getMazeDistance(originalPosition, simulatePosition) > self.steps
        
        return features
    
    def getMod(self,features,gameState):
        #closestGhost = min(features['Ghost1Close'],Ghost1Close['Ghost2Close'])
        
        if features['HomeDist'] >0 and features['Carry']>0 and features['HomeDist']<features['ClostestFoodDist']:
            return 'backhome'
        
        if features['TeamFoodLeft']<=2:
            return 'backhome'
        
        if (features['HasGhost']>0):
            return "backhome"
            
        if features["HasInvader1"]>0 and self.index == self.getTeam(gameState)[0]:
            if features["IsPacman"]>0:
                return "backhome"
            return "defense1"
            
        if features["HasInvader2"]>0 and self.index == self.getTeam(gameState)[1]:
            if features["IsPacman"]>0:
                return "backhome"
            return "defense2"
            
        return "offense"
        

    def final(self, gameState):
        CaptureAgent.final(self, gameState)
        # save updated weights to file



    

  
