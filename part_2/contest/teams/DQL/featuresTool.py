
import moreUtil
import util
import IOutil
import pickle
import reward
from sklearn.neural_network import MLPRegressor

allDict = [
'WallGrid',
'TeamFoodGrid',
'OpponentFoodGrid',
'SelfPacmanPositionGrid',
'SelfGhostPositionGrid',
'SelfScaredGhostPositionGrid',
'TeamPacmanPositionGrid',
'TeamGhostPositionGrid',
'TeamScaredGhostPositionGrid',
'Opponent1PacmanPositionGrid',
'Opponent1GhostPositionGrid',
'Opponent1ScaredGhostPositionGrid',
'Opponent2PacmanPositionGrid',
'Opponent2GhostPositionGrid',
'Opponent2ScaredGhostPositionGrid',
'TeamCapsule',
'OpponentCapsule',

'ClostFoodDist',
'TeamFoodLeft',
'OpponentFoodLeft',
'InvaderDist',
'HomeDist',
'Ghost1Dist',
'Ghost2Dist'
]


DRAW = False
ESCAPE_DIST = 4
FileName = "Fdict.json"
dirs = [(0,1),(0,-1),(1,0),(-1,0),(0,0)]
modelName = "modle.pickle"
SIGHT_RANGE = 6
MODS_FILENAME = 'ModDict.json'

