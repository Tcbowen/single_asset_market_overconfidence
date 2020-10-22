from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from .models import Subsession
import random
import numpy
import numpy as np
from django.contrib.staticfiles.templatetags.staticfiles import static



class ReceiveSignal1(Page):
  
    form_model = 'player'
  #  form_fields = ['Prob1']


    def vars_for_template(self):
        ##load signal
        img_sig_url = static(
            'Non_Bayesian_Game_Prob_Elicit/signal_{}.jpg'.format(self.player.signal_nature))
        ## load balls
        img_url = static(
            'Non_Bayesian_Game_Prob_Elicit/balls2/balls_{}.jpg'.format(self.player.signal1_black))
        return {
            'signal1black': self.player.signal1_black,
            'signal1white': self.player.signal1_white,
            'img_url': img_url,
            'img_sig_url': img_sig_url,
        }



page_sequence = [
    ReceiveSignal1,
]
