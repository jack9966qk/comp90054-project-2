from capture import readCommand, runGames

cmdString = "-r tfCnnTeam -b baselineRandomOneTeam -l layouts/tinyCaptureSuperEasy.lay --redOpts=mode=Train".split()
options = readCommand(cmdString)
runGames(**options)