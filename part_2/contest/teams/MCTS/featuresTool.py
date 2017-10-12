
import os
import sys
teamName = os.path.split(os.path.dirname(os.path.abspath(__file__)))[1]
dir = "teams/{}/".format(teamName)
sys.path.append(dir)
import util
import copy


ESCAPE_DIST = 4
dirs = [(0,1),(0,-1),(1,0),(-1,0),(0,0)]
SIGHT_RANGE = 6
SCARED_TIME = 40
DRAW = False

class featuresTool():
    
    def __init__(self,dict=None):
        self.dict = dict
        self.lastState = None        
            
    def initGame(self,agent,gameState):
        #if not agent.index == agent.getTeam(gameState)[0]: return
        
        self.walls = gameState.getWalls()
        self.size = (self.walls.width,self.walls.height)
        self.allpos = [(i,j) for i in range(self.size[0]) for j in range(self.size[1]) if not self.walls[i][j]]
        #self.probMap = [self.iniProbMap() for i in range(gameState.getNumAgents())]
        self.probMap = [[gameState.getInitialAgentPosition(i)] for i in range(gameState.getNumAgents())]
        self.start = gameState.getAgentPosition(agent.index)[0]
        self.middle = (self.size[0]/2) - (self.start%2)
        self.team = agent.getTeam(gameState)
        self.mate = [i for i in self.team if not i ==agent.index]
        self.opp = agent.getOpponents(gameState)
        self.teamNum = gameState.getNumAgents()
        self.lastidx = 0
        self.lastpos = None
        self.lastState = [gameState for i in range(self.teamNum)]
        self.lastpos = [gameState.getAgentPosition(agent.index) for i in range(self.teamNum)]
        self.lastoppfoods = agent.getFoodYouAreDefending(gameState).asList()
        self.lastCapsules = len(agent.getCapsules(gameState))
        self.scareTimeLeft = 0
        #print self.allpos
        #print self.lastoppfoods
        return 

    
    def updateProbMap(self,agent,lastState,gameState):
        opp=self.opp
        team = self.team
        selfpos = gameState.getAgentPosition(agent.index)
        noisyDist = gameState.getAgentDistances()
        teamNum = self.teamNum
        
        if not noisyDist: return 0
        #print noisyDist
        
        if self.lastidx == agent.index: return 0
        
        lidx = self.lastidx
        idx = agent.index
        if not lidx == None:
            while not (idx - 1+teamNum)%teamNum in team:
                
                idx = (idx - 1+teamNum)%teamNum
                poso = gameState.getAgentPosition(idx)
                if not poso == None:
                    self.probMap[idx]=[poso]
                else:
                    self.probMap[idx]=self.expand(self.probMap[idx])
                        
            
        for i in opp:
            tempP = copy.copy(self.probMap[i])
            for pos in self.probMap[i]:
                trueD = util.manhattanDistance(selfpos,pos)
                prob1 = gameState.getDistanceProb(trueD,noisyDist[i])
                prob2 = gameState.getDistanceProb(trueD+1,noisyDist[i])
                prob3 = gameState.getDistanceProb(trueD-1,noisyDist[i])
                prob = max([prob1,prob2,prob3])
                if prob == 0:
                    while pos in tempP:
                        tempP.remove(pos)
            if len(tempP) != 0:
                self.probMap[i] = tempP
            
            tempP = copy.copy(self.probMap[i])
            for pos in self.probMap[i]:
                obs = util.manhattanDistance(pos,selfpos) < SIGHT_RANGE
                poso = gameState.getAgentPosition(i)
                if obs and poso == None:
                    while pos in tempP:
                        tempP.remove(pos)
            if len(tempP) != 0:
                self.probMap[i] = tempP
            
            #if len(tempP) == 0:
            if self.checkkill(agent,lastState,gameState,i):
                self.probMap[i]=[gameState.getInitialAgentPosition(i)]
                self.probMap[i]=self.expand(self.probMap[i])
            
        oppfoods = agent.getFoodYouAreDefending(gameState).asList()
        lastfoods = self.lastoppfoods
        #print (len(lastfoods),len(oppfoods))
        #util.pause()
        if len(lastfoods) > len(oppfoods):
            ppos = [pos for pos in lastfoods if pos not in oppfoods]
            for pos in ppos:
                if (pos in self.probMap[self.opp[0]]) and ((pos not in self.probMap[self.opp[1]])):
                    self.probMap[self.opp[0]] = [pos]
                if (pos in self.probMap[self.opp[1]]) and ((pos not in self.probMap[self.opp[0]])):
                    self.probMap[self.opp[1]] = [pos]
        
        for i in self.opp:
            tempP = copy.copy(self.probMap[i])
            state = gameState.getAgentState(i).isPacman
            for pos in self.probMap[i]:
                if abs(pos[0]-self.start) < 15:
                    oppstate = False
                else:
                    oppstate = True
                if (oppstate == state):
                    tempP.remove(pos)
        if len(tempP) != 0:
            self.probMap[i] = tempP
        
        for i in team:
            self.probMap[i] = [gameState.getAgentPosition(i)]
        #self.lastidx = agent.index
        return 0
        
    def expand(self,poss):
        temp = []
        for pos in poss:
            for dir in dirs:
                npos = (pos[0]+dir[0],pos[1]+dir[1])
                if (not self.walls[npos[0]][npos[1]]) and (npos not in temp):
                    temp.append(npos)
        return temp
    
    def drawProbMap(self,agent,gameState):
        agent.debugClear()
            #self.debugDraw([pos],[probMap[0][pos],0,0])
        agent.debugDraw(self.probMap[self.opp[0]],[1,0,0])
        agent.debugDraw(self.probMap[self.opp[1]],[0,1,0])
        tp = [pos for pos in self.probMap[self.opp[0]] if (pos in self.probMap[self.opp[1]])]
        agent.debugDraw(tp,[1,1,0])
        return 0
    
    def getFeatures(self,agent,gameState,action,successor = None):
        self.features = util.Counter()
        
        if (not agent.index == self.lastidx):
            self.update(agent,self.lastState[agent.index],gameState)

        self.lastidx = agent.index
        
            
        #print self.features
        #util.pause()
        return self.features
        
    def update(self,agent,lastState,gameState):
        self.updateProbMap(agent,lastState,gameState)
        self.lastidx = agent.index
        self.lastoppfoods = agent.getFoodYouAreDefending(gameState).asList()
        if DRAW:
            self.drawProbMap(agent,gameState)
        
        return 
        
        
    def checkkill(self,agent,gameState,successor,opp):
        #opp=self.opp
        
        
        pos1 = gameState.getAgentPosition(opp)
        pos2 = successor.getAgentPosition(agent.index)
        
        if pos1 == None:
            return False
        
        if pos1 == pos2:
            return True
            
                
        return False
        
        