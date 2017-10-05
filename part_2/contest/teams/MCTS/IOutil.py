import json
import pickle
import os
import sys
teamName = os.path.split(os.path.dirname(os.path.abspath(__file__)))[1]
dir = "teams/{}/".format(teamName)
sys.path.append(dir)

#from sklearn.neural_network import MLPRegressor

def saveFile(filename,file):
    with open(dir+filename, "w") as f:
        json.dump(file,f,indent = 4)
        
def loadFile(filename):
    with open(dir+filename) as f:
        return json.load(f)  
        
def savePickle(filename,file):
    with open(dir+filename, "w") as f:
        pickle.dump(file, f)
        
def loadPickle(filename):
    with open(dir+filename) as f:
        return pickle.load(f)  
        
        