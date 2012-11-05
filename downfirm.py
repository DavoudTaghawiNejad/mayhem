from __future__ import division
import abceagent
from abcetools import is_zero, is_positive, is_negative, NotEnoughGoods
import numpy as np
from scipy.optimize import minimize, fmin_cobyla, minimize_scalar
import random


class DownFirm(abceagent.Agent, abceagent.Firm):
    def __init__(self, simulation_parameters, agent_parameters, _pass_to_engine):
        """ Productes a cobb_douglas function with random self.exponents that sum up to 1 """
        abceagent.Agent.__init__(self, *_pass_to_engine)
        self.num_downfirms = simulation_parameters['num_downfirm']
        self.exp_num = np.random.uniform(size=2)
        self.exp_num /= np.sum(self.exp_num)
        self.exponents = {}
        self.exponents['W'] = self.exp_num[0]
        self.exponents['K'] = self.exp_num[1]
        self.set_cobb_douglas('consumer_good', 1, self.exponents)
        self.sales_price_consumption_good = 5

    def age_captial(self):
        obsolete = self.possessions_filter(endswith='_%i' % self.round)
        for good in obsolete:
            self.destroy(good, obsolete[good])
        self.create('K', sum([sum(self.possessions_filter(beginswith='K%i_' % i).values()) for i in range(10)]))

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
        self.sales_price_consumption_good_consumption_good = self.get_messages('consumer_good_demand')[0].content
        self.sell('household', 0, 'consumer_good', self.possession('consumer_good'), self.sales_price_consumption_good_consumption_good)

    def update_expected_price(self):
        self.expected_price_of_consumption_good = self.sales_price_consumption_good_consumption_good

    def sell_captial(self):
        """ calculates the profit maximizing
        """
        price = np.random.uniform(0, 10, 1)
        objective = lambda x: - (self.sales_price_consumption_good
                                    * (self.possession('K') - x[0])
                                    + x[0] * price
                                )
        constraint = lambda x: self.possession('K') - x[0]
        x = fmin_cobyla(func=objective, x0=(0, 0), cons=[constraint], disp=0)
        quantity = x[0]
        self.sell('downfirm', random.randint(0, self.num_downfirms), 'K', float(quantity), price)

    def buy_captial(self):
        offer = dict(self.get_offers_all(descending=True))
        while len(offer) > 0:
            try:
                objective = lambda x: - (self.sales_price_consumption_good
                                            * (self.possession('W') + x[0]) ** self.exponents['W']
                                            * (self.possession('K') + x[1]) ** self.exponents['K']
                                            - x[0] * offer['W'][-1]['price']
                                            - x[1] * offer['K'][-1]['price']
                                        )
                res = minimize(objective, x0=(2, 0), method='L-BFGS-B', bounds=((0, offer['W'][-1]['quantity']), (0, offer['K'][-1]['quantity'])))
                x = res.x
                self.accept_partial(offer['W'].pop(), x[0])
                self.accept_partial(offer['K'].pop(), x[1])
            except (KeyError):
                if 'W' in offer:
                    objective = lambda x: - (self.sales_price_consumption_good
                                            * (self.possession('W') + x) ** self.exponents['W']
                                            - x * offer['W'][-1]['price']
                                        )
                    res = minimize_scalar(
                                objective,
                                method='bounded',
                                bounds=(0, offer['W'][-1]['quantity'])
                    )
                    quantity = min(res.x, self.possession('money') / offer['W'][-1]['price'])
                    self.accept_partial(offer['W'].pop(), quantity)
                if 'K' in offer:
                    objective = lambda x: - (self.sales_price_consumption_good
                                            * (self.possession('K') + x) ** self.exponents['K']
                                            - x * offer['K'][-1]['price']
                                        )
                    res = minimize_scalar(
                            objective,
                            method='bounded',
                            bounds=(0, offer['K'][-1]['quantity'])
                    )
                    quantity = min(res.x, self.possession('money') / offer['K'][-1]['price'])
                    self.accept_partial(offer['K'].pop(), quantity)
            offer = dict([(key, value) for key, value in offer.items() if len(value) > 0])





