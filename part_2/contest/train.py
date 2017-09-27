import os

times = 2
filename = "capture.py"
arg = ['-r','-b']
argv = ['baselineTeam','myTeam']
arlen = len(arg)

for i in range(times):
    str = "python "+filename 
    
    for j in range(arlen):
        str+=' '+arg[j]+' '+argv[j]

    os.system(str)