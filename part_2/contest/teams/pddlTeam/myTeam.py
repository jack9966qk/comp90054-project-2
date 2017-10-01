import os, sys
from captureAgents import CaptureAgent
import random, time, util
from game import Directions
from itertools import product
from capture import SIGHT_RANGE
import game

teamName = os.path.split(os.path.dirname(os.path.abspath(__file__)))[1]
dir = "teams/{}/".format(teamName)
sys.path.append(dir)

from moreUtil import getLayoutSize, getHomeArea
from additionalState import AdditionalState
from ffAdapter import plan

def getFoodPositions(gameState, isRed):
  width, height = getLayoutSize(gameState)
  if isRed:
    food = gameState.getBlueFood()
  else:
    food = gameState.getRedFood()
  positions = []
  for x in range(width):
    for y in range(height):
      if food[x][y]:
        positions.append((x, y))
  return positions

def makeEnvPredicates(gameState, isRed, posRange=None):
  if not posRange:
    width, height = getLayoutSize(gameState)
    posRange = (range(width), range(height))
  xRange, yRange = posRange

  s = ""
  # adjcent
  for x in list(xRange)[:-1]:
    s += "(adjcent posx-{} posx-{})\n".format(x, x+1)
  s += "\n"

  for y in list(yRange)[:-1]:
    s += "(adjcent posy-{} posy-{})\n".format(y, y+1)
  s += "\n"

  # same
  for x in xRange:
    s += "(same posx-{} posx-{})\n".format(x, x)
  s += "\n"

  for y in yRange:
    s += "(same posy-{} posy-{})\n".format(y, y)
  s += "\n"

  # wall
  for x, y in product(xRange, yRange):
    if gameState.hasWall(x, y):
      s += "(wall-at posx-{} posy-{})\n".format(x, y)
  return s

def makeObjSection(gameState, posRange=None):
  if not posRange:
    width, height = getLayoutSize(gameState)
    posRange = (range(width), range(height))
  xRange, yRange = posRange
  xobjs = ["posx-{}".format(x) for x in xRange]
  yobjs = ["posy-{}".format(y) for y in yRange]
  return "(:objects\n{}\n\n{}\n)".format(
    "\n".join(xobjs), "\n".join(yobjs))

def makePacmanInitSection(gameState, isRed, selfIdx, foodPositions, scaredIdx):
  s = "(:init\n"
  s += makeEnvPredicates(gameState, isRed)
  s += "\n"

  # home
  _, height = getLayoutSize(gameState)
  xLo, xHi = getHomeArea(gameState, isRed)
  for x in range(xLo, xHi):
    for y in range(height):
      s += "(is-home posx-{} posy-{})\n".format(x, y)
  s += "\n"
  
  # pacman
  pacx, pacy = gameState.getAgentPosition(selfIdx)
  s += "(pacman-at posx-{} posy-{})\n\n".format(pacx, pacy)

  # ghosts
  if isRed:
    ghostIndices = gameState.getBlueTeamIndices()
  else:
    ghostIndices = gameState.getRedTeamIndices()

  for i in ghostIndices:
    ghostPos = gameState.getAgentPosition(i)
    if ghostPos:
      ghx, ghy = ghostPos
      if i in scaredIdx:
        s += "(scared-ghost-at posx-{} posy-{})\n\n".format(ghx, ghy)
      else:
        s += "(ghost-at posx-{} posy-{})\n\n".format(ghx, ghy)

  # food
  for x, y in foodPositions:
    s += "(food-at posx-{} posy-{})\n".format(x, y)
  s += "\n"
  s += ")"
  return s

def makePacmanGoalSection(gameState, foodPositions):
  s = "(:goal\n"
  s += "(and\n"
  # no food left
  for x, y in foodPositions:
    s += "(not (food-at posx-{} posy-{}))\n".format(x, y)
  s += "\n"
  # back to home
  s += "(at-home)\n"
  s += ")\n)"
  return s

def makePacmanProblem(gameState, isRed, selfIdx, scaredIdx, foodPositions):
  return "(define (problem pacmanProblem) (:domain pacman)\n" + \
    makeObjSection(gameState) + "\n\n" + \
    makePacmanInitSection(gameState, isRed, selfIdx,
      foodPositions, scaredIdx) + "\n\n" + \
    makePacmanGoalSection(gameState, foodPositions) + "\n\n)"

def makeGhostInitSection(gameState, isRed, selfIdx, posRange):
  s = "(:init\n"
  s += makeEnvPredicates(gameState, isRed, posRange)
  s += "\n"
  
  # pacmans
  if isRed:
    pacmanIndices = gameState.getBlueTeamIndices()
  else:
    pacmanIndices = gameState.getRedTeamIndices()
  pacx, pacy = gameState.getAgentPosition(selfIdx)
  for i in pacmanIndices:
    pacmanPos = gameState.getAgentPosition(i)
    if pacmanPos:
      pacx, pacy = pacmanPos
      if pacx in posRange[0] and pacy in posRange[1]:
        s += "(pacman-at posx-{} posy-{})\n\n".format(pacx, pacy)
  s += "\n"

  # ghost
  ghx, ghy = gameState.getAgentPosition(selfIdx)
  if ghx in posRange[0] and ghy in posRange[1]:
    s += "(ghost-at posx-{} posy-{})\n\n".format(ghx, ghy)

  s += ")"
  return s

