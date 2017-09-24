from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
import fastDownwardAdapter

def getLayoutSize(gameState):
  width = gameState.data.layout.width
  height = gameState.data.layout.height
  return width, height

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

def makeEnvPredicates(gameState, isRed):
  width, height = getLayoutSize(gameState)
  # adjcent
  for x in range(width) - 1:
    s += "(adjcent posx-{} posx-{})\n".format(x, x+1)
  s += "\n"

  for y in range(height) - 1:
    s += "(adjcent posy-{} posy-{})\n".format(y, y+1)
  s += "\n"

  # same
  for x in range(width):
    s += "(same posx-{} posx-{})\n".format(x, x)
  s += "\n"

  for y in range(height):
    s += "(same posy-{} posy-{})\n".format(y, y)
  s += "\n"

  # wall
  for x in range(width):
    for y in range(height):
      if gameState.hasWall(x, y):
        s += "(wall-at posx-{} posy-{})\n".format(x, y)
  return s

def makeObjSection(gameState):
  width = gameState.data.layout.width
  height = gameState.data.layout.height
  xobjs = ["posx-{}".format(x) for x in range(width)]
  yobjs = ["posy-{}".format(y) for y in range(height)]
  return "(:objects\n" +
    "\n".join(xobjs) + "\n\n" +
    "\n".join(yobjs) + "\n)"

def makePacmanInitSection(gameState, isRed, foodPositions):
  s = "(:init\n"
  s += makeEnvPredicates(gameState, isRed)
  s += "\n"

  # home
  yLo, yHi = 0, width/2 if isRed else width/2, width
  for x in range(width):
    for y in range(yLo, yHi):
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
  food = getFoodPositions(gameState, isRed)
  for x in range(width):
    for y in range(height):
      if food[x][y]:
        
  s += "\n"
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

def makePacmanProblem(gameState, isRed, selfIdx, scaredIdx):
  foodPositions = getFoodPositions(gameState, isRed)
  return "(define (problem pacmanProblem) (:domain pacman)\n" +
    makeObjSection(gameState) + "\n\n" +
    makePacmanInitSection(gameState, isRed, foodPositions) + "\n\n" +
    makePacmanGoalSection(gameState, foodPositions) + "\n\n)"

def makeGhostInitSection(gameState, isRed, selfIdx):
  s = "(:init\n"
  s += makeEnvPredicates(gameState, isRed)
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
      s += "(pacman-at posx-{} posy-{})\n\n".format(pacx, pacy)
  s += "\n"

  # ghost
  ghx, ghy = gameState.getAgentPosition(selfIdx)
  s += "(ghost-at posx-{} posy-{})\n\n".format(ghx, ghy)

  return s

def makeGhostGoalSection(gameState):
  s = "(:goal\n"
  s += "(and\n"
  # no pacman left
  width, height = getLayoutSize(gameState)
  for x in range(width):
    for y in range(height):
      s += "(not (pacman-at posx-{} posy-{}))\n".format(x, y)
  s += ")\n)"
  return s

def makeGhostProblem(gameState, isRed, selfIdx):
  return "(define (problem ghostProblem) (:domain ghost)\n" +
    makeObjSection(gameState) + "\n\n" +
    makeGhostInitSection(gameState, isRed) + "\n\n" +
    makeGhostGoalSection(gameState) + "\n\n)"

def parseSolution(solution, actions):
  if solution:
      posx, posy = solution.strip("()").split()[-2:]
      nx, ny = posx[-1], posy[-1]
      x, y = gameState.getAgentPosition(self.index)
      action = None
      if nx == x + 1:
        action = "East"
      elif nx == x - 1:
        action = "West"
      elif ny == y + 1:
        action = "South"
      elif ny == y - 1:
        action = "North"
      if action in actions:
        return action
  print("WARNING: Solution not parsed successfully or not valid")
  return None

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
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

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
    # print(gameState)
    # exit()


  def chooseAction(self, gameState):
    """
    # TODO
    """
    actions = gameState.getLegalActions(self.index)

    problem = makePacmanProblem(
      gameState,
      gameState.isOnRedTeam(self.index),
      self.index,
      []) # TODO determine whether ghost scared
    
    solution = fastDownwardAdapter.plan("../../part_1/pacman.pddl", problem)

    action = parseSolution(solution, actions)
    if action: return action

    # fall back to random
    return random.choice(actions)

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


  def chooseAction(self, gameState):
    """
    # TODO
    """
    actions = gameState.getLegalActions(self.index)

    problem = makeGhostProblem(
      gameState,
      gameState.isOnRedTeam(self.index),
      self.index
    )
    
    solution = fastDownwardAdapter.plan("../../part_1/ghost.pddl", problem)

    action = parseSolution(solution, actions)
    if action: return action

    # fall back to random
    return random.choice(actions)

