from captureAgents import CaptureAgent
import random, time, util
from game import Directions, Actions
import game
import os
from weightIO import *
import moreUtil
from additionalState import AdditionalState

WEIGHTS_FILENAME = "trainedWeights.pickle"
trainSet = []
labelSet = []

# read from file if exist
if os.path.exists(WEIGHTS_FILENAME):
    WEIGHTS = loadWeightsJson(WEIGHTS_FILENAME)
else:
    WEIGHTS = util.Counter()

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'RlAgent', second = 'DummyAgent'):
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

class RlAgent(CaptureAgent):
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
        pass
        '''
        Your initialization code goes here, if you need any.
        '''

        
        
    def chooseAction(self, gameState):
        # Pick Action
        pass

    def final(self, gameState):
        CaptureAgent.final(self, gameState)