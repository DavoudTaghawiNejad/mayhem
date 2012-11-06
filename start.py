from __future__ import division
import sys
sys.path.append('../abce/lib')
from upfirm import UpFirm
from downfirm import DownFirm
from household import Household
from abce import *


for simulation_parameters in read_parameters('simulation_parameters.csv'):
    s = Simulation(simulation_parameters)
    action_list = [
        ('downfirm', 'age_captial'),

        ('upfirm', 'labor_market_info_to_auctioneer'),
        ('household', 'labor_auctioneer'),
        ('upfirm', 'hire_labor'),
        ('household', 'supply_labor'),
        ('upfirm', 'production'),
        ('all', 'sell_captial'),
        ('downfirm', 'buy_captial'),
        ('downfirm', 'production'),

        ('downfirm', 'consumer_good_to_auctioneer'),
        ('household', 'consumer_good_auctioneer'),
        ('downfirm', 'sell_consumer_good'),
        ('household', 'buy_consumer_good'),

        ('downfirm', 'update_expected_price'),

        ('upfirm', 'learn'),
    ]
    s.add_action_list(action_list)

    s.build_agents_from_file(UpFirm)
    s.build_agents_from_file(DownFirm)
    s.build_agents_from_file(Household)

    s.declare_round_endowment(resource='labor_endowment', productivity=24, product='labor')
    #Every round every consumer gets 24 units of hours. (if he created 1 time in __init__)

    s.declare_perishable(good='labor')
    for i in range(10):
        s.declare_perishable(good='K%i' % i)

    # s.debug_subround()

    s.run()

