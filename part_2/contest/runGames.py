import imp
from multiprocessing import Pool
from functools import partial

# single threaded game simulation, writes replay file to directory
def runGames(redTeam, blueTeam, dir, numGames, prefix):
    call(["python", "./capture.py",
          "-r", redTeam, "-b", blueTeam, "-l", "RANDOM",
          "-Q", "-n", str(numGames), "--record={}/{}replay".format(dir, prefix)])
    print("{} finished".format(prefix))

def simulateGames(redTeam, blueTeam, numRuns=1, numGamesPerRun=1, numProcesses=20):
    dir = "replay/" + time.strftime("%b-%d-%H-%M-%S", time.localtime(time.time()))
    if not os.path.exists(dir):
        os.mkdir(dir)
    
    pool = Pool(processes=numProcesses)
    runFunc = partial(runGames, redTeam, blueTeam, dir, numGamesPerRun)

    argsIter = [ "run{:2d}_".format(i) for i in range(numRuns) ]
    for args in argsIter: print(args)
    for i in pool.imap_unordered(runFunc, argsIter):
        print(i)
    # pool.join()
    print("all runs finished")
    return dir

if __name__ == "__main__":
    
    dir = simulateGames("baselineTeam", "baselineTeam", numGamesPerRun=50, numRuns=500)