## Approaches

A variety of approaches were attempted in this project, where different techniques covered in the subject are involved.

### Reinforcement Learning

Inspired by the Pacman project in an earlier tutorial on reinforcement learning, we attempted to apply the technique of approximate Q-learning. 

Instead of using the game state directly, weights are applied on a set of features extracted from states. Feature extraction is preferred because the state space is too large for learning to be done effectively. It also helps the algorithm to generalise to mazes with different sizes and layout, since the feature space remains consistent.

> Extracted features include:...

> Reward for the game is defined as:...

As discussed on the [project page](http://inst.eecs.berkeley.edu/~cs188/pacman/reinforcement.html), weights are initialised with arbitrary values, and then updated in each step:

> [formula]

### Reinforcement Learning with Modes

Since the rules of the game appear to be much more complex than the original Pacman game, the concept of "modes" were introduced to the agent, where each mode represents a specific sub-goal, such as "offense", "defense" or "back to home".

Each mode has its corresponding set of weights and reward function. In each step, the agent firstly determines a mode through a simple decision tree, then chooses an action using weights in the specific mode. Applying the same training procedure as the last approach, weights of each mode are trained simultaneously.

### Predefined Weights with Modes

This is an variation of the previous attempt, where weights are predefined instead of being learnt through experience.

### MCTS

As another attempt to handle the large, unknown state space, Monte Carlo tree search was implemented. After determining a mode, Monte Carlo tree search is performed, with UCB1 applied to balance between exploration and exploitation. The algorithm is mostly the same as discussed earlier in this subject, except that instead of running simulation until a terminal state, it terminates when a certain depth is reached, with value of the state approximated as the product of features and weights.

### Others

Many other approaches were attempted, including but not limited to using machine learning regression to approximate values through features, deep Q-learning using CNN with 2D matrix input or dense layers with features as input

## Results

[Table of ranked agents, similar to online tournament]

[Table of tournament results for some agents]

Pure reinforcement learning does not produce good results overall, although the agent learns to chase invaders and eating food from opponents, it is not able to escape from ghosts and return to the home area.

Introducing mode selection does appear to improve the performance. With reinforcement learning, weights trained for defense and offense modes are effective, while weights for "back to home" mode remains unhelpful. The problem is overcomed by predefining the weights, which indicates...

Learning weights for each mode is more effective because...
