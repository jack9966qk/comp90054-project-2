# Food

def getFoodList(agent, gameState):
    return agent.getFood(gameState).asList()

def getFoodDefList(agent, gameState):
    return agent.getFoodYouAreDefending(gameState).asList()

def getFoodDists(agent, gameState):
    pos = gameState.getAgentPosition(agent.index)
    foods = getFoodList(agent, gameState)
    dists = [agent.getMazeDistance(pos, p) for p in foods]
    return [999999] if not dists else dists

def getFoodLeft(agent, gameState):
    return len(getFoodList(agent, gameState))

def getFoodDefDists(agent, gameState):
    pos = gameState.getAgentPosition(agent.index)
    foods = getFoodDefList(agent, gameState)
    dists = [agent.getMazeDistance(pos, p) for p in foods]
    return [999999] if not dists else dists

def getFoodDefLeft(agent, gameState):
    return len(getFoodDefList(agent, gameState))

def getClosestFoodDist(agent, gameState):
    return min(getFoodDists(agent, gameState))

def getNumFoodLeft(agent, gameState):
    return len(getFoodList(agent, gameState))

# Agents

def getLayoutSize(gameState):
    width = gameState.data.layout.width
    height = gameState.data.layout.height
    return width, height

def getHomeArea(agent, gameState):
    width, _ = getLayoutSize(gameState)
    return (0, width/2) if agent.red else (width/2, width)

def getTeammateIndices(agent, gameState):
    teamIndices = agent.getTeam(gameState)
    teamIndices.remove(agent.index)
    return teamIndices

def getClosestTeammateDist(agent, gameState):
    pos = gameState.getAgentPosition(agent.index)
    teammates = [gameState.getAgentPosition(i)
        for i in getTeammateIndices(agent, gameState)]
    dists = [agent.getMazeDistance(pos, p) if p else 999999 for p in teammates]
    return min(dists)

def getOpponentPositions(agent, gameState):
    opponents = [gameState.getAgentPosition(i)
        for i in agent.getOpponents(gameState)]
    opponents = [p for p in opponents if p != None]
    return opponents

def getClosestGhostDist(agent, gameState):
    pos = gameState.getAgentPosition(agent.index)
    opponents = getOpponentPositions(agent, gameState)
    wLo, wHi = getHomeArea(agent, gameState)
    opponents = [(x, y) for (x, y) in opponents if not (wLo <= x <= wHi)]
    dists = [agent.getMazeDistance(pos, p) for p in opponents]
    return min(dists) if dists else 999999

def getClosestInvaderDist(agent, gameState):
    pos = gameState.getAgentPosition(agent.index)
    opponents = getOpponentPositions(agent, gameState)
    wLo, wHi = getHomeArea(agent, gameState)
    opponents = [(x, y) for (x, y) in opponents if wLo <= x <= wHi]
    dists = [agent.getMazeDistance(pos, p) for p in opponents]
    return min(dists) if dists else 999999

def getTotalGhostDist(agent, gameState):
    pos = gameState.getAgentPosition(agent.index)
    opponents = getOpponentPositions(agent, gameState)
    wLo, wHi = getHomeArea(agent, gameState)
    opponents = [(x, y) for (x, y) in opponents if not (wLo <= x <= wHi)]
    dists = [agent.getMazeDistance(pos, p) for p in opponents]
    return sum(dists) if dists else 999999

# home and carry

def getHomeDist(agent, gameState):
    pos = gameState.getAgentPosition(agent.index)
    walls = gameState.getWalls()
    _, height = getLayoutSize(gameState)
    wLo, wHi = getHomeArea(agent, gameState)
    if wLo <= pos[0] < wHi: return 0
    borderPositions = [(wLo, y) for y in range(height)] + \
                      [(wHi, y) for y in range(height)]
    borderPositions = [(x, y) for (x, y) in borderPositions if not walls[x][y]]
    dists = [agent.getMazeDistance(pos, p) for p in borderPositions]
    return min(dists) if dists else 999999

def getCarry(agent, gameState):
    return gameState.getAgentState(agent.index).numCarrying

def getFeatures(agent, gameState):
    return [
        getCarry(agent, gameState),
        getClosestFoodDist(agent, gameState),
        getClosestInvaderDist(agent, gameState),
        getClosestGhostDist(agent, gameState),
        getNumFoodLeft(agent, gameState),
        getHomeDist(agent, gameState)
    ]