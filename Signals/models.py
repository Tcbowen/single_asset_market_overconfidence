from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random
import numpy
import numpy as np

author = 'Your name here'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'Non_Bayesian_Game_Prob_Elicit'
    players_per_group = None
    num_rounds = 50


class Subsession(BaseSubsession):
    def creating_session(self):
        for player in self.get_players():

            ## set the world state prob =.5
            world_state_binomial = np.random.binomial(1, 0.5)
            player.world_state = world_state_binomial
            
            if player.world_state == 1:
                if player.signal_nature==1:
                    ##good = 4 black
                    signal1_blackballs = 4
                    
                else:  
                    ##weak
                    ##bad = 2 black
                    signal1_blackballs = 3               
             
            if player.world_state == 0:
                if player.signal_nature==1:
                    ##good = 3 black
                    signal1_blackballs = 1
                else:  
                    ##weak
                    ##bad = 2 black
                    signal1_blackballs = 2
             
            ### Choose two ball from the signal...
            player.signal1_black = np.random.binomial(2,signal1_blackballs/4) ### is this correct
            player.signal1_white = 2-player.signal1_black



class Group(BaseGroup):
    pass


class Player(BasePlayer):
  
    payment_signal1 = models.IntegerField()
   
    world_state = models.IntegerField()
  
    signal1_black = models.IntegerField()
    signal1_white = models.IntegerField()

    signal_nature = models.IntegerField(initial=1)
