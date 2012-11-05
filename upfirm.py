from __future__ import division
import abceagent
from abcetools import is_zero, is_positive, is_negative, NotEnoughGoods
import random


class UpFirm(abceagent.Agent, abceagent.Firm):
    def __init__(self, simulation_parameters, agent_parameters, _pass_to_engine):
        abceagent.Agent.__init__(self, *_pass_to_engine)
        self.create('money', 100)
        self.cobb_douglas_exponent = random.uniform(0, 1)
        self.exp = 1 / (self.cobb_douglas_exponent)
        self.set_cobb_douglas('K%s' % self.idn, 1, {'labor': self.cobb_douglas_exponent})
        self.sales_price = 1

    def labor_market_info_to_auctioneer(self):
        self.sales_price = 1.1
        self.cobb_douglas_exponent = 1.1
        self.message('household', 0, 'upfirm_sales_price', self.sales_price)
        self.message('household', 0, 'cobb_douglas_exponent', self.cobb_douglas_exponent)

    def hire_labor(self):
        price = self.get_messages('labor_supply')[0].content
        quantity = (self.cobb_douglas_exponent * self.sales_price / price) ** self.exp
        try:
            self.buy('household', 0, 'labor', quantity, price)
        except NotEnoughGoods:
            self.buy('household', 0, 'labor', self.possession('money') * price, price)

