import copy
import util
import utils
dirs = [(0,1),(0,-1),(1,0),(-1,0),(0,0)]

def offence_mode(tool,agent,gameState):
    oppposs = [tool.probMap[i] for i in tool.opp]
    spos = gameState.getAgentPosition(agent.index)
    tpos = gameState.getAgentPosition([i for i in agent.getTeam(gameState) if not i == agent][0])
    obsarea = utils.obspos(tool,agent,gameState)
    action,temp =utils.eatFoodSimu(tool,agent,gameState,gameState.getLegalActions(agent.index),[tpos]+tool.expand(obsarea))
    if temp == 99999:
        action,temp = utils.eatFoodSimu(tool,agent,gameState,gameState.getLegalActions(agent.index),[])
    if action == None:
        action = "Stop"
    return action
    
    
def defence_mode(tool,agent,gameState):
    oppposs = [tool.probMap[i] for i in tool.opp]
    spos = gameState.getAgentPosition(agent.index)
    tpos = gameState.getAgentPosition([i for i in agent.getTeam(gameState) if not i == agent.index][0])
    '''
    if (not gameState.getAgentState(tool.opp[0]).isPacman) and (not gameState.getAgentState(tool.opp[0]).isPacman):
        mwalls = []
    else:
    '''
    mwalls = [(tool.oppmiddle,i) for i in range(1,tool.size[1]-1)]
    
    obsarea = utils.obspos(tool,agent,gameState)
    obsarea = tool.expand(obsarea)
    if gameState.getAgentState(agent.index).isPacman:
        action,temp =utils.backHomeSimu(tool,agent,gameState,gameState.getLegalActions(agent.index),[])
    else:
        action,temp =utils.killInvaderSimu(tool,agent,gameState,gameState.getLegalActions(agent.index),[tpos]+mwalls)
    if temp == 99999:
        action,temp = utils.killInvaderSimu(tool,agent,gameState,gameState.getLegalActions(agent.index),[]+mwalls)
    if action == None:
        action = "Stop"
    return action
    
