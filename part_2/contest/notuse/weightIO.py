import pickle
import json

def saveWeights(weights, filename):
    with open(filename, "w") as f:
        pickle.dump(weights, f)
        
def saveWeightsJson(weights, filename):
    with open(filename, "w") as f:
        json.dump(weights,f,indent = 4)

def loadWeights(filename):
    with open(filename) as f:
        return pickle.load(f)       
        
def loadWeightsJson(filename):
    with open(filename) as f:
        return json.load(f)