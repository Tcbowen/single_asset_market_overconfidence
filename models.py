from otree.api import (
    models, BaseConstants
)
from otree_markets import models as markets_models
from otree_markets.exchange.base import Order, OrderStatusEnum
from .configmanager import ConfigManager

import random
import numpy
import itertools
import numpy as np
import math

class Constants(BaseConstants):
    name_in_url = 'single_asset_market_overconfidence'
    players_per_group = None
    num_rounds = 20 
    ## sets the trading env (0=a, 1=b and c)
    env = 0


    # the columns of the config CSV and their types
    # this dict is used by ConfigManager
    config_fields = {
        'period_length': int,
        'asset_endowment': int,
        'cash_endowment': int,
        'allow_short': bool,
    }


class Subsession(markets_models.Subsession):

    @property
    def config(self):
        config_addr = Constants.name_in_url + '/configs/' + self.session.config['config_file']
        return ConfigManager(config_addr, self.round_number, Constants.config_fields)
    
    def allow_short(self):
        return self.config.allow_short

    def set_signal(self, env):
    	if env == 0:
    		sig = random.choice([0, 1])## ramdomly chooses low or high for the round
    		for p in self.get_players():
    			p.signal_nature = sig
    	else:
    		sig = itertools.cycle([0, 1])
    		for g in self.get_groups():
    			signal = next(sig)
    			for p in g.get_players():
    				p.signal_nature = signal
    def set_profits(self):
         for player in self.get_players():
            player.set_profit()
    def set_payoffs(self):
        ############
        ##sort profit to get ranking 
        rank = []
        for player in self.get_players():
            rank.append(player)
        rank.sort(reverse = True, key = lambda x: x.profit)
        n=1
        for r in rank:
            r.ranking = n
            n=n+1
        ####################
        for p in self.get_players():
            p.set_total_payoff()
    def get_black_balls(self):
    	total_black =0
    	for p in self.get_players():
    		total_black = total_black+p.signal1_black
    	return total_black
    def get_white_balls(self):
    	total_white =0
    	for p in self.get_players():
    		total_white = total_white+p.signal1_white
    	return total_white
    def get_black_balls_low(self):
    	total_black =0
    	for p in self.get_players():
    		if p.signal_nature==0:
    				total_black = total_black + p.signal1_black
    	return total_black
    def get_black_balls_high(self):
    	total_black =0
    	for p in self.get_players():
    		if p.signal_nature==1:
    				total_black = total_black + p.signal1_black
    	return total_black
    def creating_session(self):
        ## world state (0=bad, 1=good)
        ## set the global world state
        world_state_binomial = np.random.binomial(1, 0.5) 
        ## set signal 
        self.group_randomly()
        self.set_signal(Constants.env)
        for player in self.get_players():
            ## set the world state for each player equal to the global state
            player.world_state = world_state_binomial 
            ##good state
            if player.world_state == 1:
                if player.signal_nature==1:
                    ##hi = 4 black
                    signal1_blackballs = 4
                else:  
                    ##low = 2 black
                    signal1_blackballs = 3               
            ##bad state
            if player.world_state == 0:
                if player.signal_nature==1:
                    ##hi = 3 black
                    signal1_blackballs = 1
                else:  
                    ##low = 2 black
                    signal1_blackballs = 2  
            ### cacluated the black balls to be shown using binomial distribution
            player.signal1_black = np.random.binomial(2,signal1_blackballs/5) 
            ## white balles = 2-black
            player.signal1_white = 2-player.signal1_black
        ### get totals 
        total_black = self.get_black_balls()
        total_white = self.get_white_balls()
        total_black_low = self.get_black_balls_low()
        total_black_high= self.get_black_balls_high()
        for player in self.get_players():
            player.total_black = total_black
            player.total_white = total_white
            player.total_black_low = total_black_low
            player.total_black_high = total_black_high
        ## create market sesssion
        if self.round_number > self.config.num_rounds:
            return
        return super().creating_session()


class Group(markets_models.Group):

    def _on_enter_event(self, event):
        '''handle an enter message sent from the frontend
        
        first check to see if the new order would cross your own order, sending an error if it does
        '''
        enter_msg = event.value
        asset_name = enter_msg['asset_name'] if enter_msg['asset_name'] else markets_models.SINGLE_ASSET_NAME

        exchange = self.exchanges.get(asset_name=asset_name)
        if enter_msg['is_bid']:
            best_ask = exchange._get_best_ask()
            if best_ask and best_ask.pcode == enter_msg['pcode'] and enter_msg['price'] >= best_ask.price:
                self._send_error(enter_msg['pcode'], 'Cannot enter a bid that crosses your own ask')
                return
        else:
            best_bid = exchange._get_best_bid()
            if best_bid and best_bid.pcode == enter_msg['pcode'] and enter_msg['price'] <= best_bid.price:
                self._send_error(enter_msg['pcode'], 'Cannot enter an ask that crosses your own bid')
                return
        super()._on_enter_event(event)

    def confirm_enter(self, order):
        exchange = order.exchange
        try:
            # query for active orders in the same exchange as the new order, from the same player
            old_order = (
                exchange.orders
                    .filter(pcode=order.pcode, is_bid=order.is_bid, status=OrderStatusEnum.ACTIVE)
                    .exclude(id=order.id)
                    .get()
            )
        except Order.DoesNotExist: 
            pass
        else:
            # if another order exists, cancel it
            exchange.cancel_order(old_order.id)

        super().confirm_enter(order)

