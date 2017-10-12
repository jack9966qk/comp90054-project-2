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

WEIGHTS = {"score": 1000, "myFood": 2, "opponentFood": -5, "numInvaders": -10,
           "death": -500, "distanceToFood": -10, "isPacman": 20, "carry": 100,
           "isGhost": 5, "invaderDistance": -10, "homeDist": -10}
debug = False
featuresTool = featuresTool.featuresTool(usemodel = False)
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
        self.steps = 3
        self.believePos = None
        featuresTool.initGame(self,gameState)
        
        '''
        Your initialization code goes here, if you need any.
        '''
        
        
    def chooseAction(self, gameState):
        
        # Pick Action
        opponentsPos = [gameState.getAgentPosition(i) for i in self.getOpponents(gameState) if gameState.getAgentPosition(i) != None]
        myPos = gameState.getAgentState(self.index).getPosition()
        enemySimulation = False
        for pos in opponentsPos:
            if self.getMazeDistance(myPos, pos) <= 5:
                enemySimulation = True
        
        evalFunc = "offensive"
        myFood = len(self.getFoodYouAreDefending(gameState).asList())
        if gameState.getAgentState(self.index).numCarrying >= 3:
            evalFunc = "backHome"
        elif myFood <= 15:
            evalFunc = "defensive"
        elif enemySimulation:
            evalFunc = "realTime"
#        print evalFunc, self.index
        
        rootNode = self.MCTS(gameState.deepCopy(), 20, evalFunc)
        children = rootNode.getChild()
        """
        for child in children:
            v = child.getTotalValue() / child.getVisits()
            print v, child.getVisits(), child.getGameState().getAgentState(self.index).getDirection()
        """
        choice = max(children, key = lambda x: x.getTotalValue() / x.getVisits())
#            print choice.getTotalValue()/choice.getVisits()
        action = choice.getGameState().getAgentState(self.index).getDirection()
        
        prevState = self.getPreviousObservation()
        if prevState == None: prevState = gameState
        featuresTool.update(self, prevState, gameState)
        
        if debug:
            self.debugClear()
            self.debugDraw(self.p, [0,1,1])
            util.pause()
        #util.pause()
        
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
#                        print myPos, opPos, minAct, "iteration", iteration
                        opState = state.deepCopy()
                        AgentRules.applyAction(opState, minAct, op)
                    else:
                        # else opponent choose action by minisizing our value
                        minScore = float("inf")
                        opState = None
                        l = []
                        for a in opLegalAction:
                            tempState = state.deepCopy()
                            AgentRules.applyAction(tempState, a, op)
                            tempScore = self.evaluateSimulation(tempState, state, evalFunc, 0)
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
            
            simulatedState = self.simulate(curr.getGameState())
            
            self.p.append(simulatedState.getAgentPosition(self.index))
            
            stateValue = self.evaluateSimulation(simulatedState, gameState, evalFunc, curr.getDepth())
            """
            states = [self.simulate(curr.getGameState()) for i in range(3)]
            values = [self.evaluateSimulation(s, gameState, evalFunc, curr.getDepth()) for s in states]
            stateValue = max(values)
            """
            if debug:
                if evalFunc == "realTime":
                    features = self.getRealTimeFeature(simulatedState, gameState, curr.getDepth())
                    s = "die" if features["death"] else "live"
                    test = curr
                    while test.getParent() != root:
                        test = test.getParent()
                    a = test.getGameState().getAgentState(self.index).getDirection()
                    p = simulatedState.getAgentPosition(self.index)
                    pp = test.getParent().getGameState().getAgentPosition(self.index)
                    v = self.evaluateSimulation(simulatedState, gameState, evalFunc, curr.getDepth())
                    print self.index, p, a, s, pp, "value", v, iteration
                elif evalFunc == "offensive":
                    features = self.offensiveFeature(simulatedState)
                    test = curr
                    while test.getParent() != root:
                        test = test.getParent()
                    a = test.getGameState().getAgentState(self.index).getDirection()
                    p = simulatedState.getAgentPosition(self.index)
                    v = self.evaluateSimulation(simulatedState, gameState, evalFunc, curr.getDepth())
                    print features, p, a, "value", v
            
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
        gamma = 1
        if node is not None:
            node.visit()
            node.updateValue(value * gamma)
            self.backprop(node.getParent(), value * gamma)
    
    def evaluateSimulation(self, gameState, originalState, evalFunc, depth):
        # evaluate the value for simulated state
        if evalFunc == "realTime":
            features = self.getRealTimeFeature(gameState, originalState, depth)
        elif evalFunc == "offensive":
            features = self.offensiveFeature(gameState)
        elif evalFunc == "defensive":
            features = self.defensiveFeature(gameState, originalState)
        elif evalFunc == "backHome":
            features = self.backHomeFeature(gameState, originalState, depth)
        weights = WEIGHTS
        return features * weights
    
    def getRealTimeFeature(self, gameState, originalState, depth):
        
        # features that represent a simulated game state
        features = util.Counter()
        features["score"] = self.getScore(gameState) - self.getScore(originalState)
        features["myFood"] = len(self.getFoodYouAreDefending(gameState).asList())
        features["carry"] = gameState.getAgentState(self.index).numCarrying - originalState.getAgentState(self.index).numCarrying
        
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        features["numInvaders"] = len(invaders)
        
        originalPosition = originalState.getAgentState(self.index).getPosition()
        simulatePosition = gameState.getAgentState(self.index).getPosition()
        features["death"] = self.getMazeDistance(originalPosition, simulatePosition) > (self.steps + depth + 1)
#        print depth
#        if features["death"]: print "die"
        
        return features
    
    def backHomeFeature(self, gameState, originalState, depth):
        
        features = util.Counter()
        originalPosition = originalState.getAgentState(self.index).getPosition()
        simulatePosition = gameState.getAgentState(self.index).getPosition()
        features["death"] = self.getMazeDistance(originalPosition, simulatePosition) > (self.steps + depth + 1)
        
        features["score"] = self.getScore(gameState) - self.getScore(originalState)
        
        if not gameState.getAgentState(self.index).isPacman:
            features["homeDist"] = 0
        else:
            minDist = 9999
            myPos = gameState.getAgentPosition(self.index)
            walls = self.walls.asList()
            for i in range(self.size[1]):
                tempPos = (self.middle, i)
                if not tempPos in walls:
                    tempDist = self.getMazeDistance(myPos, tempPos)
                    minDist = min(minDist, tempDist)
            features["homeDist"] = minDist
        
        return features
    
    def offensiveFeature(self, gameState):
        
        # features that decide where to move
        features = util.Counter()
        
        myPos = gameState.getAgentState(self.index).getPosition()
        distances = [self.getMazeDistance(myPos, food) for food in self.getFood(gameState).asList()]
        features["distanceToFood"] = min(distances) if len(distances) != 0 else 0
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



    

  
