import json
import pickle

#from sklearn.neural_network import MLPRegressor

def saveFile(filename,file):
    with open(filename, "w") as f:
        json.dump(file,f,indent = 4)
        
def loadFile(filename):
    with open(filename) as f:
        return json.load(f)  
        
def savePickle(filename,file):
    with open(filename, "w") as f:
        pickle.dump(file, f)
        
def loadPickle(filename):
    with open(filename) as f:
        return pickle.load(f)  
        
        