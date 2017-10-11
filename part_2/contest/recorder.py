import cPickle
import datetime

class Recorder(object):
    def __init__(self, fileName = None):
        self.steps = []
        if not fileName:
            self.fileName = "episodes/" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".cpickle"
        else:
            self.fileName = fileName
    
    def recordStep(self, agent, gameState, prevState, prevAction, reward, extra):
        self.steps.append({"agent": agent,
                           "currentState": gameState,
                           "prevState": prevState,
                           "prevAction": prevAction,
                           "reward": reward,
                           "terminal": False,
                           "extra": extra})
    
    def recordFinalStep(self, agent, gameState, prevState, prevAction, reward, extra):
        self.steps.append({"agent": agent,
                           "currentState": gameState,
                           "prevState": prevState,
                           "prevAction": prevAction,
                           "reward": reward,
                           "terminal": True,
                           "extra": extra})
        self.save()
    
    def save(self):
        with open(self.fileName, "wb") as f:
            cPickle.dump(self.steps, f)

def loadRecord(fileName):
    with open(fileName, "rb") as f:
        return cPickle.load(f)