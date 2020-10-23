from otree.api import (
    models, BaseConstants
)
from otree_markets import models as markets_models
from .configmanager import ConfigManager

import random
import numpy
import numpy as np

class Constants(BaseConstants):
    name_in_url = 'otree_single_asset_market'
    players_per_group = None
    num_rounds = 20 


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

    def creating_session(self):
        ##################################
        #signal code
        ##################################
        for player in self.get_players():
            ## set the world state good or bad at probabilty of .5
            world_state_binomial = np.random.binomial(1, 0.5)
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
        if self.round_number > self.config.num_rounds:
            return
        return super().creating_session()


class Group(markets_models.Group):
    pass


class Player(markets_models.Player):

    def asset_endowment(self):
        return self.subsession.config.asset_endowment
    
    def cash_endowment(self):
        return self.subsession.config.cash_endowment

    payment_signal1 = models.IntegerField()
   
    world_state = models.IntegerField()
  
    signal1_black = models.IntegerField()
    signal1_white = models.IntegerField()

    signal_nature = models.IntegerField(initial=1)

    Question_1 = models.IntegerField(
        label='''
        After the trading, you should have a better idea of what is the true state of the wolrd in this
        this trading period. Please use the infromation to the right hand side to answer the 
        following question truthfully. 

        What is the probailty( out of 100) that you believe the true state is 'G'?
        Your answer:'''
    )

    Question_2 = models.IntegerField(
        label='''
        Please provide an interval that you are 87.5 onfident that the computer's 
        prediction of the true state is 'G' falls into. Again please answer the queastion
        truthfully.

        your answer:
        '''
    )

    Question_3 = models.IntegerField(
    	choices=[1,2,3,4,5,6,7,8],
        label='''
        How would you rank your own performance in this trading period? in another worlds, what is the beleive of your own
        ranking of your profit in this period. Please choose one of the following. 
        '''
    )