from __future__ import division
import numpy as np
from pyfann import libfann
from math import ceil


class CaclaLearner:
    def __init__(self, dim_state, dim_action, action_positve=False, hidden_layer_action='auto', hidden_layer_value='auto', gamma=0.3, sigma=1):
        if hidden_layer_action == 'auto':
            hidden_layer_action = ceil((dim_state + dim_action) / 2)
        if hidden_layer_value == 'auto':
            hidden_layer_value = ceil((dim_state + 1) / 2)
        self.gamma = gamma
        self.sigma = sigma
        self.ann = libfann.neural_net()
        self.ann.create_standard_array([dim_state, hidden_layer_action, dim_action])
        self.vnn = libfann.neural_net()
        self.vnn.create_standard_array([dim_state, hidden_layer_value, 1])
        self.dim_action = dim_action

    def set_state(self, state):
        self.state = state
        self.V_state = self.get_value(state)

    def get_action(self):
        self.state_1 = self.state
        self.V_state_1 = self.V_state
        self.action = self.get_optimal(self.state) + np.random.normal(loc=0.0, scale=self.sigma, size=self.dim_action)
        return self.action

    def give_reward(self, reward):
        self.reward = np.array([reward])

    def learn(self):
        value = self.reward + self.gamma * self.V_state
        self.vnn.train(self.state_1, [value])

        if value > self.V_state_1:
            self.ann.train(self.state_1, self.action)

    def learn_episode_end(self):
        self.vnn.train(self.state_1, self.reward)
        self.ann.train(self.state, self.action)

    def get_optimal(self, state):
        return self.ann.run(state)

    def plot_optimal(self, a, b, step=100):
        return range(a, b, step), [self.get_optimal([s])[0] for s in range(a, b, step)]

    def get_value(self, state):
        return self.vnn.run(state)[0]


