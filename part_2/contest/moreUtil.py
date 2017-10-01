from game import Actions
import json

tSetName = "train.json"
lSetName = "label.json"

def getLayoutSize(gameState):
    width = gameState.data.layout.width
    height = gameState.data.layout.height
    return width, height

def getHomeArea(gameState, isRed):
    width, height = getLayoutSize(gameState)
    return (0, width/2) if isRed else (width/2, width)

def getInvaderDist(agent, gameState):
    myState = gameState.getAgentState(agent.index)
    myPos = myState.getPosition()
    enemies = [gameState.getAgentState(i) for i in agent.getOpponents(gameState)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    dists = [agent.getMazeDistance(myPos, a.getPosition()) for a in invaders]
    if len(dists)==0 :
        dists = [0]
    return dists

def getHomeDist(tool,agent,gameState):
    middle = tool.middle
    bestv = 999999
    myState = gameState.getAgentState(agent.index)
    if not myState.isPacman: return 0
    pos1 = gameState.getAgentPosition(agent.index)
    walls = gameState.getWalls().asList()
    
    for i in range(16):
        pos2 = (middle,i)
        if not pos2 in walls:
            tempv = agent.getMazeDistance(pos1,pos2)
            bestv = min(bestv,tempv)
    
    return bestv
    
def isInvader(featruesTool,pos):
    return abs(pos[0]-featruesTool.start) < (featruesTool.size[0]/2-1)

def getGhostDist(agent, gameState):
    myState = gameState.getAgentState(agent.index)
    myPos = myState.getPosition()
    enemies = [gameState.getAgentState(i) for i in agent.getOpponents(gameState)]
    invaders = [a for a in enemies if (not a.isPacman) and a.getPosition() != None]
    dists = [agent.getMazeDistance(myPos, a.getPosition()) for a in invaders]
    if len(dists)==0 :
        dists = [0]

    return dists
    
def getGhostDistFeature(featruesTool,agent, successor,opp):
    allpos = featruesTool.probMap[opp]
    myState = successor.getAgentState(agent.index)
    myPos = myState.getPosition()
    minv = 999999
    
    for pos in allpos:
        if not isInvader(featruesTool,pos):
            minv = min(minv,agent.getMazeDistance(myPos, pos))
    return minv

def getInvaderDistFeature(featruesTool,agent, successor,opp):
    allpos = featruesTool.probMap[opp]
    myState = successor.getAgentState(agent.index)
    myPos = myState.getPosition()
    minv = 999999
    
    for pos in allpos:
        if isInvader(featruesTool,pos):
            minv = min(minv,agent.getMazeDistance(myPos, pos))
    return minv
    
#def getInvaderDistFeature(agent, nextState):
#    return min(getInvaderDist(agent, nextState))

def getInvaderNumFeature(agent, nextState):
    return len(getInvaderDist(agent, nextState))

def getHomeDistFeature(tool,agent, nextState):
    return getHomeDist(tool,agent, nextState)

#def getGhostDistFeature(agent, nextState):
#    return min(getGhostDist(agent, nextState))

def getFoodLeftFeature(agent, nextState):
    return len(agent.getFood(nextState).asList())

def getCarryFeature(agent):
    return agent.additionalState.carry[agent.index]

def getIsPacmanFeature(agent, nextState):
    myState = nextState.getAgentState(agent.index)
    return myState.isPacman

def closestFood(pos, food, walls):
    """
    closestFood -- this is similar to the function that we have
    worked on in the search project; here its all in one place
    """
    fringe = [(pos[0], pos[1], 0)]
    expanded = set()
    while fringe:
        pos_x, pos_y, dist = fringe.pop(0)
        if (pos_x, pos_y) in expanded:
            continue
        expanded.add((pos_x, pos_y))
        # if we find a food at this location then exit
        if food[pos_x][pos_y]:
            return dist
        # otherwise spread out from the location to its neighbours
        nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
        for nbr_x, nbr_y in nbrs:
            fringe.append((nbr_x, nbr_y, dist+1))
    # no food found
    return None

def saveSet(trainset,labelSet):
    saveFile(trainset,tSetName)
    saveFile(labelSet,lSetName)
    return 0
    
def getTrainSet(featrues):
    dict = ['invaderDist',
    'getHomeDist',
    'ghostDist',
    'isPacman',
    'foodLeft',
    'carry',
    'closest-food',
    'bias'
    ]
    temp = []
    for line in dict:
        temp.append(featrues[line])
    return temp
    
def saveFile(file,fileName):
    with open(fileName, "w") as f:
        json.dump(file,f,indent = 4)
        
def loadFile(fileName):
    with open(fileName) as f:
        return json.load(f)

def getClosestFoodFeature(agent, gameState, nextState):
    food = agent.getFood(gameState)
    walls = gameState.getWalls()
    next_x, next_y = nextState.getAgentPosition(agent.index)
    dist = closestFood((next_x, next_y), food, walls)
    #if dist is not None:
        # make the distance a number less than one otherwise the update
        # will diverge wildly
        #return float(dist ** 2) / (walls.width * walls.height)
    if dist == None : return 0
    return dist
        
def getFoodDists(agent, gameState):
    selfpos = gameState.getAgentPosition(agent.index)
    #print agent.getFood(gameState).asList()
    dists = [agent.getMazeDistance(selfpos,pos) for pos in agent.getFood(gameState).asList()]
    if len(dists)==0:
        dists = [999999]
    return dists
    
def getModSelf(tool,agent,features,gameState):
    #closestGhost = min(features['Ghost1Close'],Ghost1Close['Ghost2Close'])
        
    if features['HomeDist'] >0 and features['Carry']>0 and features['HomeDist']<features['ClostestFoodDist']:
        return 'backhome'
    
    if features['TeamFoodLeft']<=2:
        return 'backhome'
    
    if (features['HasGhost']>0):
        return "backhome"
    print (tool.team[0],agent.index)
       
    if features["HasInvader1"]>0 and agent.index == tool.team[0]:
        if features["IsPacman"]>0:
            return "backhome"
        return "defense1"
        
    if features["HasInvader2"]>0 and agent.index == tool.team[1]:
        if features["IsPacman"]>0:
            return "backhome"
        return "defense2"
        
    return "offense"





