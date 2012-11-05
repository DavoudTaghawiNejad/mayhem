from __future__ import division
import abceagent
from abcetools import is_zero, is_positive, is_negative, NotEnoughGoods
import numpy as np


class DownFirm(abceagent.Agent, abceagent.Firm):
    def __init__(self, simulation_parameters, agent_parameters, _pass_to_engine):
        """ Productes a cobb_douglas function with random self.exponents that sum up to 1 """
        abceagent.Agent.__init__(self, *_pass_to_engine)
        self.exponents = np.random.uniform(size=10)
        self.exponents /= np.sum(self.exponents)
        self.exponents = dict([('K%i' % i, self.exponents[i]) for i in range(10)])
        self.set_cobb_douglas('consumer_good', 1, self.exponents)

        self.sales_prices = 1

    def age_captial(self):
        obsolete = self.possessions_filter(endswith='_%i' % self.round)
        for good in obsolete:
            self.destroy(good, obsolete[good])
        print [self.possessions_filter(beginswith='K%i_' % i) for i in range(10)]
        self.create('K', sum([sum(self.possessions_filter(beginswith='K%i_' % i).values()) for i in range(10)]))
        print sum([sum(self.possessions_filter(beginswith='K%i_' % i).values()) for i in range(10)])

    def production(self):
        """ produces consumption good from all its working capital. The maximum
        it can produce is given by the investment_good K he has
        """
        self.log('working', {'capital': float(self.possession('working_captial'))})
        production_maximum = min(self.possession('K') ** self.exponents[0], self.possession('working_captial'))  # produce the maximum or all you got
        self.produce(self.production, {'working_captial': production_maximum})

    def consumer_good_to_auctioneer(self):
        self.message('household', 0, 'consumer_good_quantity', self.possession('consumer_good'))

    def sell_consumer_good(self):
        self.price_consumption_good = self.get_messages('consumer_good_demand')[0].content
        self.sell('household', 0, 'consumer_good', self.possession('consumer_good'), self.price_consumption_good)

    def update_expected_price(self):
        self.expected_price_of_consumption_good = self.price_consumption_good
