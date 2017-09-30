import moreUtil

def getIntermediaReward(agent, state, action, nextState):
    nx, ny = nextState.getAgentPosition(agent.index)
    x, y = state.getAgentPosition(agent.index)
    sum = 0
    
    
    
    if (abs(nx - x) + abs(ny - y)) > 1: # check death
        sum+= -100
    
    if (nx, ny) == (x, y): # no move
        sum+= -5000000
    
    enemies = [state.getAgentState(i) for i in agent.getOpponents(state)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    positions = [a.getPosition() for a in invaders]
    if len(positions) > 0 and not state.getAgentState(agent.index).isPacman:
        for position in positions:
            if (nx, ny) == position: sum+= 100 # chase invaders
    
    features = agent.getFeatures(state, action)
    carrys = state.getAgentState(agent.index).numCarrying
    if state.getAgentState(agent.index).isPacman and not nextState.getAgentState(agent.index).isPacman and carrys>0:#features['carry'] > 0:
        sum+= carrys**3 * 1000#features['carry']**3 * 200
    
    isRed = state.isOnRedTeam(agent.index)
    food = state.getBlueFood() if isRed else state.getRedFood()
    capsule = state.getBlueCapsules() if isRed else state.getRedCapsules()
    if food[nx][ny]:
        sum+= 100 # eat food
    if (nx, ny) in capsule:
        sum+= 300 # eat capsule
    sum+= -1
    return sum

def getFinalReward(nextState):
    if nextState == "Tie": return -5000
    elif nextState == "Win": return 10000
    else: return -5000

def getReward(agent, state, action, nextState):
    if type(nextState) is str:
        return getFinalReward(nextState)
    else:
        return getIntermediaReward(agent, state, action, nextState)