
import moreUtil
import util
import IOutil
import pickle
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


tdict = [
    'ClostestFoodDist',
    'TeamFoodLeft',
    'OpponentFoodLeft',
    'HomeDist',
    'TeamDist',
    'IsPacman',
    'TeamIsPacman',
    'Carry'
]

FileName = "Fdict.json"
dirs = [(0,1),(0,-1),(1,0),(-1,0),(0,0)]
modelName = "modle.pickle"

class featuresTool():
    
    def __init__(self,dict=None,usemodel = False):
        self.dict = dict
        self.lastState = None
        if not dict:
            self.dict = IOutil.loadFile(FileName)
            #self.dict = tdict
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
        self.start = agent.start[0]
        self.middle = (self.size[0]/2) - (self.start%2)
        self.team = agent.getTeam(gameState)
        self.mate = [i for i in self.team if not i ==agent.index]
        self.opp = agent.getOpponents(gameState)
        self.teamNum = gameState.getNumAgents()
        self.lastidx = 0
        self.lastpos = None
        self.lastState = [gameState for i in range(self.teamNum)]
            
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
                
                
                self.probMap[idx]=self.expand(self.probMap[idx])
                        
            
        for i in opp:
            tempP = self.probMap[i]
            for pos in tempP:
                trueD = util.manhattanDistance(selfpos,pos)
                prob1 = gameState.getDistanceProb(trueD,noisyDist[i])
                prob2 = gameState.getDistanceProb(trueD+1,noisyDist[i])
                prob3 = gameState.getDistanceProb(trueD-1,noisyDist[i])
                prob = max([prob1,prob2,prob3])
                if prob == 0:tempP.remove(pos)
            self.probMap[i] = tempP
                    
            
            poso = gameState.getAgentPosition(i)
            if not poso == None:
                self.probMap[i]=[poso]
            
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
        return 0
    
    def getFeatures(self,agent,gameState,action,successor = None):
        features = util.Counter()
        if successor == None :successor = gameState.generateSuccessor(agent.index, action)
        
        
        if (not agent.index == self.lastidx): #and (not self.lastidx == None):
            self.update(agent,self.lastState[agent.index],gameState)
        self.lastidx = agent.index
        self.lastState[agent.index] = gameState
        #self.updateProbMap(agent,gameState)
        #print self.probMap[self.opp[0]]
        #self.drawProbMap(agent,gameState)
        #util.pause()
        
        for line in self.dict:
            features[line] = getattr(self,'get'+line)(agent,gameState,action,successor)
        
        #print features
        #util.pause()
        return features
        
    def update(self,agent,lastState,gameState):
        self.updateProbMap(agent,lastState,gameState)
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
        
    def getClostestFoodDist(self,agent,gameState,action,successor):
        return moreUtil.getClosestFoodFeature(agent, gameState, successor)
        
    def getTeamFoodLeft(self,agent,gameState,action,successor):
        return moreUtil.getFoodLeftFeature(agent, successor)
    
    def getOpponentFoodLeft(self,agent,gameState,action,successor):
        return len(agent.getFoodYouAreDefending(successor).asList())
        
    def getTeamDist(self,agent,gameState,action,successor):
        return agent.getMazeDistance(gameState.getAgentPosition(self.team[0]), gameState.getAgentPosition(self.team[1]))
        
    def getIsPacman(self,agent,gameState,action,successor):
        return int(gameState.getAgentState(agent.index).isPacman)-0.5
    
    def getTeamIsPacman(self,agent,gameState,action,successor):
        return int(gameState.getAgentState(self.mate[0]).isPacman)-0.5
        
    def getHomeDist(self,agent,gameState,action,successor):
        return moreUtil.getHomeDistFeature(self,agent, successor)
        
    def getGhost1Dist(self,agent,gameState,action,successor):
        return moreUtil.getGhostDistFeature(self,agent, successor,self.opp[0])
        
    def getGhost2Dist(self,agent,gameState,action,successor):
        return moreUtil.getGhostDistFeature(self,agent, successor,self.opp[1])
    
    def getInvader1Dist(self,agent,gameState,action,successor):
        return moreUtil.getInvaderDistFeature(self,agent, successor,self.opp[0])
        
    def getInvader2Dist(self,agent,gameState,action,successor):
        return moreUtil.getInvaderDistFeature(self,agent, successor,self.opp[1])
        
    def getHasInvader1(self,agent,gameState,action,successor):
        return int(not moreUtil.getInvaderDistFeature(self,agent, successor,self.opp[0]) == 999999)-0.5
        
    def getHasInvader2(self,agent,gameState,action,successor):
        return int(not moreUtil.getInvaderDistFeature(self,agent, successor,self.opp[1]) == 999999)-0.5
        
    def getCarry(self,agent,gameState,action,successor):
        #return moreUtil.getCarryFeature(agent)
        return gameState.getAgentState(agent.index).numCarrying
        