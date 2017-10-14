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
import os
import featuresTool
from MCT import MCT
from math import log, sqrt
from capture import AgentRules

WEIGHTS = {"score": 1000, "myFood": 30, "opponentFood": -5, "eatCapsule": 200,
           "death": -800, "distanceToFood": -5, "isPacman": 20, "carry": 100,
           "isGhost": 50, "invaderDistance": -50, "homeDist": -10, "reverse": -50}
DEBUG = False
mapTool = featuresTool.featuresTool()

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'MonteCarloAgent', second = 'MonteCarloAgent'):
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

class MonteCarloAgent(CaptureAgent):
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
        self.middle = self.size[0]/2 if self.red else self.size[0]/2 - 1
        self.steps = 3
        self.lastEvalFunc = "offensive"
        self.oppoScared = 0
        mapTool.initGame(self,gameState)
#        featuresTool.update(self, gameState, gameState)
        
        
    def chooseAction(self, gameState):
        
        # Pick Action
        oppoState = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        myPos = gameState.getAgentState(self.index).getPosition()
        opponentsPos = [gameState.getAgentPosition(i) for i in self.getOpponents(gameState) if gameState.getAgentPosition(i) != None]
        distances = [self.getMazeDistance(myPos, food) for food in self.getFood(gameState).asList()]
        minDist = min(distances) if len(distances) != 0 else 0
        team = self.getTeam(gameState)
        
        agentState = gameState.getAgentState(self.index)
        
        enemySimulation = False
        for pos in opponentsPos:
            if self.getMazeDistance(myPos, pos) <= 5:
                enemySimulation = True
        
        self.invaderNum = len([s for s in oppoState if s.isPacman])
        invaderDist = self.defensiveFeature(gameState)["invaderDistance"]
        
        prevState = self.getPreviousObservation()
        if self.oppoScared > 0:
            self.oppoScared -= 1
        if prevState != None and len(self.getCapsules(prevState)) > len(self.getCapsules(gameState)):
            # if capsule eaten, keep a timer
            self.oppoScared = 40
        
        evalFunc = "offensive"
        
        if agentState.numCarrying >= 10 or len(self.getFood(gameState).asList()) < 3:
            evalFunc = "backHome"
        elif self.oppoScared > 0:
            if self.oppoScared > self.homeDistance(gameState) / 3:
                evalFunc = "offensive"
            else:
                evalFunc = "backHome"
        elif oppoState[0].isPacman or oppoState[1].isPacman:
            if (oppoState[0].isPacman and self.index == team[0]) or (oppoState[1].isPacman and self.index == team[1]):
                if agentState.numCarrying > 0:
                    evalFunc = "backHome"
                else:
                    if invaderDist < agentState.scaredTimer and minDist < agentState.scaredTimer:
                        evalFunc = "realTime" if enemySimulation else "offensive"
                    else:
                        evalFunc = "defensive"
        elif enemySimulation:
            evalFunc = "realTime"
        
        rootNode = self.MCTS(gameState.deepCopy(), 20, evalFunc)
        children = rootNode.getChild()
        self.lastEvalFunc = evalFunc
        
        if DEBUG:
            for child in children:
                v = child.getTotalValue() / child.getVisits()
                print v, child.getVisits(), child.getGameState().getAgentState(self.index).getDirection()
        
        # choose the action that has highest average utility
        choice = max(children, key = lambda x: x.getTotalValue() / x.getVisits())
        action = choice.getGameState().getAgentState(self.index).getDirection()
        
        mapTool.update(self, gameState, gameState.generateSuccessor(self.index, action))
        
        if DEBUG:
            self.debugClear()
            self.debugDraw(self.p, [0,1,1])
            util.pause()
        if featuresTool.DRAW:
            util.pause()
        
        return action
    
    def simulateDeadEnd(self, gameState, action, prevFood, step):
        
        # simulate whether a given action leads to a dead end
        if step == 0: 
            return False
        
         # if agent is ghost and encounter a pacman, return false
        myPos = gameState.getAgentState(self.index).getPosition()
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        if len(invaders) != 0:
            nextPos = Actions.getSuccessor(myPos, action)
            if nextPos in [a.getPosition() for a in invaders]:
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
        root = MCT(None, gameState.deepCopy(), 0)
        actions = gameState.getLegalActions(self.index)
        self.p = []
        
        # remove some randomness by removing stop
        actions.remove(Directions.STOP)

        # remove action that leads to a dead end
        backup = list(actions)
        foodNum = len(self.getFood(gameState).asList())
        for action in actions:
            if self.simulateDeadEnd(gameState, action, foodNum, 5):
                actions.remove(action)
        if len(actions) == 0:
            actions = backup
