
def getIntermediaReward(agent, state, action, nextState):
    nx, ny = nextState.getAgentPosition(agent.index)
    x, y = state.getAgentPosition(agent.index)
    
    if (abs(nx - x) + abs(ny - y)) > 1: # check death
        return -100
    
    if (nx, ny) == (x, y): # no move
        return -5
    
    enemies = [state.getAgentState(i) for i in agent.getOpponents(state)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    positions = [a.getPosition() for a in invaders]
    if len(positions) > 0 and not state.getAgentState(agent.index).isPacman:
        for position in positions:
            if (nx, ny) == position: return 50 # chase invaders
    
    features = agent.getFeatures(state, action)
    if state.getAgentState(agent.index).isPacman and not nextState.getAgentState(agent.index).isPacman and features['carry'] > 0:
        return features['carry']**3 * 20000
    
    isRed = state.isOnRedTeam(agent.index)
    food = state.getBlueFood() if isRed else state.getRedFood()
    capsule = state.getBlueCapsules() if isRed else state.getRedCapsules()
    if food[nx][ny]:
        return 1000 # eat food
    if (nx, ny) in capsule:
        return 3 # eat capsule
    return -1

def getFinalReward(nextState):
    if nextState == "Tie": return -50
    elif nextState == "Win": return 100
    else: return -100

def getReward(agent, state, action, nextState):
    if type(nextState) is str:
        return getFinalReward(nextState)
    else:
        return getIntermediaReward(agent, state, action, nextState)