from capture import readCommand, runGames

cmdString = "-r tfModeSelTeam -l layouts/trivialCapture.lay --redOpts=mode=Train".split()
options = readCommand(cmdString)
runGames(**options)