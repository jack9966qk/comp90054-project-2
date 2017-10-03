import moreUtil

def getIntermediaReward(agent, state, action, nextState):
    nx, ny = nextState.getAgentPosition(agent.index)
    x, y = state.getAgentPosition(agent.index)
    sum = 0
    
    team = agent.getTeam(state)
    teamDist = agent.getMazeDistance(state.getAgentPosition(team[0]), state.getAgentPosition(team[1]))
    
    if (abs(nx - x) + abs(ny - y)) > 1: # check death
        sum+= -50
        return sum
    
    #sum+= teamDist * 1
    
    if (nx, ny) == (x, y): # no move
        sum+= -10
    
    enemies = [state.getAgentState(i) for i in agent.getOpponents(state)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    positions = [a.getPosition() for a in invaders]
    if len(positions) > 0 and not state.getAgentState(agent.index).isPacman:
        for position in positions:
            if (nx, ny) == position: sum+= 50 # chase invaders
    
    #features = agent.getFeatures(state, action)
    carrys = state.getAgentState(agent.index).numCarrying
    sum+= -carrys*5
    if state.getAgentState(agent.index).isPacman and not nextState.getAgentState(agent.index).isPacman and carrys>0:#features['carry'] > 0:
        sum+= carrys**2 * 100+500#features['carry']**3 * 200
    
    isRed = state.isOnRedTeam(agent.index)
    food = state.getBlueFood() if isRed else state.getRedFood()
    capsule = state.getBlueCapsules() if isRed else state.getRedCapsules()
    if food[nx][ny]:
        sum+= 20 # eat food
    if (nx, ny) in capsule:
        sum+= 30 # eat capsule
    sum+= -1
    return sum

def getFinalReward(nextState):
    if nextState == "Tie": return -50
    elif nextState == "Win": return 100
    else: return -50

def getReward(agent, state, action, nextState):
    if type(nextState) is str:
        return getFinalReward(nextState)
    else:
        return getIntermediaReward(agent, state, action, nextState)