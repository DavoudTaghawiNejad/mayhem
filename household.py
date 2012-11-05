from __future__ import division
import abceagent
from abcetools import is_zero, is_positive, is_negative, NotEnoughGoods
import random
from sympy import *


class Household(abceagent.Agent, abceagent.Household):
    def __init__(self, simulation_parameters, agent_parameters, _pass_to_engine):
        abceagent.Agent.__init__(self, *_pass_to_engine)
        self.create('labor_endowment', 1)
        self.y = random.uniform(0, 1)
        self.price_consumption_good = 1.1

    def labor_auctioneer(self):
        """ 1. does the maximization for each upstream-firm given their expected_sales_prices
        2.  maximizes the representative Household utility function
        3. finds the eqilibrium price and send it to the agents.
        """
        expected_sales_prices = self.get_messages('upfirm_sales_price')
        cd = self.get_messages('cobb_douglas_exponent')
        rng = range(len(expected_sales_prices))

        labor = Symbol('labor')
        p = Symbol('p')

        demand_equations = [
            solve(
                Eq(0,
                    diff(expected_sales_prices[i] * labor ** float(cd[i]) - labor * p,
                    labor)
                ),
            labor)[0]
        for i in rng]

        labor_demand = demand_equations[0]
        for i in rng[1:]:
            labor_demand = Add(labor_demand, demand_equations[i])

        labor = Symbol('labor')
        labor_supply = solve(
                            Eq(0,
                                diff(
                                    (24 - labor) ** self.y * (labor * p / self.price_consumption_good) * (1 - self.y),
                                labor)
                            ),
                        labor)
        equation = Eq(labor_demand, labor_supply[0])
        price = solve(equation, p)
        price = price[1]
        assert price >= 0
        assert price == float(price)
        self.message_to_group('upfirm', 'labor_supply', float(price))

    def supply_labor(self):
        """ recieve the wage and send labor"""
        offers = self.get_offers('labor')
        for offer in offers:
            self.accept(offer)

    def consumer_good_auctioneer(self):
        """ given the supplied quantity of the consumer_good and the representative Household's money,
        calculates the market clearing price and announces it to the downstream firms
        """
        quotes = self.get_messages('consumer_good_quantity')
        quantity = sum([quote.content for quote in quotes])
        self.message_to_group('downfirm', 'consumer_good_demand', quantity / self.possession('money'))

    def buy_consumer_good(self):
        """ recieve consumer_good and give money """
        offers = self.get_offers('consumer_good')
        for offer in offers:
            self.accept(offer)

    def sell_captial(self):
        pass




