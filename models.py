from otree.api import (
    models, BaseConstants
)
from otree_markets import models as markets_models
from otree_markets.exchange.base import Order, OrderStatusEnum
from .configmanager import ConfigManager
from itertools import chain

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
        'state': int,
        'sig_a': int,
        'sig_b_c': int,
        'env': int, 
        'player_1_a': int, 
        'player_2_a': int, 
        'player_3_a': int, 
        'player_4_a': int, 
        'player_5_a': int, 
        'player_6_a': int, 
        'player_7_a': int, 
        'player_8_a': int, 
        'player_1_b_c': int, 
        'player_2_b_c': int, 
        'player_3_b_c': int, 
        'player_4_b_c': int, 
        'player_5_b_c': int, 
        'player_6_b_c': int, 
        'player_7_b_c': int, 
        'player_8_b_c': int
    }


class Subsession(markets_models.Subsession):

    @property
    def config(self):
        config_addr = Constants.name_in_url + '/configs/' + self.session.config['config_file']
        return ConfigManager(config_addr, self.round_number, Constants.config_fields)  
    def allow_short(self):
        return self.config.allow_short
    def creating_session(self):

        self.set_signal(self.config.env)
        self.set_balls_signal(self.config.env)

        for player in self.get_players():
            ## set the world state for each player equal to the global state
            player.world_state = self.config.state

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
            sig = self.config.sig_a
            for p in self.get_players():
                p.signal_nature = sig
        else:
            sig = self.config.sig_b_c
            for p in self.get_players():
                p.signal_nature = sig
    def set_balls_signal(self,env):
            player_bb = self.get_bb_array(env)
            i=0
            for p in self.get_players():
                p.signal1_black = player_bb[i]
                p.signal1_white = 2-p.signal1_black
                i=i+1
    #######################################################################
    ### creates an array of player private signals  
    ### 
    #######################################################################
    def get_bb_array(self, env):
        if env==0:
            return [self.config.player_1_a,self.config.player_2_a, self.config.player_3_a, self.config.player_4_a, 
                    self.config.player_5_a, self.config.player_6_a,self.config.player_7_a, self.config.player_8_a]
        else:
            return [self.config.player_1_b_c,self.config.player_2_b_c, self.config.player_3_b_c, self.config.player_4_b_c, 
                    self.config.player_5_b_c, self.config.player_6_b_c,self.config.player_7_b_c, self.config.player_8_b_c]

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
        
        first check to see if the new order would cross your own order, sending an error if it does.
        this isn't a proper check to see whether it would cross your own order, as it only checks the best
        opposite-side order.
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
        
    #    if player.settled_assets['A'] > 6:
    #        self._send_error(enter_msg['pcode'], 'you cannot purchase more than 6 assets per round')
    #        return
        player = self.get_player(enter_msg['pcode'])
        if player.check_available(enter_msg['is_bid'], enter_msg['price'], enter_msg['volume'], asset_name):
            self.try_cancel_active_order(enter_msg['pcode'], enter_msg['is_bid'], asset_name)
        super()._on_enter_event(event)
        
    
    def _on_accept_event(self, event):
        accepted_order_dict = event.value
        asset_name = accepted_order_dict['asset_name'] if accepted_order_dict['asset_name'] else markets_models.SINGLE_ASSET_NAME

        sender_pcode = event.participant.code
        player = self.get_player(sender_pcode)

        if player.check_available(not accepted_order_dict['is_bid'], accepted_order_dict['price'], accepted_order_dict['volume'], accepted_order_dict['asset_name']):
            self.try_cancel_active_order(sender_pcode, not accepted_order_dict['is_bid'], asset_name)

        super()._on_accept_event(event)
   
    def try_cancel_active_order(self, pcode, is_bid, asset_name):
        exchange = self.exchanges.get(asset_name=asset_name)
        try:
            old_order = exchange.orders.get(pcode=pcode, is_bid=is_bid, status=OrderStatusEnum.ACTIVE)
        except Order.DoesNotExist: 
            pass
        else:
            exchange.cancel_order(old_order.id)
    

class Player(markets_models.Player):


    def check_available(self, is_bid, price, volume, asset_name):
        '''instead of checking available assets, just check settled assets since there can
        only ever be one bid/ask on the market from each player
        '''
        if not is_bid and self.settled_assets[asset_name] < volume:
            return False
        return True
       
    def update_holdings_trade(self, price, volume, is_bid, asset_name):
        if is_bid:
            self.settled_cash -= price * volume

            self.available_assets[asset_name] += volume
            self.settled_assets[asset_name] += volume
        else:
            self.settled_cash += price * volume

            self.available_assets[asset_name] -= volume
            self.settled_assets[asset_name] -= volume

    def asset_endowment(self):
        return self.subsession.config.asset_endowment
    
    def cash_endowment(self):
        return self.subsession.config.cash_endowment

    def update_holdings_available(self, order, removed):
        sign = 1 if removed else -1
        if not order.is_bid:
            self.available_assets[order.exchange.asset_name] += order.volume * sign
            

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
    Question_1_payoff_pre = models.IntegerField(initial=0)
    Question_2_payoff_pre = models.IntegerField(initial=0)
    Question_3_payoff_pre = models.IntegerField(initial=0)
    Question_1_payoff_post = models.IntegerField(initial=0)
    Question_2_payoff_post = models.IntegerField(initial=0)
    Question_3_payoff_post = models.IntegerField(initial=0)
    survey_avg_pay = models.IntegerField()
    profit = models.IntegerField()
    asset_value = models.IntegerField()
    payoff_from_trading = models.IntegerField()
    shares = models.IntegerField()
    average_payoff = models.IntegerField()
