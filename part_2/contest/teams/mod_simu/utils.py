import copy
import util
dirs = [(0,1),(0,-1),(1,0),(-1,0),(0,0)]


def expands(tool,poss,count):
    if count == 0:
        return []
    temp = copy.deepcopy(poss)
    for i in range(count):
        temp = tool.expand(temp)
    return temp
    
def expandSimu(tool,target,selfposs,agent,extrawalls):
    count = 0
    lastlen = 0
    if selfposs[0] in target: return 0
    while (not len(selfposs)==lastlen) and (len(selfposs)>0):
        count +=1
        lastlen = len(selfposs)
        selfposs = expand(tool,selfposs,extrawalls)
        for pos in target:
            if pos in selfposs:
                return count 
    return 99999
    
def eatFoodSimu(tool,agent,gameState,actions,extrawalls):
    allposs = []
    bestV = 999999
    bestaction = None
    for action in actions:
        allposs.append([gameState.generateSuccessor(agent.index,action).getAgentPosition(agent.index)])
    
    for i in range(len(allposs)):
        temp = expandSimu(tool,agent.getFood(gameState).asList(),allposs[i],agent,extrawalls)
        if temp < bestV:
            bestV = temp
            bestaction = actions[i]
    return bestaction,bestV
        
def killInvaderSimu(tool,agent,gameState,actions,extrawalls):
    allposs = []
    bestV = 999999
    bestaction = None
    area = getinvaderMap(tool,agent)
    for action in actions:
        tpos = gameState.generateSuccessor(agent.index,action).getAgentPosition(agent.index)
        if outofarea(tool,tpos):
            actions.remove(action)
            continue
        allposs.append([tpos])
    for i in range(len(allposs)):
        temp = expandSimu(tool,area,allposs[i],agent,extrawalls)
        if temp < bestV:
            bestV = temp
            bestaction = actions[i]
    return bestaction,bestV

def backHomeSimu(tool,agent,gameState,actions,extrawalls):
    allposs = []
    bestV = 999999
    bestaction = None
    area = tool.home
    print (11111)
    for action in actions:
        tpos = gameState.generateSuccessor(agent.index,action).getAgentPosition(agent.index)
        allposs.append([tpos])
        
    for i in range(len(allposs)):
        temp = expandSimu(tool,area,allposs[i],agent,extrawalls)
        if temp < bestV:
            bestV = temp
            bestaction = actions[i]
    return bestaction,bestV
    
def expand(tool,poss,extrawalls):
        temp = []
        nwalls = tool.walls.asList()+extrawalls
        for pos in poss:
            for dir in dirs:
                npos = (pos[0]+dir[0],pos[1]+dir[1])
                if (not npos in nwalls) and (npos not in temp):
                    temp.append(npos)
        return temp
        
def getinvaderMap(tool,agent):
    temp = []
    for i in tool.opp:
        map = tool.probMap[i]
        for pos in map:
            if (tool.athome(pos)) and (pos not in temp):
                temp.append(pos)

    if len(temp)==0:
        c = 999
        for i in tool.opp:
            map = tool.probMap[i]
            for pos in map:
                dist = abs(pos[0]-tool.middle)
                if dist<c:
                    c=dist
                    temp = []
                if (dist==c) and (pos not in temp):
                    temp.append(pos)
    agent.debugClear()
    agent.debugDraw(temp,[1,0,0])
    return temp
    
def outofarea(tool,pos):
    if abs(pos[0]-tool.start)<=15:
        return False
    return True
    
def p2s(agent,spos,set):
    dist = 999
    for pos in set:
        temp = agent.getMazeDistance(spos,pos)
        if temp <dist:
            dist = temp
    return dist
    
def obspos(tool,agent,gameState):
    temp = []
    for i in tool.opp:
        pos = gameState.getAgentPosition(tool.opp[0])
        if not pos == None:
            temp.append(pos)
    return temp