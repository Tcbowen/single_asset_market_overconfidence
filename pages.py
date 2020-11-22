from otree_markets.pages import BaseMarketPage
from django.contrib.staticfiles.templatetags.staticfiles import static
from ._builtin import Page, WaitPage

class Market(BaseMarketPage):

    def vars_for_template(self):
        
        img_sig_url = '/static/single_asset_market_overconfidence/signal_{}.jpg'.format(self.player.signal_nature)
        img_url = '/static/single_asset_market_overconfidence/balls2/balls_{}.jpg'.format(self.player.signal1_black)

        return {
            'signal1black': self.player.signal1_black,
            'signal1white': self.player.signal1_white,
            'img_url': img_url,
            'img_sig_url': img_sig_url,
        }

class Survey(Page):
    timeout_seconds = 30
    def before_next_page(self):
        if self.timeout_happened:
            self.player.save()

    def vars_for_template(self):
            
            def before_next_page(self):
                self.player.save()
    
            img_sig_url = '/static/single_asset_market_overconfidence/signal_{}.jpg'.format(self.player.signal_nature)
            img_url = '/static/single_asset_market_overconfidence/balls2/balls_{}.jpg'.format(self.player.signal1_black)

            return {
                'signal1black': self.player.signal1_black,
                'signal1white': self.player.signal1_white,
                'img_url': img_url,
                'img_sig_url': img_sig_url,
            }

    form_model = 'player'
    form_fields = ['Question_1', 'Question_2_low','Question_2_hi', 'Question_3']

class Wait(WaitPage):
    wait_for_all_groups = True
    
    after_all_players_arrive = 'set_payoffs'
    
class Results(Page):

    timeout_seconds = 15
    def before_next_page(self):
        if self.timeout_happened:
            self.player.save()

    def vars_for_template(self): 
        if self.player.world_state==1:
            state="Good"
        elif self.player.world_state==0:
            state="Bad"

        return {
            'profit': self.player.profit,
            'Question_1_pay': self.player.Question_1_payoff,
            'Question_2_pay': self.player.Question_2_payoff,
            'Question_3_pay': self.player.Question_3_payoff,
            'total_pay':self.player.total_payoff,
            'state': state
        }


page_sequence = [Market, Survey, Wait, Results]
