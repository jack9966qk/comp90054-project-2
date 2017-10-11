from capture import readCommand, runGames

cmdString = "-r tfDqfdModeSelTeam --redOpts=mode=Train".split()
options = readCommand(cmdString)
runGames(**options)