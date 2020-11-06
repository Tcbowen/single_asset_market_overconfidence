from otree_markets.pages import BaseMarketPage
from django.contrib.s
taticfiles.templatetags.staticfiles import static
from ._builtin import Page, WaitPage

class Market(BaseMarketPage):
    timeout_seconds = 120
    def before_next_page(self):
        if self.timeout_happened:
            self.player.save()

    #def is_displayed(self):
       # return self.round_number <= self.subsession.config.num_rounds

    def vars_for_template(self):
        ##load signal
        img_sig_url = '/static/single_asset_market_overconfidence/signal_{}.jpg'.format(self.player.signal_nature)
        ## load balls
        img_url = '/static/single_asset_market_overconfidence/balls2/balls_{}.jpg'.format(self.player.signal1_black)
        return {
            'signal1black': self.player.signal1_black,
            'signal1white': self.player.signal1_white,
            'img_url': img_url,
            'img_sig_url': img_sig_url,
        }
class set_profits(WaitPage):
    wait_for_all_groups = True
    
    after_all_players_arrive = 'set_profits'

class Survey(Page):
    timeout_seconds = 30
    def before_next_page(self):
        if self.timeout_happened:
            self.player.save()
    def vars_for_template(self):
            ##load signal
            def before_next_page(self):
                self.player.save()
            #def is_displayed(self):
              #  return self.round_number <= self.subsession.config.num_rounds

<<<<<<< HEAD
            img_sig_url = static(
                'single_asset_market_overconfidence/signal_{}.jpg'.format(self.player.signal_nature))
            ## load balls
            img_url = static(
                'single_asset_market_overconfidence/balls2/balls_{}.jpg'.format(self.player.signal1_black))
=======
            img_sig_url = '/static/single_asset_market_overconfidence/signal_{}.jpg'.format(self.player.signal_nature)
            ## load balls
            img_url = '/static/single_asset_market_overconfidence/balls2/balls_{}.jpg'.format(self.player.signal1_black)
>>>>>>> origin/morgan
            return {
                'signal1black': self.player.signal1_black,
                'signal1white': self.player.signal1_white,
                'profit':self.player.profit,
                'img_url': img_url,
                'img_sig_url': img_sig_url,
            }

    form_model = 'player'
    form_fields = ['Question_1', 'Question_2_low','Question_2_hi', 'Question_3']

class Wait(WaitPage):
    wait_for_all_groups = True
    
    after_all_players_arrive = 'set_payoffs'


page_sequence = [Market,set_profits, Survey, Wait]