class featuresTool():
    
    def __init__(self,dict=None,usemodel = False):
        self.dict = dict
        self.lastState = None
        if not dict:
            self.dict = IOutil.loadFile(FileName)
            #self.dict = tdict
        self.Mdict = IOutil.loadFile(MODS_FILENAME)
        rMdict = {}
        for i in range(len(self.Mdict)):
            rMdict[self.Mdict[i]]=i
        self.rMdict = rMdict
        #print self.rMdict
        if usemodel:
            with open(modelName) as f:
                self.model = pickle.load(f) 
            #self.model = IOutil.loadPickle(modelName)
            
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
            
       # print self.allpos
        return 
        
        '''
    def iniProbMap(self):
        temp = util.Counter()
        for pos in self.allpos:
            temp[pos]=0
        return temp
        '''
    def evaluate(self,features):
        X = self.getFeaturesSet(features)
        predict = self.model.predict([X])
        return predict[0]
    
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
            tempP = self.probMap[i]
            for pos in tempP:
                trueD = util.manhattanDistance(selfpos,pos)
                prob1 = gameState.getDistanceProb(trueD,noisyDist[i])
                prob2 = gameState.getDistanceProb(trueD+1,noisyDist[i])
                prob3 = gameState.getDistanceProb(trueD-1,noisyDist[i])
                prob = max([prob1,prob2,prob3])
                if prob == 0:
                    while pos in tempP:
                        tempP.remove(pos)
            
            
            for pos in tempP:
                obs = util.manhattanDistance(pos,selfpos) < SIGHT_RANGE
                poso = gameState.getAgentPosition(i)
                if obs and poso == None:
                    while pos in tempP:
                        tempP.remove(pos)
            self.probMap[i] = tempP
            
            #if len(tempP) == 0:
            if self.checkkill(agent,lastState,gameState,i):
                self.probMap[i]=[gameState.getInitialAgentPosition(i)]
                self.probMap[i]=self.expand(self.probMap[i])
            
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
        if successor == None :successor = gameState.generateSuccessor(agent.index, action)
        
        
        if (not agent.index == self.lastidx):
            self.update(agent,self.lastState[agent.index],gameState)
        self.lastidx = agent.index
        self.lastState[agent.index] = gameState
        self.lastpos[agent.index] = gameState.getAgentPosition(agent.index)
        
        #print self.probMap[0]
        #util.pause()
        
        for line in self.dict:
            self.features[line] = getattr(self,'get'+line)(agent,gameState,action,successor)
        
        #print features
        #util.pause()
        return self.features
        
    def update(self,agent,lastState,gameState):
        self.updateProbMap(agent,lastState,gameState)
        if DRAW:
            self.drawProbMap(agent,gameState)
        
        return 
        
    def getFeaturesSet(self,featrues):
        temp = []
        for line in self.dict:
            temp.append(featrues[line])
        return temp
        
    def getTrainSet(self,agent,gameState,action,successor):
        fea = util.Counter()
        if not type(gameState) == str:
            fea = self.getFeatures(agent,gameState,action,successor)
        
        temp = []
        for line in self.dict:
            temp.append(fea[line])
        return temp
        
    def getMod(self,agent,features,gameState):
        mod = moreUtil.getModSelf(self,agent,features,gameState)
        return mod
        
    def getModSet(self,agent,gameState,action,successor):
        fea = util.Counter()
        if not type(gameState) == str:
            fea = self.getFeatures(agent,gameState,action,successor)
        
        temp = []
        for line in self.dict:
            temp.append(fea[line])
        
        mod = self.getMod(agent,fea,gameState)
        
        #if mod == "defense1":
        #    print 111
        #print 222
        return temp,mod#self.getModLabel(mod)
        
    def getModLabel(self,mod):
        if not (mod in self.Mdict):
            return -1
        return self.rMdict[mod]
        
    def checkkill(self,agent,gameState,successor,opp):
        #opp=self.opp
        team = self.team
        
        
        pos1 = gameState.getAgentPosition(opp)
        pos2 = successor.getAgentPosition(agent.index)
        
        if pos1 == None:
            return False
        
        if pos1 == pos2:
            return True
            
                
        return False
        
    def getReward():
        return 
        
    def getClostestFoodDist(self,agent,gameState,action,successor):
        return min(moreUtil.getFoodDists(agent, successor))
        
    def getTeamFoodLeft(self,agent,gameState,action,successor):
        return len(moreUtil.getFoodDists(agent, successor))
    
    def getSumOfFoodDists(self,agent,gameState,action,successor):
        return sum(moreUtil.getFoodDists(agent, successor))
        
    def getOpponentFoodLeft(self,agent,gameState,action,successor):
        return len(agent.getFoodYouAreDefending(successor).asList())
        
    def getTeamDist(self,agent,gameState,action,successor):
        return agent.getMazeDistance(self.lastpos[self.team[0]], self.lastpos[self.team[0]])
        
    def getIsPacman(self,agent,gameState,action,successor):
        return int(gameState.getAgentState(agent.index).isPacman)-0.5
    
    def getTeamIsPacman(self,agent,gameState,action,successor):
        return int(gameState.getAgentState(self.mate[0]).isPacman)-0.5
        
    def getHomeDist(self,agent,gameState,action,successor):
        return moreUtil.getHomeDistFeature(self,agent, successor)
        
    def getObsGhost1Dist(self,agent,gameState,action,successor):
        poso = gameState.getAgentPosition(self.opp[0])
        if poso == None:
            return 99999
        else: 
            return agent.getMazeDistance(gameState.getAgentPosition(agent.index),poso)
        
    def getObsGhost2Dist(self,agent,gameState,action,successor):
        poso = gameState.getAgentPosition(self.opp[1])
        if poso == None:
            return 99999
        else: 
            return agent.getMazeDistance(gameState.getAgentPosition(agent.index),poso)
    
    def getGhost1Dist(self,agent,gameState,action,successor):
        return moreUtil.getGhostDistFeature(self,agent, successor,self.opp[0])
        
    def getGhost2Dist(self,agent,gameState,action,successor):
        return moreUtil.getGhostDistFeature(self,agent, successor,self.opp[1])
        
    def getGhost1Close(self,agent,gameState,action,successor):
        return min(moreUtil.getGhostDistFeature(self,agent, successor,self.opp[0]) , ESCAPE_DIST) 
        
    def getGhost2Close(self,agent,gameState,action,successor):
        return min(moreUtil.getGhostDistFeature(self,agent, successor,self.opp[1]) , ESCAPE_DIST) 
        
    def getHasGhost(self,agent,gameState,action,successor):
        dist1 = moreUtil.getGhostDistFeature(self,agent, successor,self.opp[0])
        dist2 = moreUtil.getGhostDistFeature(self,agent, successor,self.opp[1])
        return int(min(dist1,dist2) < ESCAPE_DIST) - 0.5
        
    def getInvader1Dist(self,agent,gameState,action,successor):
        return moreUtil.getInvaderDistFeature(self,agent, successor,self.opp[0])
        
    def getInvader2Dist(self,agent,gameState,action,successor):
        return moreUtil.getInvaderDistFeature(self,agent, successor,self.opp[1])
        
    def getHasInvader1(self,agent,gameState,action,successor):
        return int(not moreUtil.getInvaderDistFeature(self,agent, successor,self.opp[0]) == 999999)-0.5
        
    def getHasInvader2(self,agent,gameState,action,successor):
        return int(not moreUtil.getInvaderDistFeature(self,agent, successor,self.opp[1]) == 999999)-0.5
        
    def getHasKill1(self,agent,gameState,action,successor):
        return int(self.checkkill(agent,gameState,successor,self.opp[0]))-0.5
        
    def getHasKill2(self,agent,gameState,action,successor):
        return int(self.checkkill(agent,gameState,successor,self.opp[1]))-0.5
        
    def getCarryXHome(self,agent,gameState,action,successor):
        return moreUtil.getHomeDistFeature(self,agent, successor) * gameState.getAgentState(agent.index).numCarrying
        
    def getIsStop(self,agent,gameState,action,successor):
        return int(action == "Stop")-0.5
        
    def getCarry(self,agent,gameState,action,successor):
        #return moreUtil.getCarryFeature(agent)
        return gameState.getAgentState(agent.index).numCarrying
        