class Player(markets_models.Player):

    def check_available(self, is_bid, price, volume, asset_name):
        '''instead of checking available assets, just check settled assets since there can
        only ever be one bid/ask on the market from each player
        '''
        if is_bid and self.settled_cash < price * volume:
            return False
        elif not is_bid and self.settled_assets[asset_name] < volume:
            return False
        return True

    def asset_endowment(self):
        return self.subsession.config.asset_endowment
    
    def cash_endowment(self):
        return self.subsession.config.cash_endowment

## Bayes methods
    def BU_low(self, k, m ):
        return (math.pow(0.6,k) + math.pow(.4,m))/((math.pow(.6,k) + math.pow(.4,m)) +(math.pow(.4,k) + math.pow(.6,m)))
    def BU_hi(self, k, m ):
        return (math.pow(0.8,k) + math.pow(.2,m))/((math.pow(.8,k) + math.pow(.2,m)) +(math.pow(.2,k) + math.pow(.8,m)))

    def BU_env_b(self, l, h ):
        return (((math.pow(0.6,l) * math.pow(.4,8-l)) + (math.pow(.8,h)*math.pow(.2,8-h)))/(((math.pow(.6,l)*math.pow(.4,8-l)*math.pow(.8,h)*math.pow(.2,8-h)) +(math.pow(.4,l)*math.pow(.6,8-l)*math.pow(.2,h)*math.pow(.4,8-h)))))

## Variables 
    ranking = models.IntegerField()
    profit = models.IntegerField()
    total_payoff = models.IntegerField()
    payment_signal1 = models.IntegerField()
    world_state = models.IntegerField()
    signal1_black = models.IntegerField()
    signal1_white = models.IntegerField()
    signal_nature = models.IntegerField()
    total_black = models.IntegerField()
    total_white = models.IntegerField()
    total_black_low = models.IntegerField()
    total_black_high = models.IntegerField()
    Question_1_payoff = models.IntegerField()
    Question_2_payoff = models.IntegerField()
    Question_3_payoff = models.IntegerField()
    payoff_from_assets = models.IntegerField()
## Questions 
    Question_1 = models.IntegerField(
        label='''
        After the trading, you should have a better idea of what is the true state of the wolrd in this
        this trading period. Please use the infromation to the right hand side to answer the 
        following question truthfully. 

        What is the probailty( out of 100) that you believe the true state is 'G'?

        Your answer:'''
    )

    Question_2_low = models.IntegerField(
        label='''
        Please provide an interval that you are 87.5 onfident that the computer's 
        prediction of the true state is 'G' falls into. Again please answer the queastion
        truthfully.

        your answer:

        (low)
        '''
    )
    Question_2_hi = models.IntegerField(label='''
        (hi):
        ''')

    Question_3 = models.IntegerField(
    	choices=[1,2,3,4,5,6,7,8],
        label='''
        How would you rank your own performance in this trading period? in another worlds, what is the beleive of your own
        ranking of your profit in this period. Please choose one of the following. 
        '''
    )

    def set_profit(self):
        shares = list(self.settled_assets.values())[0]
        if self.world_state==1:
            self.profit =  shares*300 - (self.subsession.config.cash_endowment - self.settled_cash)
             ## bad state
        else:
           self.profit =  shares*100 - (self.subsession.config.cash_endowment - self.settled_cash) 
        ### return the ranking of a player and set ranking
    def get_profit(self):
        return self.profit

    def set_total_payoff(self):
        ## question 1#######################################

        p_n = random.randint(0,99)
        n_asset_binomail = np.random.binomial(1, p_n/100)
        n_asset_value = n_asset_binomail*200 +100
        if self.Question_1>p_n:
            self.Question_1_payoff = self.world_state*200 +100
        else:
            self.Question_1_payoff = n_asset_value

        #####Question 2#################################
        L = self.Question_2_low
        U = self.Question_2_hi
        if Constants.env==1:
            BU = self.BU_env_b(self.total_black_low, self.total_black_high)
        else:
            if self.world_state==1:
                BU = (int) (self.BU_hi(self.total_black, self.total_white))
             ## bad state
            else:
                BU = (int) (self.BU_low(self.total_black, self.total_white))
        if BU>L and BU<U:
            self.Question_2_payoff= (1-(U-L))
        else:
            self.Question_2_payoff= 0

        ### question 3###################################

        ##C correct ranking
        C = self.ranking
        ##R is the reported belief
        R = self.Question_3
        self.Question_3_payoff= (int) (1.2 - (1/50)*(math.pow((C - R),2)))

        ##payoff from assets#############################################
        ## 10,000 - cost of shares pruchased + procceds from sales
        self.payoff_from_assets = self.settled_cash - self.subsession.config.cash_endowment

        ##final portfolio value########################################

        shares = list(self.settled_assets.values())[0]

        if self.world_state == 1:
            multiplier =300
        else:
            multiplier =100
        ##number of shares * multiplier 

        portfolio_value = shares*multiplier

        ## payoff_from_assets#############################
        ### adds cash to the values of shares purchased 
        self.payoff_from_assets = self.payoff_from_assets + portfolio_value

        ## set total payoff ###############################
        
        self.total_payoff = (int)((self.Question_1_payoff + self.Question_2_payoff +self.Question_3_payoff)/3) + self.payoff_from_assets