## Questions Pre
    Question_1_pre = models.IntegerField(min=0, max=100,
        label='''
        Your answer:'''
    )
    Question_1_post = models.IntegerField(min=0, max=100,
        label='''
        Your answer:'''
    )
    Question_2_pre = models.IntegerField(min=100, max=300,
        label='''
        Enter a number between 100 and 300.'''
    )
    Question_2_post = models.IntegerField(min=100, max=300,
        label='''
        Enter a number between 100 and 300.'''
    )
    Question_3_pre = models.IntegerField(
        choices=[1,2,3,4,5,6,7,8],
        label='''
         Please choose one of the following.
        '''
    )
    Question_3_post = models.IntegerField(
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
        old_asset_value = 0
        if self.world_state==1:
            self.asset_value = self.shares*300
            self.profit = self.asset_value + self.settled_cash
             ## bad state
        else:
            self.asset_value = self.shares*100
            self.profit =  self.asset_value + self.settled_cash
    #######################################################################
    ### sets the proft for an indivdual player 
    #######################################################################
    def get_profit(self):
        return self.profit
    #######################################################################
    ### calculates payoff
    #######################################################################
    def set_total_payoff(self):
        ###################question 1 post#####################################
        p_n_pre = random.randint(0,99)
        n_asset_binomail_pre = np.random.binomial(1, p_n_pre/100)
        n_asset_value_pre = n_asset_binomail_pre*200 +100
        #######################################################################
        p_n_post = random.randint(0,99)
        n_asset_binomail_post = np.random.binomial(1, p_n_post/100)
        n_asset_value_post = n_asset_binomail_post*200 +100
         ################question 1 post#########################################
        if self.Question_1_post>p_n_post:
            self.Question_1_payoff_post = self.world_state*200 +100
        else:
            self.Question_1_payoff_post = n_asset_value_post

        ################question 1 pre#########################################
        if self.Question_1_pre>p_n_pre:
            self.Question_1_payoff_pre = self.world_state*200 +100
        else:
            self.Question_1_payoff_pre = n_asset_value_pre
        ################### ### question 2 post###################################
        p_n = random.randint(100,300)
        if self.Question_2_post>p_n:
            self.Question_2_payoff_post = self.world_state*200 +100
        else:
            self.Question_2_payoff_post = p_n
        ################### ### question 2 pre###################################
        p_n = random.randint(100,300)
        if self.Question_2_pre>p_n:
            self.Question_2_payoff_pre = self.world_state*200 +100
        else:
            self.Question_2_payoff_pre = p_n
        ################### ### question 3 pre###################################
        ##C correct ranking
        C = self.ranking
        ##R is the reported belief
        R = self.Question_3_pre
        self.Question_3_payoff_pre= (int) (100 - (math.pow((C - R),2)))
        ################### ### question 3 post###################################
        ##C correct ranking
        C = self.ranking
        ##R is the reported belief
        R = self.Question_3_post
        self.Question_3_payoff_post= (int) (100 - (math.pow((C - R),2)))
        ### set to zero if did not answer survye questions
        if self.Question_1_pre==0:
            self.Question_1_payoff_pre = 0
        if self.Question_1_post==0:
            self.Question_1_payoff_post = 0
        if self.Question_2_pre==0:
            self.Question_2_payoff_pre = 0
        if self.Question_2_post==0:
            self.Question_2_payoff_post = 0
        if self.Question_3_pre==0:
            self.Question_3_payoff_pre = 0
        if self.Question_3_post==0:
            self.Question_3_payoff_post = 0
        ## set total payoff ###############################
        self.payoff_from_trading = self.profit

        self.survey_avg_pay  = (int)((self.Question_1_payoff_pre + self.Question_2_payoff_pre + self.Question_3_payoff_pre + self.Question_1_payoff_post+self.Question_2_post+ self.Question_3_payoff_post)/6) 
        
        self.total_payoff = self.survey_avg_pay + self.payoff_from_trading

        ## sets payoff to best payoff per round 
        conversion_rate = .0017
        if self.subsession.round_number > 2:
                self.payoff = (self.payoff + (self.total_payoff * conversion_rate))