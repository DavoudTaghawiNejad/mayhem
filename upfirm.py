from __future__ import division
import abceagent
from abcetools import is_zero, is_positive, is_negative, NotEnoughGoods
import random
from cacla import CaclaLearner
import time


class UpFirm(abceagent.Agent, abceagent.Firm):
    def __init__(self, simulation_parameters, agent_parameters, _pass_to_engine):
        abceagent.Agent.__init__(self, *_pass_to_engine)
        self.create('money', 100)
        self.cobb_douglas_exponent = random.uniform(0, 1)
        self.exp = 1 / (self.cobb_douglas_exponent)
        self.sales_price = 1
        self.num_downfirms = simulation_parameters['num_downfirm']

        self.learner = CaclaLearner(1, 20)

        if agent_parameters['type'] == 'K':
            self.set_cobb_douglas('K', 1, {'labor': self.cobb_douglas_exponent})
            self.captial_type = 'K'
        elif agent_parameters['type'] == 'W':
            self.set_cobb_douglas('W', 1, {'labor': self.cobb_douglas_exponent})
            self.captial_type = 'W'
        else:
            SystemExit('wrong captial type in agent_parameters.csv')
        self.learner.set_state([0])
        self.begin_money = self.possession('money')

    def labor_market_info_to_auctioneer(self):
        """ sends it's cobb_douglas_exponent and sales_price ot the auctioneer """
        self.sales_price = 1.1
        self.cobb_douglas_exponent = 1.1
        self.message('household', 0, 'upfirm_sales_price', self.sales_price)
        self.message('household', 0, 'cobb_douglas_exponent', self.cobb_douglas_exponent)

    def hire_labor(self):
        """ hires as much labor as supplied, which is profit maximizing for the  """
        price = self.get_messages('labor_supply')[0].content
        quantity = (self.cobb_douglas_exponent * self.sales_price / price) ** self.exp
        try:
            self.buy('household', 0, 'labor', quantity, price)
        except NotEnoughGoods:
            self.buy('household', 0, 'labor', self.possession('money') / price, price)

    def sell_captial(self):
        actions = self.learner.get_action()
        actions = actions.reshape((10, 2))
        for action in actions:
            price = float(action[0]) * 10
            quantity = min(float(action[1]) * self.possession(self.captial_type), self.possession(self.captial_type))
            if price > 0:
                rnd = random.randint(0, self.num_downfirms)
                try:
                    self.sell('downfirm', rnd, self.captial_type, quantity, price)
                except:
                    self.sell('downfirm', rnd, self.captial_type, self.possession(self.captial_type), price)


    def production(self):
        """ produces all he can """
        self.log_value('labor_before_production', self.possession('labor'))
        self.log('production', self.produce_use_everything())

    def learn(self):
        self.learner.set_state([0])
        self.learner.give_reward(self.possession('money') - self.begin_money)
        self.learner.learn()
        self.begin_money = self.possession('money')
