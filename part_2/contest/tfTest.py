from capture import readCommand, runGames

cmdString = "-r tfModeSelTeam -b baselineRandomOneTeam --redOpts=mode=Train".split()
options = readCommand(cmdString)
runGames(**options)