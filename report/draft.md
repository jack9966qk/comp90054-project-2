## Approaches

A variety of approaches were attempted in this project, where different techniques covered in the subject are involved.

### Reinforcement Learning

Inspired by the Pacman project in an earlier tutorial on reinforcement learning, we attempted to apply the technique of approximate Q-learning. 

Instead of using the game state directly, a set of features are extracted from it, where weights are applied on them. Feature extraction is preferred because the state space is too large for learning to be done effectively. It also helps the algorithm to generalise to mazes with different sizes and layouts, since the feature space remains consistent against these changes.

Some of the features include the distance to closest food, ghost, ghost and home area, number of food carrying, whether agent is a Pacman, and more. Opponent positions are recorded and maintained during update, so that approximate can be obtained even if they are not directly visible. The agent is positively rewarded if it obtains score, captures food or invaders, and negatively rewarded for score lost and deaths. It is also rewarded for the final outcome (win, lose or tie).

### Reinforcement Learning with Modes

Since the rules of the game appear to be much more complex than the original Pacman game, the concept of "modes" were introduced to the agent, where each mode represents a specific sub-goal, such as "offense", "defense" or "back to home".

Each mode has its corresponding set of weights and reward function. In each step, the agent firstly determines a mode through a simple decision tree, then chooses an action using weights in the specific mode. Applying the same training procedure as the last approach, weights of each mode are trained simultaneously.

### Predefined Weights with Modes

This is an variation of the previous attempt, where weights are predefined instead of being learnt through experience.

### MCTS with Modes

As another attempt to handle the large, unknown state space, Monte Carlo tree search was implemented. After determining a mode, Monte Carlo tree search is performed, with UCB1 applied to balance between exploration and exploitation. The algorithm is mostly the same as discussed earlier in this subject, except that instead of running simulation until a terminal state, it terminates when a certain depth is reached, with value of the state approximated as the product of features and weights.

### Others

Many other approaches were attempted, including but not limited to using machine learning regression to approximate values through features, deep Q-learning using CNN with 2D matrix input or dense layers with features as input.

## Results

[Table of ranked agents, similar to online tournament]

[Table of tournament results for some agents]

Ranking of agents |
-----------------|
`staff_team_top` |
MCTS |
Modes with predefined weights |
`staff_team_medium`|
`staff_team_basic`|


Pure reinforcement learning does not produce good results overall, although the agent learns to chase invaders and eating food from opponents, it is not able to escape from ghosts and return to the home area. A single set of weights could be too simple for the game mechanics, where agents may have different priorities and strategies in different scenarios. For example, the agent is unable to recognise the long term goal of returning captured food.

Introducing mode selection does appear to improve the performance. With reinforcement learning, weights trained for defense and offense modes are effective, while the "back to home" mode remains unhelpful. The agent sometimes moves between two positions near the border without crossing it, which may indicate some bugs in feature extraction or the reward function.

With predefined weights, however, the agent performs well in all modes, which is able to beat the baseline team easily, and get a relatively high rank above `staff_team_medium` on the tournament. It indicates that the idea of mode selection and value approximation through features are indeed helpful, and could be applied to other approaches, while the learning process requires improvement.

More sophisticated learning algorithms such as Deep Q-learning are therefore experimented. However, they were not able to produce successful agents, possibly due to the lack of training data or experience.

Combining the ideas above with Monte Carlo search algorithm leads to better results, which is expected because rather than the greedy approaches above, it simulates subsequent game states and anticipates risks such as dead ends. The agent performs slightly better than before, and beats `staff_team_top` occasionally.

It is also worth mentioning that, due to the logic in decision tree, agents using mode selection are more likely to be defensive rather than offensive. When there is a contest between two of such agents, it is likely that both teams stays near at the border since both team choose to be defensive, resulting in ties. The mode selection could be further improved either by refining the logic, or adapting some algorithms such as reinforcement learning.
