from capture import readCommand, runGames

cmdString = "-r tfModeSelTeam -b baselineRandomOneTeam -l layouts/tinyCaptureSuperEasy.lay --redOpts=mode=Train".split()
options = readCommand(cmdString)
runGames(**options)