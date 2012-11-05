from __future__ import division
import abceagent
from abcetools import is_zero, is_positive, is_negative, NotEnoughGoods
import random
import numpy as np


class DownFirm(abceagent.Agent, abceagent.Firm):
    def __init__(self, simulation_parameters, agent_parameters, _pass_to_engine):
        """ Productes a cobb_douglas function with random exponents that sum up to 1 """
        abceagent.Agent.__init__(self, *_pass_to_engine)
        exponents = np.random.uniform(size=10)
        exponents /= np.sum(exponents)
        exponents = dict([('K%i' % i, exponents[i]) for i in range(10)])
        self.set_cobb_douglas('consumer_good', 1, exponents)

        self.sales_prices = 1

    def age_captial(self):
        self.destroy(self.possessions_filter(ends_with='_%i' % self.round))
        for i in range(10):
            self.create('K%i' % i, self.possessions_filter(begin_with='K%i_' % i))

    def production(self):
        """ produces all he can """
        self.produce_use_everything()