#        print actions
        
        successors = [gameState.generateSuccessor(self.index, a) for a in actions]
        children = [MCT(root, s, 1) for s in successors]
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
                # opponent would choose an action that minimises our expected value
                state = curr.getGameState().deepCopy()
                opponents = [i for i in self.getOpponents(state) if state.getAgentPosition(i) != None]
                opponentsPos = [state.getAgentPosition(i) for i in opponents]
                myPos = state.getAgentState(self.index).getPosition()
                if len(opponents) > 0 and self.getMazeDistance(myPos, opponentsPos[0]) <= 5:
                    op = opponents[0]
                    opLegalAction = state.getLegalActions(op)
                    opLegalAction.remove(Directions.STOP)
                    if state.getAgentState(self.index).isPacman and not state.getAgentState(op).isPacman:
                        # if agent is pacman and opponent is ghost
                        # simulate being chased
                        opPos = state.getAgentPosition(op)
                        myPos = state.getAgentPosition(self.index)
                        # find the action that moves closest to our agent position
                        minAct = min(opLegalAction, key = lambda x: self.getMazeDistance(myPos, Actions.getSuccessor(opPos, x)))
                        opState = state.deepCopy()
                        AgentRules.applyAction(opState, minAct, op)
                        AgentRules.checkDeath(opState, op)
                    elif not state.getAgentState(self.index).isPacman and state.getAgentState(op).isPacman:
                        # if agent is ghost and opponent is pacman
                        # simulate chasing
                        opPos = state.getAgentPosition(op)
                        myPos = state.getAgentPosition(self.index)
                        maxAct = max(opLegalAction, key = lambda x: self.getMazeDistance(myPos, Actions.getSuccessor(opPos, x)))
                        opState = state.deepCopy()
                        AgentRules.applyAction(opState, maxAct, op)
                        AgentRules.checkDeath(opState, op)
                    else:
                        # else opponent choose action by minisizing our value
                        minScore = float("inf")
                        opState = None
                        l = []
                        for a in opLegalAction:
                            tempState = state.deepCopy()
                            AgentRules.applyAction(tempState, a, op)
                            AgentRules.checkDeath(tempState, op)
                            tempScore = self.evaluateSimulation(tempState, state, evalFunc, 0, Directions.STOP)
                            if tempScore < minScore:
                                minScore = tempScore
                                l = [tempState]
                            elif tempScore == minScore:
                                l.append(tempState)
                        opState = random.choice(l)
                    
                    actions = opState.getLegalActions(self.index)
                    actions.remove(Directions.STOP)
                    reverse = Directions.REVERSE[opState.getAgentState(self.index).getDirection()]
                    if reverse in actions and len(actions) > 1:
                        actions.remove(reverse)
                    successors = [opState.generateSuccessor(self.index, a) for a in actions]
                else:
                    # if opponent not observable, simulate agent itself
                    actions = state.getLegalActions(self.index)
                    actions.remove(Directions.STOP)
                    successors = [state.generateSuccessor(self.index, a) for a in actions]
                    
                children = [MCT(curr, s, curr.getDepth()+1) for s in successors]
                curr.addChild(children)
                curr = random.choice(children)
            
            # determine the action that leads to current node
            n = curr
            while n.getParent() != root:
                n = n.getParent()
            action = n.getGameState().getAgentState(self.index).getDirection()
            
            states = [self.simulate(curr.getGameState()) for i in range(2)]
            values = [self.evaluateSimulation(s, gameState, evalFunc, curr.getDepth(), action) for s in states]
            stateValue = max(values)
            
            self.backprop(curr, stateValue)
            iteration -= 1
        
        return root
    
    
    def simulate(self, gameState):
        # simulate game for a given number of steps
        fakeState = gameState.deepCopy()
        opponentsTemp = [i for i in self.getOpponents(fakeState) if fakeState.getAgentPosition(i) != None]
        myPos = fakeState.getAgentPosition(self.index)
        opponents = [i for i in opponentsTemp if self.getMazeDistance(myPos, fakeState.getAgentPosition(i)) <= 5]
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
                AgentRules.checkDeath(fakeState, op)

            step -= 1
        
        # return the game state after simulation
        return fakeState
    
    
    def UCB1(self, node):
        # C is a parameter needs to be tuned
        # UCB1 = avgV + C * sqrt (ln(N) / n)
        C = 600
        n = node.getVisits()
        if n == 0:
            ucb1 = float("inf")
        else:
            avgValue = node.getTotalValue() / n
            ucb1 = avgValue + C * sqrt(log(node.getParent().getVisits()) / n)
        return ucb1
    
    
    def backprop(self, node, value):
        # backpropagation step
        gamma = 0.9
        if node is not None:
            node.visit()
            node.updateValue(value * gamma)
            self.backprop(node.getParent(), value * gamma)
    
    def evaluateSimulation(self, gameState, originalState, evalFunc, depth, action):
        # evaluate utility for simulated state
        
        if evalFunc == "realTime":
            features = self.realTimeFeature(gameState, originalState, depth)
        elif evalFunc == "offensive":
            features = self.offensiveFeature(gameState, originalState, action, depth)
        elif evalFunc == "defensive":
            features = self.defensiveFeature(gameState)
        elif evalFunc == "backHome":
            features = self.backHomeFeature(gameState, originalState, depth)
        weights = WEIGHTS
        return features * weights
    
    
    def backHomeFeature(self, gameState, originalState, depth):
        
        features = util.Counter()
        originalPosition = originalState.getAgentState(self.index).getPosition()
        simulatePosition = gameState.getAgentState(self.index).getPosition()
        features["death"] = self.getMazeDistance(originalPosition, simulatePosition) > (self.steps + depth + 1)
        
        features["score"] = self.getScore(gameState) - self.getScore(originalState)
        
        features["homeDist"] = self.homeDistance(gameState)
        
        return features
    
    def offensiveFeature(self, gameState, originalState, action, depth):
        
        # features that decide where to move
        features = util.Counter()
        
        originalPosition = originalState.getAgentState(self.index).getPosition()
        simulatePosition = gameState.getAgentState(self.index).getPosition()
        agentState = originalState.getAgentState(self.index)
        if not agentState.isPacman and abs(originalPosition[0]-self.middle) > 1 and agentState.scaredTimer == 0:
            # if agent is ghost and not close enough to mid lane
            # do not penalize for death
            features["death"] = 0
        else:
            features["death"] = self.getMazeDistance(originalPosition, simulatePosition) > (self.steps + depth + 1)
        
        originalDirection = originalState.getAgentState(self.index).getDirection()
        reverse = Directions.REVERSE[originalDirection]
        features["reverse"] = (self.lastEvalFunc == "offensive") and (action == reverse)
        
        myPos = gameState.getAgentState(self.index).getPosition()
        distances = [self.getMazeDistance(myPos, food) for food in self.getFood(gameState).asList()]
        features["distanceToFood"] = min(distances) if len(distances) != 0 else 0
        features["opponentFood"] = len(self.getFood(gameState).asList())
        features["carry"] = gameState.getAgentState(self.index).numCarrying
        
        features["eatCapsule"] = self.getCapsules(originalState) > self.getCapsules(gameState)
        
        features["isPacman"] = 1 if gameState.getAgentState(self.index).isPacman else 0
        
        return features
    
    def realTimeFeature(self, gameState, originalState, depth):
        
        # features that represent a simulated game state
        features = util.Counter()
        features["score"] = self.getScore(gameState) - self.getScore(originalState)
        features["carry"] = gameState.getAgentState(self.index).numCarrying - originalState.getAgentState(self.index).numCarrying
        
        originalPosition = originalState.getAgentState(self.index).getPosition()
        simulatePosition = gameState.getAgentState(self.index).getPosition()
        agentState = originalState.getAgentState(self.index)
        if not agentState.isPacman and abs(originalPosition[0]-self.middle) > 1 and agentState.scaredTimer == 0:
            # if agent is ghost and not close enough to mid lane
            # do not penalize for death
            features["death"] = 0
        else:
            features["death"] = self.getMazeDistance(originalPosition, simulatePosition) > (self.steps + depth + 1)

        return features
    
    def defensiveFeature(self, gameState):
        
        # features for defense
        features = util.Counter()
        
        opponents = self.getOpponents(gameState)
        oppoStates = [gameState.getAgentState(i) for i in opponents]
        simulateInvaderNum = len([s for s in oppoStates if s.isPacman])
        myPos = gameState.getAgentState(self.index).getPosition()
        probMap = mapTool.probMap
        team = self.getTeam(gameState)

        if not oppoStates[0].isPacman and not oppoStates[1].isPacman:
            features["invaderDistance"] = -5
        elif self.invaderNum == 2 and simulateInvaderNum == 1:
            features["invaderDistance"] = 0
        else:
            if oppoStates[0].isPacman and oppoStates[1].isPacman:
                if self.index == team[0]:
                    features["invaderDistance"] = min([self.getMazeDistance(myPos, p) for p in probMap[opponents[0]]])
                else:
                    features["invaderDistance"] = min([self.getMazeDistance(myPos, p) for p in probMap[opponents[1]]])
            else:
                op = opponents[0] if oppoStates[0].isPacman else opponents[1]
                features["invaderDistance"] = min([self.getMazeDistance(myPos, p) for p in probMap[op]])
             
        features["myFood"] = len(self.getFoodYouAreDefending(gameState).asList())
        features["isGhost"] = 0 if gameState.getAgentState(self.index).isPacman else 1
        
        return features
    
    def homeDistance(self, gameState):
        
        if not gameState.getAgentState(self.index).isPacman:
            d = 0
        else:
            minDist = 9999
            myPos = gameState.getAgentPosition(self.index)
            walls = self.walls.asList()
            for i in range(self.size[1]):
                tempPos = (self.middle, i)
                if not tempPos in walls:
                    tempDist = self.getMazeDistance(myPos, tempPos)
                    minDist = min(minDist, tempDist)
            d = minDist
        
        return d

    def final(self, gameState):
        CaptureAgent.final(self, gameState)
        # save updated weights to file



    

  
