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
        while True:
            self.exp_num = np.random.normal(size=2) + 0.5
            if all(self.exp_num > 0):
                break
        self.exp_num /= np.sum(self.exp_num)
        self.exponents = {}
        self.exponents['W'] = self.exp_num[0]
        self.exponents['K'] = self.exp_num[1]
        print(self.exponents)
        self.set_cobb_douglas('consumer_good', 1, self.exponents)
        self.sales_price_consumption_good = 5

    def age_captial(self):
        """ deletes all captial that should die this round and creates a fake captial K,
        that is the sum of all kapitals
        """
        obsolete = self.possessions_filter(endswith='_%i' % self.round)
        for good in obsolete:
            self.destroy(good, obsolete[good])
        self.create('K', sum([sum(self.possessions_filter(beginswith='K%i_' % i).values()) for i in range(10)]))

    def production(self):
        """ produces consumption good from all its working capital. The maximum
        it can produce is given by the investment_good K he has
        """
        self.log('before_production', self.possessions_all())
        production_maximum = min(self.possession('K') ** self.exponents['K'], self.possession('W'))  # produce the maximum or all you got
        self.log('consumption_good', self.produce({'K': production_maximum, 'W': production_maximum}))

    def consumer_good_to_auctioneer(self):
        """ announces its possession of consumer_good """
        self.message('household', 0, 'consumer_good_quantity', self.possession('consumer_good'))

    def sell_consumer_good(self):
        """ sells all consumer_good for the prices the auctioneer send """
        self.sales_price_consumption_good_consumption_good = self.get_messages('consumer_good_demand')[0].content
        self.sell('household', 0, 'consumer_good', self.possession('consumer_good'), self.sales_price_consumption_good_consumption_good)

    def update_expected_price(self):
        """ dummy for futur experiments """
        self.expected_price_of_consumption_good = self.sales_price_consumption_good_consumption_good

    def sell_captial(self):
        """ 1. take a random price (can be learned)
            2. calculate for this price how much of the good should be sold to maximize profit.
            3. offers to sell the according amount.
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
        if self.idn % 5 == 0:
            print('buy_captial')

        """ buys the profit maximizing amount of captial """
        offers = dict(self.get_offers_all(descending=True))
        while offers:
            offers = dict([(key, value) for key, value in offers.items() if value])
            if 'K' in offers and 'W' in offers:
                objective = lambda x: - (self.sales_price_consumption_good
                                            * (self.possession('W') + x[0]) ** self.exponents['W']
                                            * (self.possession('K') + x[1]) ** self.exponents['K']
                                            - x[0] * offers['W'][-1]['price']
                                            - x[1] * offers['K'][-1]['price']
                                        )
                res = minimize(objective, x0=(2, 0), method='L-BFGS-B', bounds=((0, offers['W'][-1]['quantity']), (0, offers['K'][-1]['quantity'])))
                x = res.x
                print(x)
                try:
                    oo = offers['W'].pop()
                    self.accept_partial(oo, x[0])
                except NotEnoughGoods:
                    self.accept_partial(oo, self.possession('money') / oo['price'])
                try:
                    oo = offers['K'].pop()
                    self.accept_partial(oo, x[1])
                except NotEnoughGoods:
                    self.accept_partial(oo, self.possession('money') / oo['price'])
            else:
                if 'K' in offers:
                    objective = lambda x: - (self.sales_price_consumption_good
                                            * (self.possession('K') + x) ** self.exponents['K']
                                            - x * offers['K'][-1]['price']
                                        )
                    try:
                        res = minimize_scalar(
                                objective,
                                method='bounded',
                                bounds=(0, offers['K'][-1]['quantity'])
                        )
                    except IndexError:
                        print('----', offers['K'], '----')
                        raise
                    quantity = min(res.x, self.possession('money') / offers['K'][-1]['price'])
                    self.accept_partial(offers['K'].pop(), quantity)
                if 'W' in offers:
                    objective = lambda x: - (self.sales_price_consumption_good
                                            * (self.possession('W') + x) ** self.exponents['W']
                                            - x * offers['W'][-1]['price']
                                        )
                    try:
                        res = minimize_scalar(
                                    objective,
                                    method='bounded',
                                    bounds=(0, offers['W'][-1]['quantity'])
                    )
                    except:
                        print '++++', offers
                        raise
                    quantity = min(res.x, self.possession('money') / offers['W'][-1]['price'])
                    self.accept_partial(offers['W'].pop(), quantity)







