import copy
import featuresTool
import util

def backCheck(tool,agent,gameState,action):
    oppMap = [copy.deepcopy(tool.probMap[i]) for i in tool.opp]
    sposs = [gameState.generateSuccessor(agent.index,action).getAgentPosition(agent.index)]
    #print oppMap
    #print sposs
    for i in range(len(oppMap)):
        if len(oppMap[i])>1:
            oppMap[i]=[]
    #print sposs
    #util.pause()
    if athome(tool,sposs):
        return action
    res = simu(tool,oppMap,sposs,agent,gameState)
    count = 0
    #print 1111111
    #util.pause()
    if res>0:
        return action
    #util.pause()
    actions = gameState.getLegalActions(agent.index)
    #actions.remove(action)
    bestaction = action
    bestvalue = 99999
    for taction in actions:
        sposs = [gameState.generateSuccessor(agent.index,taction).getAgentPosition(agent.index)]
        res = simu(tool,oppMap,sposs,agent,gameState)
        #print (taction,res)
        if (res<bestvalue) and res>0:
            bestaction = taction
            bestvalue = res
    return bestaction
    
def deletepos(defence,offence):
    temp = []
    for pos in offence:
        if not pos in defence:
            temp.append(pos)
    return temp

def catchbest(tool,oppMap,sposs,agent):
    if len(sposs)==0: return oppMap
    for i in range(len(oppMap)):
        map = oppMap[i]
        spos = sposs[0]
        bestcV = 99999
        bestcpos = []
        for pos in map:
            dist = agent.getMazeDistance(pos,spos)
            if dist < bestcV:
                bestcV = dist
                bestcpos = [pos]
        oppMap[i] = bestcpos
    return oppMap

def athome(tool,poss):
    #print poss
    #print tool.start
    for pos in poss:
        if abs(pos[0]-tool.start)<=15:
            return True
    return False
    
def simu(tool,oppMap,orisposs,agent,gameState):
    sposs = copy.deepcopy(orisposs)
    Maps = copy.deepcopy(oppMap)
    count = 0
    #print len(sposs)
    #print athome(tool,sposs)
    #util.pause()
    while len(sposs)>0 and (not athome(tool,sposs)):
        #print 1
        #util.pause()
        for i in range(len(Maps)):
            map = Maps[i]
            map = tool.expand(map)
            sposs = deletepos(map,sposs)
            Maps[i] = map
        sposs = tool.expand(sposs)
        count +=1
        sposs,_ = homebest(tool,sposs,agent)
        oppMap = catchbest(tool,oppMap,sposs,agent)
        #draw(oppMap,sposs,agent)
    if len(sposs) == 0:
        return -1
    
    return count
    

        
def draw(oppMap,sposs,agent):
    agent.debugClear()
    agent.debugDraw(oppMap[0],[1,0,0])
    agent.debugDraw(oppMap[1],[0,1,0])
    agent.debugDraw(sposs,[0,0,1])
        
def homebest(tool,poss,agent):
    besthpos = []
    besthV = 99999
    for pos in poss:
        for i in range(tool.size[1]):
            hpos = (tool.middle,i)
            if not tool.walls[hpos[0]][hpos[1]]:
                dist = agent.getMazeDistance(pos,hpos)
                if (dist<besthV):
                    besthV=dist
                    besthpos = [pos]
    return besthpos,besthV
             
        
        