import copy
import util
import random
dirs = [(0,1),(0,-1),(1,0),(-1,0),(0,0)]


def expands(tool,poss,count):
    if count == 0:
        return []
    temp = copy.deepcopy(poss)
    for i in range(count):
        temp = tool.expand(temp)
    return temp
    
def expandSimu(tool,target,selfposs,oppposs,agent,extrawalls):
    count = 0
    lastlen = 0
    if selfposs[0] in target: return 0
    oppposs = getSetBest(tool,agent,selfposs,oppposs)
    oppposs = [expand(tool,each,[]) for each in oppposs]
    selfposs = [each for each in selfposs if each not in oppposs[0]]
    selfposs = [each for each in selfposs if each not in oppposs[1]]
    while (not len(selfposs)==lastlen) and (len(selfposs)>0):
        count +=1
        lastlen = len(selfposs)
        selfposs = expand(tool,selfposs,extrawalls+oppposs[0]+oppposs[1])
        oppposs = getSetBest(tool,agent,selfposs,oppposs)
        oppposs = [expand(tool,each,[]) for each in oppposs]
        selfposs = [each for each in selfposs if each not in oppposs[0]]
        selfposs = [each for each in selfposs if each not in oppposs[1]]
        for pos in target:
            if pos in selfposs:
                return count 
    return 99999
    
def eatFoodSimu(tool,agent,gameState,actions,extrawalls):
    allposs = []
    bestV = 999999
    bestaction = None
    oppposs = [tool.probMap[i] for i in tool.opp]
    for action in actions:
        allposs.append([gameState.generateSuccessor(agent.index,action).getAgentPosition(agent.index)])
    
    for i in range(len(allposs)):
        temp = expandSimu(tool,agent.getFood(gameState).asList(),allposs[i],oppposs,agent,extrawalls)
        if temp < bestV:
            bestV = temp
            bestaction = actions[i]
    return bestaction,bestV
        
def killInvaderSimu(tool,agent,gameState,actions,extrawalls):
    allposs = []
    bestV = 999999
    bestaction = None
    area = getinvaderMap(tool,agent)
    oppposs = [tool.probMap[i] for i in tool.opp]
    for action in actions:
        tpos = gameState.generateSuccessor(agent.index,action).getAgentPosition(agent.index)
        if outofarea(tool,tpos):
            actions.remove(action)
            continue
        allposs.append([tpos])
    for i in range(len(allposs)):
        temp = expandSimu(tool,area,allposs[i],oppposs,agent,extrawalls)
        if temp < bestV:
            bestV = temp
            bestaction = actions[i]
    return bestaction,bestV

def backHomeSimu(tool,agent,gameState,actions,extrawalls):
    allposs = []
    bestV = 999999
    bestaction = None
    area = tool.home
    oppposs = [tool.probMap[i] for i in tool.opp]
    for action in actions:
        tpos = gameState.generateSuccessor(agent.index,action).getAgentPosition(agent.index)
        allposs.append([tpos])
        
    for i in range(len(allposs)):
        temp = expandSimu(tool,area,allposs[i],oppposs,agent,extrawalls)
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
    #agent.debugClear()
    #agent.debugDraw(temp,[1,0,0])
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

def getSetBest(tool,agent,selfposs,oppposs):
    nposs = []
    for map in oppposs:
        bestV = 99999
        bestp = []
        for pos in map:
            temp = p2s(agent,pos,selfposs)
            if temp < bestV:
                bestV = temp
                bestp = []
            if temp == bestV:
                bestp.append(pos)
        if len(bestp)>0:
            bestp = [random.choice(bestp)]
        nposs.append(bestp)
    return nposs