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
import os

class Constants(BaseConstants):
    name_in_url = 'single_asset_market_overconfidence'
    players_per_group = None
    num_rounds = 30 
 
    # the columns of the config CSV and their types
    # this dict is used by ConfigManager
    config_fields = {
        'period_length': int,
        'asset_endowment': int,
        'cash_endowment': int,
        'allow_short': bool,
        'sig': int,
        'env': int
    }


class Subsession(markets_models.Subsession):

    @property
    def config(self):
        config_addr = Constants.name_in_url + '/configs/' + self.session.config['config_file']
        return ConfigManager(config_addr, self.round_number, Constants.config_fields)  
    def allow_short(self):
        return self.config.allow_short
    def creating_session(self):

        world_state_binomial = np.random.binomial(1, 0.5) 
        self.set_signal(self.config.env)

        for player in self.get_players():
            ## set the world state for each player equal to the global state
            player.world_state = world_state_binomial 
            ##good state
            if player.world_state == 1:
                if player.signal_nature==1:
                    signal1_blackballs = 4
                else:  
                    signal1_blackballs = 3               
            ##bad state
            if player.world_state == 0:
                if player.signal_nature==1:
                    signal1_blackballs = 1
                else:  
                    signal1_blackballs = 2  
            player.signal1_black = np.random.binomial(2,signal1_blackballs/5) 
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

        if self.round_number > self.config.num_rounds:
            return
        return super().creating_session()
    #######################################################################
    ### sets the players signals 
    ### env, player
    #######################################################################
    def set_signal(self, env):
        if env == 0:
            sig = self.config.sig
            for p in self.get_players():
                p.signal_nature = sig
        else:
            sig = self.config.sig
            i=0
            for p in self.get_players():
                if i%2==0:
                    p.signal_nature = sig
                else: 
                    p.signal_nature = (1-sig)
                i= i+1
    #######################################################################
    ### sets all profits players 
    ### player
    #######################################################################
    def set_profits(self):
         for player in self.get_players():
            player.set_profit()
    #######################################################################
    ### sets the payoff for each player and assigns a ranking
    ### player
    #######################################################################
    def set_payoffs(self):
        ############
        self.set_profits()
        ##sort profit to get ranking 
        rank = []
        for player in self.get_players():
            rank.append(player)
        rank.sort(reverse = True, key = lambda x: x.profit)
        n=1

        for i in range(len(rank)):
            if i>0 and rank[i].profit == rank[i-1].profit:
                rank[i].ranking = rank[i-1].ranking
            else:
                rank[i].ranking = n
            n=n+1

        for p in self.get_players():
            p.set_total_payoff()
    #######################################################################
    ### retuns the total black and white balls in the systems 
    ### player
    #######################################################################
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
    #######################################################################
    ### retuns the total black balls when signal low
    ### player
    #######################################################################
    def get_black_balls_low(self):
        total_black =0
        for p in self.get_players():
            if p.signal_nature==0:
                    total_black = total_black + p.signal1_black

        return total_black
    #######################################################################
    ### retuns the total black balls when signal high
    ### player
    #######################################################################
    def get_black_balls_high(self):
        total_black =0
        for p in self.get_players():
            if p.signal_nature==1:
                    total_black = total_black + p.signal1_black

        return total_black

class Group(markets_models.Group):
    def period_length(self):
        return self.subsession.config.period_length

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
        if enter_msg['price'] >300 or enter_msg['price'] <100:
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
        return (((math.pow(0.6,l) * math.pow(.4,8-l))*(math.pow(.8,h)*math.pow(.2,8-h)))/(((math.pow(.6,l)*math.pow(.4,8-l)*math.pow(.8,h)*math.pow(.2,8-h)) +(math.pow(.4,l)*math.pow(.6,8-l)*math.pow(.2,h)*math.pow(.8,8-h)))))
## defined Variables 
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
    shares = models.IntegerField()
## Questions 
    Question_1 = models.IntegerField(
        label='''
        Your answer:'''
    )

    Question_2_low = models.IntegerField(
        label='''
        (low)
        '''
    )
    Question_2_hi = models.IntegerField(label='''
        (hi):
        ''')

    Question_3 = models.IntegerField(
        choices=[1,2,3,4,5,6,7,8],
        label='''
         Please choose one of the following.
        '''
    )
    #######################################################################
    ### sets the proft for an indivdual player 
    #######################################################################
    def set_profit(self):
        self.shares = self.settled_assets['A']
        if self.world_state==1:
            self.profit =  (self.shares*300 -self.subsession.config.asset_endowment*300 ) + (self.settled_cash - self.subsession.config.cash_endowment)
             ## bad state
        else:
           self.profit =  (self.shares*100-self.subsession.config.asset_endowment*100) + (self.settled_cash - self.subsession.config.cash_endowment)
    #######################################################################
    ### sets the proft for an indivdual player 
    #######################################################################
    def get_profit(self):
        return self.profit
    #######################################################################
    ### calculates payoff
    #######################################################################
    def set_total_payoff(self):
        ###################question 1#######################################
        p_n = random.randint(0,99)
        n_asset_binomail = np.random.binomial(1, p_n/100)
        n_asset_value = n_asset_binomail*200 +100
        if self.Question_1>p_n:
            self.Question_1_payoff = self.world_state*200 +100
        else:
            self.Question_1_payoff = n_asset_value
        #########################Question 2#################################

        L = self.Question_2_low
        U = self.Question_2_hi

        if self.subsession.config.env==1:
            BU = self.BU_env_b(self.total_black_low, self.total_black_high)
        else:
            if self.signal_nature==1:
                BU = self.BU_hi(self.total_black, self.total_white)
             ## bad state
            else:
                BU = self.BU_low(self.total_black, self.total_white)

        if BU>(L/100) and BU<(U/100):
            self.Question_2_payoff= (100-(U-L))
        else:
            self.Question_2_payoff= 0
       ################### ### question 3###################################

        ##C correct ranking
        C = self.ranking
        ##R is the reported belief
        R = self.Question_3
        self.Question_3_payoff= (int) (100 - (math.pow((C - R),2)))

        ## set total payoff ###############################
        self.total_payoff = (int)((self.Question_1_payoff + self.Question_2_payoff +self.Question_3_payoff)/3) + self.profit