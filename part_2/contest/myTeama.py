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
import moreUtil
import IOutil
import featuresTool

WEIGHTS_FILENAME = 'WeightsDict.json'
DICTS_FILENAME = 'Fdict.json'
MODS_FILENAME = 'ModDict.json'
featuresTool = featuresTool.featuresTool(usemodel = True)



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
        
        self.weightsDict = self.loadWeightDict()
        featuresTool.initGame(self,gameState)
        
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
        mod = self.getMod(sfeatures)
        weights = self.weightsDict[mod]
        return features * weights
        
        
    def chooseAction(self, gameState):
        # Pick Action
        
        actions = gameState.getLegalActions(self.index)
        actions.remove("Stop")
        values = [self.evaluate(gameState, a) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        
        
        action = random.choice(bestActions)
        features = featuresTool.getFeatures(self,gameState,action)
        self.lastAction = action
        sfeatures = featuresTool.getFeatures(self,gameState,"Stop")
        mod = self.getMod(sfeatures)
        
        print zip(actions, values)
        print mod
        print features
        print action
        
        #util.pause()
        return action
    
    def getMod(self,features):
        #closestGhost = min(features['Ghost1Close'],Ghost1Close['Ghost2Close'])
        if features['HomeDist'] >0 and features['Carry']>0 and features['HomeDist']<features['ClostestFoodDist']:
            return 'backhome'
        
        
        return "offense"
        

    def final(self, gameState):
        CaptureAgent.final(self, gameState)
        # save updated weights to file
        IOutil.saveFile(WEIGHTS_FILENAME,self.weightsDict)



    

  