def makeGhostGoalSection(gameState, standbyPos, posRange):
  s = "(:goal\n"
  s += "(and\n"
  # no pacman left
  for x, y in product(posRange[0], posRange[1]):
    s += "(not (pacman-at posx-{} posy-{}))\n".format(x, y)
  # standbyPos
  posX, posY = standbyPos
  s += "(ghost-at posx-{} posy-{})\n".format(posX, posY)
  s += ")\n)"
  return s

def makeGhostProblem(gameState, isRed, selfIdx, standbyPos, posRange):
  return "(define (problem ghostProblem) (:domain ghost)\n" + \
    makeObjSection(gameState, posRange=posRange) + "\n\n" + \
    makeGhostInitSection(gameState, isRed, selfIdx, posRange) + "\n\n" + \
    makeGhostGoalSection(gameState, standbyPos, posRange) + "\n\n)"

def parseSolution(solution, actions, x, y):
  if solution:
    print(solution[0])
    posx, posy = solution[0].strip().strip("()").split()[-2:]
    nx_str, ny_str = (posx.split("-")[-1], posy.split("-")[-1])
    if nx_str.isdigit() and ny_str.isdigit():
      nx, ny = int(nx_str), int(ny_str)
      print(nx, ny)
      print(x, y)
      print(actions)
      action = None
      if nx == x + 1:
        action = "East"
      elif nx == x - 1:
        action = "West"
      elif ny == y + 1:
        action = "North"
      elif ny == y - 1:
        action = "South"
      print(action)
      if action in actions:
        return action
  print("WARNING: Solution not parsed successfully or not valid")
  # exit()
  return None

def drawSight(gameState, selfPos, drawFunc):
  width, height = getLayoutSize(gameState)
  visiblePositions = [pos for pos in product(range(width), range(height))
    if abs(pos[0] - selfPos[0]) + abs(pos[1] - selfPos[1]) <= SIGHT_RANGE
  ]
  drawFunc(visiblePositions, [1, 0, 0], clear=True)
  drawFunc([selfPos], [0, 0, 1])

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'PddlOffenseAgent', second = 'PddlDefenseAgent'):
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

EATCAP = "eatcap"
RETURN = "return"

class PddlOffenseAgent(CaptureAgent):
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
    # self.state = EATCAP
    # self.carry = 0

  # def updateState(self, gameState):
  #   # x, _ = gameState.getAgentPosition(self.index)
  #   # xLo, xHi = getHomeArea(gameState, gameState.isOnRedTeam(self.index))
  #   # if xLo <= x < xHi:
  #   #   self.carry = 0
  #   if self.carry > 5:
  #     self.state = RETURN
  #   else:
  #     self.state = EATCAP

  def setAdditionalState(self, additionalState):
    self.additionalState = additionalState

  def shouldReturn(self):
    return self.additionalState.carry[self.index] >= 5

  def chooseAction(self, gameState):
    """
    # TODO
    """
    # if failed fall back to random
    actions = gameState.getLegalActions(self.index)
    action = random.choice(actions)
    
    selfPos = gameState.getAgentPosition(self.index)
    # drawSight(gameState, selfPos, self.debugDraw)


    isRed = gameState.isOnRedTeam(self.index)
    
    if self.shouldReturn():
      foodPositions = []
    else:
      foodPositions = getFoodPositions(gameState, isRed)
      # limit num of food considered
      foodPositions = sorted(foodPositions, key=lambda p: self.distancer.getDistance(selfPos, p))
      foodPositions = foodPositions[:5]

    problem = makePacmanProblem(
      gameState,
      isRed,
      self.index,
      [], # TODO determine whether ghost scared
      foodPositions)
    
    solution = plan(dir + "pacman.pddl", problem)

    x, y = gameState.getAgentPosition(self.index)
    act = parseSolution(solution, actions, x, y)
    if act: action = act
    self.additionalState.update(gameState, self.index, action)
    return action

class PddlDefenseAgent(CaptureAgent):
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

    # get 'centre' of home area
    _, height = getLayoutSize(gameState)
    xLo, xHi = getHomeArea(gameState, gameState.isOnRedTeam(self.index))
    validPositions = [(x, y) for x, y
      in product(range(xLo, xHi), range(height))
      if not gameState.hasWall(x, y)]
    def getEccentricity(pos):
      return max([self.distancer.getDistance(pos, p) for p in validPositions])
    self.centre = min(validPositions, key=getEccentricity)
    self.homeRange = (range(xLo, xHi), range(height))

  def setAdditionalState(self, additionalState):
    self.additionalState = additionalState

  def chooseAction(self, gameState):
    """
    # TODO
    """
    # selfPos = gameState.getAgentPosition(self.index)
    # drawSight(gameState, selfPos, self.debugDraw)
    

    # if failed fall back to random
    actions = gameState.getLegalActions(self.index)
    action = random.choice(actions)

    actions = gameState.getLegalActions(self.index)

    problem = makeGhostProblem(
      gameState,
      gameState.isOnRedTeam(self.index),
      self.index,
      self.centre,
      self.homeRange
    )
    
    solution = plan(dir + "ghost.pddl", problem)

    x, y = gameState.getAgentPosition(self.index)
    act = parseSolution(solution, actions, x, y)
    if act: action = act
    self.additionalState.update(gameState, self.index, action)
    return action

