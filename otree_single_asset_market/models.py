from otree.api import (
    models, BaseConstants
)
from otree_markets import models as markets_models
from .configmanager import ConfigManager

import random
import numpy
import numpy as np
import math

class Constants(BaseConstants):
    name_in_url = 'otree_single_asset_market'
    players_per_group = None
    num_rounds = 20 
    env = 1


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
    def set_signal(self, player, sig):
        player.signal_nature = sig

    def creating_session(self):
        ##################################
        #signal code
        ##################################
        sig = 0
        for player in self.get_players():
            ## set the world state good or bad at probabilty of .5
            world_state_binomial = np.random.binomial(1, 0.5)
            player.world_state = world_state_binomial
            ## set signal 
            if Constants.env == 0:
            ## env a ## 1==hi, 0==low
                self.set_signal(player, sig)
            ## env b #### ##################### not 50/50 just random. is this correct
            elif Constants.env == 1:
                sig = np.random.randint(0,high = 2)
                self.set_signal(player,sig)
            else:
                ## env c
                sig = np.random.randint(0,high = 2)
                self.set_signal(player,sig)
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
        if self.round_number > self.config.num_rounds:
            return
        return super().creating_session()


class Group(markets_models.Group):

    def set_total_payoff(self):
        for p in self.get_players():
            p.set_total_payoff()


class Player(markets_models.Player):

    def asset_endowment(self):
        return self.subsession.config.asset_endowment
    
    def cash_endowment(self):
        return self.subsession.config.cash_endowment

## Bayes
    def BU_hi(self, k, m ):
        return (math.pow(0.6,k) + math.pow(.4,m))/((math.pow(.6,k) + math.pow(.4,m)) +(math.pow(.4,k) + math.pow(.6,m)))
    def BU_low(self, k, m ):
        return (math.pow(0.8,k) + math.pow(.2,m))/((math.pow(.8,k) + math.pow(.2,m)) +(math.pow(.2,k) + math.pow(.8,m)))
    def BU_env_b(self, l, h ):
        return (((math.pow(0.6,l) * math.pow(.4,8-l)) + (math.pow(.8,h)*math.pow(.2,8-h)))/(((math.pow(.6,l)*math.pow(.4,8-l)*math.pow(.8,h)*math.pow(.2,8-h)) +(math.pow(.4,l)*math.pow(.6,8-l)*math.pow(.2,h)*math.pow(.4,8-h)))))

## Variables 
    total_payoff = models.IntegerField()
    payment_signal1 = models.IntegerField()
    world_state = models.IntegerField()
    signal1_black = models.IntegerField()
    signal1_white = models.IntegerField()
    signal_nature = models.IntegerField()

## Questions 
    Question_1 = models.IntegerField(
        label='''
        After the trading, you should have a better idea of what is the true state of the wolrd in this
        this trading period. Please use the infromation to the right hand side to answer the 
        following question truthfully. 

        \nWhat is the probailty( out of 100) that you believe the true state is 'G'?
        Your answer:'''
    )

    Question_2_low = models.IntegerField(
        label='''
        Please provide an interval that you are 87.5 onfident that the computer's 
        prediction of the true state is 'G' falls into. Again please answer the queastion
        truthfully.

        \nyour answer:

        \n(low)
        '''
    )
    Question_2_hi = models.IntegerField(label='''
        \n (hi):
        ''')

    Question_3 = models.IntegerField(
    	choices=[1,2,3,4,5,6,7,8],
        label='''
        \nHow would you rank your own performance in this trading period? in another worlds, what is the beleive of your own
        ranking of your profit in this period. Please choose one of the following. 
        '''
    )
    def set_total_payoff(self):
        Question_1_payoff = models.IntegerField()
        Question_2_payoff = models.IntegerField() 
        Question_2_payoff = models.IntegerField()
        ## question 1
        p_n = random.randint(0,99)
        n_asset = models.IntegerField()
        if self.Question_1>p_n:
            n_asset = 300
        else:
            n_asset = 100
        Question_1_payoff = n_asset

        #####Question 2
        L = self.Question_2_low
        U = self.Question_2_hi
        if Constants.env>0:
            BU = self.BU_env_b(self.signal1_black, self.signal1_white)
        else:
            if self.world_state==1:
                BU = (int) (self.BU_hi(self.signal1_black, self.signal1_white))
             ## bad state
            else:
                BU = (int) (self.BU_low(self.signal1_black, self.signal1_white))

        if BU>L and BU<U:
            Question_2_payoff= (1-(U-L))
        else:
            Question_2_payoff= 0

        ### question 3
        ##C correct ranking
        C=0
        ##R is the real ranking 
        R=0
        Question_3_payoff =0
        #Question_3_payoff= 1.2 – (1/50)(C – R)^2

        ##payoff from assets
        payoff_from_assets = models.IntegerField()
        payoff_from_assets = 0

        ##+experimental points 
        ##-cost of shares 
        ##proceeds 
        ##the final value of portfolio 


        self.total_payoff = (Question_1_payoff + Question_2_payoff +Question_3_payoff)/3 + payoff_from_assets