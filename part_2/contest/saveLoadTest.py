from tensorforce import Configuration
from tensorforce.agents import PPOAgent, DQNAgent
from tensorforce.core.networks import layered_network_builder
from tensorforce.core.networks import from_json
from tensorforceTrainTeam import saveModel, loadModelIfExists

##### ADAPTED FROM TENSORFORCE BLOGPOST
# https://reinforce.io/blog/introduction-to-tensorforce/

network = from_json("tensorforceNetwork.json")

# Define a state
states = dict(shape=(2048,), type='float')

# Define an action (models internally assert whether
# they support continuous and/or discrete control)
actions = dict(continuous=False, num_actions=5)

# The agent is configured with a single configuration object
agent_config = Configuration(
    batch_size=8,
    learning_rate=0.001,
    memory_capacity=800,
    first_update=80,
    repeat_update=4,
    target_update_frequency=20,
    states=states,
    actions=actions,
    network=network
)
agent = DQNAgent(config=agent_config)

# # agent.save_model("tensorforceModel/")
# retval = agent.model.saver.save(agent.model.session, "tensorforceModel/")
# print(retval)

# agent.load_model("tensorforceModel/")

print(agent.model.session.graph)

saveModel(agent)
loadModelIfExists(agent)