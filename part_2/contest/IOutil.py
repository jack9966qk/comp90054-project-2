import json

def saveFile(filename,file):
    with open(filename, "w") as f:
        json.dump(file,f,indent = 4)
        
def loadFile(filename):
    with open(filename) as f:
        return json.load(f)  