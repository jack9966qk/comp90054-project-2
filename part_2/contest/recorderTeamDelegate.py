from captureAgents import CaptureAgent
from baselineTeam import OffensiveReflexAgent, DefensiveReflexAgent
import random, time, util
from game import Directions, Actions
import game
import os
import cPickle

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               replayFile=None):
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
  firstAgent = RecorderAgent()
  secondAgent = RecorderAgent()
  firstAgent.baseAgent = OffensiveReflexAgent(firstIndex)
  secondAgent.baseAgent = DefensiveReflexAgent(secondIndex)
  return [firstAgent, secondAgent]

##########
# Agents #
##########

class RecorderAgent(object):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at baselineTeam.py for more details about how to
    create an agent as this is the bare minimum.
    """
    def __getattr__(self, item):
        print(item)
        if item in self.__dict__: # some overridden
            return self.__dict__[item] 
        else:
            return getattr(self.baseAgent, item) # redirection

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

        '''
        Your initialization code goes here, if you need any.
        '''
        self.baseAgent.registerInitialState(gameState)
        self.lastAction = None
        self.lastObservation = None
        self.record = []

    def chooseAction(self, gameState):
        if self.lastAction and self.lastObservation:
            self.record.append((self.lastObservation, self.lastAction, gameState))
        action = self.baseAgent.chooseAction(gameState)
        self.lastAction = action
        self.lastObservation = gameState
        print("return action " + str(action))
        return action

    def final(self, gameState):
        if self.lastAction and self.lastObservation:
            self.record.append((self.lastObservation, self.lastAction, gameState))
        self.baseAgent.final(gameState)
        with open("agent-{}-record.cpickle".format(self.index), 'w') as f:
            cPickle.dump(self.record, f)
