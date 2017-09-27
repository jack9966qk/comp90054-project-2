from threading import Thread
from capture import readCommand, runGames
import socket
import pickle
import subprocess
import numpy as np
from gym.spaces import Discrete, Box
import network

class PacmanEnv(object):
    reward_range = (-np.inf, np.inf)
    action_space = Discrete(5)
    observation_space = Box(0, 1, (32, 16, 4))

    def __init__(self):
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(("localhost", 2333))
        self.socket.listen(1)
        self.conn = None
        self.gameProcess = None
        # print("ENV INIT COMPLETE")

    def step(self, action):
        """Run one timestep of the environment's dynamics.
        Accepts an action and returns a tuple (observation, reward, done, info).
        # Arguments
            action (object): An action provided by the environment.
        # Returns
            observation (object): Agent's observation of the current environment.
            reward (float) : Amount of reward returned after previous action.
            done (boolean): Whether the episode has ended, in which case further step() calls will return undefined results.
            info (dict): Contains auxiliary diagnostic information (helpful for debugging, and sometimes learning).
        """
        # print("ENV SENDING ACTION")
        network.send(self.conn, action)
        observation, reward, done, info = network.receive(self.conn)
        return observation, reward, done, info

    def reset(self):
        """
        Resets the state of the environment and returns an initial observation.
        
        # Returns
            observation (object): The initial observation of the space. Initial reward is assumed to be 0.
        """
        self.gameProcess = subprocess.Popen(["python", "capture.py",
                                             "-r", "envTeam", "-b", "baselineTeam", "-q", "-z", "0.5"])
        # print("ENV WAITING FOR CONNECTION")
        self.conn, _ = self.socket.accept()
        observation = network.receive(self.conn)
        # print("ENV RECEIVED INITIAL OBSERVATION")
        return observation

    def render(self, mode='human', close=False):
        """Renders the environment.
        The set of supported modes varies per environment. (And some
        environments do not support rendering at all.) 
        
        # Arguments
            mode (str): The mode to render with.
            close (bool): Close all open renderings.
        """
        pass

    def close(self):
        """Override in your subclass to perform any necessary cleanup.
        Environments will automatically close() themselves when
        garbage collected or when the program exits.
        """
        # print("ENV CLOSE")
        self.socket.close()
        if self.gameProcess:
            self.gameProcess.kill()

    def seed(self, seed=None):
        """Sets the seed for this env's random number generator(s).
        
        # Returns
            Returns the list of seeds used in this env's random number generators
        """
        return [2017]

    def configure(self, *args, **kwargs):
        """Provides runtime configuration to the environment.
        This configuration should consist of data that tells your
        environment how to run (such as an address of a remote server,
        or path to your ImageNet data). It should not affect the
        semantics of the environment.
        """
        pass

    def __del__(self):
        # print("ENV __DEL__")
        self.socket.close()
        if self.gameProcess:
            self.gameProcess.kill()

    def __str__(self):
        return '<{} instance>'.format(type(self).__name__)