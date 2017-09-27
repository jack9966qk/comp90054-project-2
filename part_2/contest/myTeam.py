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
from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
import json
import math
weightFile = "weight.json"
dirdict = {Directions.NORTH: (0, 1),
Directions.SOUTH: (0, -1),
Directions.EAST:  (1, 0),
Directions.WEST:  (-1, 0)}

dirs = [(0,1),(0,-1),(1,0),(-1,0),(0,0)]

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
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    '''
    Your initialization code goes here, if you need any.
    '''

    fo = open(weightFile,"r")
    self.weightDict = json.load(fo)
    fo.close()
    
    self.probMap = []
    self.probMap.append(util.Counter())
    self.probMap.append(util.Counter())
    
    self.walls = gameState.getWalls()
    self.size = (self.walls.width,self.walls.height)
    
    size = self.size

    
    
    #util.pause()
    self.discount = 0.9
    self.roundcount = 0
    self.middle = int(math.floor(self.start[0])/16+15)
    self.patrol = [(self.middle,7),(self.middle,8)]
    
    self.distancer.getMazeDistances()
    mazeAction = {}
    self.allpos = []
    self.allfood = []
    foodList = self.getFood(gameState).asList()
    self.map = {}
    self.mapMST = {}
    self.maxMST = self.getMST(foodList)
    
    for i in range(size[0]):
        for j in range(size[1]):
            
            if not self.walls[i][j]:
                self.allpos.append((i,j))
    
    for pos in self.allpos:
        self.probMap[0][pos]=0
        self.probMap[1][pos]=0
    
    opp = self.getOpponents(gameState)
    
    self.probMap[0][gameState.getInitialAgentPosition(opp[0])]=1.0
    self.probMap[1][gameState.getInitialAgentPosition(opp[1])]=1.0
    
    #print self.size
    #print self.allpos
    #print self.start
    util.pause()
    
    #os.system('PAUSE')
    
  def getProbMap(self,gameState):
    opp=self.getOpponents(gameState)
    selfpos = gameState.getAgentPosition(self.index)
    noisyDist = gameState.getAgentDistances()
    for i in range(2):
        tempP = self.iniProbMap(self.allpos)
        prevP = self.probMap[i]
        for pos in self.allpos:
            if prevP[pos]>0:
                temp = prevP[pos]
                tcount = 0
                tpos = []
                for dir in dirs:
                    pos1 = (pos[0]+dir[0],pos[1]+dir[1])
                    if pos1 in self.allpos:
                        tcount+=1
                        tpos.append(pos1)
                for npos in tpos:
                    tempP[npos]+= temp / tcount
        sum=0
        for pos in self.allpos:
            trueD = util.manhattanDistance(selfpos,pos)
            tempP[pos] *= gameState.getDistanceProb(trueD,noisyDist[opp[i]])
            
            sum+=tempP[pos]
        if sum==0: 
            sum=1
            tempP = self.iniProbMap(self.allpos)
            tempP[gameState.getInitialAgentPosition(opp[i])]=1
        poso = gameState.getAgentPosition(opp[i])
        if not poso == None:
            sum=1
            tempP = self.iniProbMap(self.allpos)
            tempP[poso]=1
        for pos in self.allpos:
            tempP[pos] /= sum
        self.probMap[i]=tempP
    
    return 0
  
  def iniProbMap(self,allpos):
    temp = util.Counter()
    for pos in allpos:
        temp[pos]=0
    return temp
  
  def drawProbMape(self,gameState):
    self.debugClear()
    for pos in self.allpos:
        self.debugDraw([pos],[self.probMap[0][pos],self.probMap[1][pos],0])
    return 0
  
  def getDistance(self,pos1,pos2):
    if self.map.has_key((pos1,pos2)) or self.map.has_key((pos2,pos1)):
        return self.map[(pos1,pos2)]
    else:
        temp = self.getMazeDistance(pos1,pos2)
        self.map[(pos1,pos2)] = temp
        self.map[(pos2,pos1)] = temp
        return temp
  
  def getMST(self,foodList):
    foodList = tuple(foodList)
    if self.mapMST.has_key(foodList):
        return self.mapMST[foodList]
    else:
        temp = 0
        closeL = [foodList[0]]
        openL = foodList[1:]
        for food1 in openL:
            tempv = 99999999
            tempf = None
            for food2 in closeL:
                tempd = self.getDistance(food1,food2)
                if tempd<tempv:
                    tempv = tempd
                    tempf = food2
            temp+=tempv
            closeL.append(tempf)
        self.mapMST[foodList] = temp
        return temp
  
  
  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    return successor
  
  def evaluate(self,gameState,action):
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights
    
  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)
    
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]
    
    print [self.getMod(gameState)]
    print zip(actions, values)
    print gameState.getAgentDistances()
    self.getProbMap(gameState)
    self.drawProbMape(gameState)
    util.pause()

    return random.choice(bestActions)

    '''
    You should change this in your own agent.
    '''
    return random.choice(actions)

    
  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    self.roundcount+=1
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    myState = successor.getAgentState(self.index)
    features["isPacman"] = myState.isPacman
    features["invaderDist"] = min(self.getInvadersDist(successor))
    features["invaderNum"] = len(self.getInvadersDist(successor))
    features["ghostDist"] = min(self.getGhostDist(successor))<4
    features["home"] = self.getDistance(self.start,successor.getAgentPosition(self.index))
    #features["getHomeDist"] = self.getHomeDist(successor)
    features['food'] = self.getFoodValue(successor)
    features['foodLeft'] = len(self.getFood(successor).asList())
    features['isStop'] = action == "Stop"
    features['isNear'] = max([5-self.getTeamDist(successor),0])
    #features['isNear'] = 100/(self.getTeamDist(successor)+0.000001)
    features['patrol'] = self.getPatrolDist(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    mod = self.getMod(gameState)
    dict = self.weightDict[mod]
    
    return dict
    
  def getFoodValue(self,gameState):
    foodList = self.getFood(gameState).asList()
    pos1 = gameState.getAgentPosition(self.index)
    foodDist = [self.getDistance(pos1,pos2) for pos2 in foodList]
    
    return min(foodDist)
    
  def getInvadersDist(self,gameState):
    myState = gameState.getAgentState(self.index)
    myPos = myState.getPosition()
    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    dists = [self.getDistance(myPos, a.getPosition()) for a in invaders]
    if len(dists)==0 :
        dists = [0]
    
    return dists
   
  def getGhostDist(self,gameState):
    myState = gameState.getAgentState(self.index)
    myPos = myState.getPosition()
    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    invaders = [a for a in enemies if (not a.isPacman) and a.getPosition() != None]
    dists = [self.getDistance(myPos, a.getPosition()) for a in invaders]
    if len(dists)==0 :
        dists = [0]
    
    return dists
  
  def getTeamDist(self,gameState):
    team = self.getTeam(gameState)
    temp = 0
    pos1 = gameState.getAgentPosition(team[0])
    pos2 = gameState.getAgentPosition(team[1])
    dist = self.getDistance(pos1,pos2)
    if self.roundcount<200: return 12
    return dist
    
  def getPatrolDist(self,gameState):
    temp = 0
    for pos in self.patrol:
        temp+=self.getDistance(pos,gameState.getAgentPosition(self.index))
    return temp
  
  def getHomeDist(self,gameState):
    middle = self.middle
    bestv = 999999
    pos1 = gameState.getAgentPosition(self.index)
    walls = gameState.getWalls().asList()
    for i in range(16):
        pos2 = (middle,i)
        if not pos2 in walls:
            tempv = self.getDistance(pos1,pos2)
            bestv = min(bestv,tempv)
    return bestv
  
  def getMod(self,gameState):
    myState = gameState.getAgentState(self.index)
    pos1 = gameState.getAgentPosition(self.index)
    opps = self.getOpponents(gameState)
    temp = "offense"
    if self.getTeam(gameState)[0] == self.index: 
        temp = "patrol"
    if len(self.getFood(gameState).asList()) < 3:
        temp = "backhome"
    #if self.getHomeDist(gameState)<self.getFoodValue(gameState) and abs(pos1[0]-self.start[0])>15:
    #    temp = "backhome"
    
    obs = False
    dist = []
    for opp in opps:
        pos2 = gameState.getAgentPosition(opp)
        if not pos2 == None:
            obs = True
            dist.append(self.getDistance(pos1,pos2))
    if obs == True and min(dist)<4:
        if not myState.isPacman:
            temp = "defense"
        else:
            temp = "backhome"
            
    return temp
    return "patrol"
    return "offense"
    return "backhome"
    return "defense"
