from otree_markets.pages import BaseMarketPage
from django.contrib.staticfiles.templatetags.staticfiles import static
from ._builtin import Page, WaitPage
class Wait_for_trading(WaitPage):
    wait_for_all_groups = True

class Pre_Trading_Survey(Page):
    def get_timeout_seconds(self):
        if self.subsession.round_number<=2:
            return 50
        else:
            return 30
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
    form_fields = ['Question_1_pre', 'Question_2_pre', 'Question_3_pre']


class Market(BaseMarketPage): 
    def get_timeout_seconds(self):
        return self.group.get_remaining_time()
    
    def vars_for_template(self):
        
        img_sig_url = '/static/single_asset_market_overconfidence/signal_{}.jpg'.format(self.player.signal_nature)
        img_url = '/static/single_asset_market_overconfidence/balls2/balls_{}.jpg'.format(self.player.signal1_black)

        r_num = self.subsession.round_number 
        output = "Period Number"
        if r_num>2:
            r_num = r_num -2
        else:
            output = "Practice Period"


        return {
            'round_num_display_string': output, 
            'round_num':r_num,
            'signal1black': self.player.signal1_black,
            'signal1white': self.player.signal1_white,
            'img_url': img_url,
            'img_sig_url': img_sig_url,
        }
class Post_Trading_Survey(BaseMarketPage):
    def get_timeout_seconds(self):
        if self.subsession.round_number<=2:
            return 50
        else:
            return 30
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
    form_fields = ['Question_1_post', 'Question_2_post', 'Question_3_post']

class Wait(WaitPage):
    wait_for_all_groups = True
    
    after_all_players_arrive = 'set_payoffs'
    
class Results(Page):
    def get_timeout_seconds(self):
        if self.subsession.round_number==2:
            return 1000
        else:
            return 30
    def before_next_page(self):
        if self.timeout_happened:
            self.player.save()

    def vars_for_template(self): 
        if self.player.world_state==1:
            state="G"
        elif self.player.world_state==0:
            state="B"

        return {
            'Question_1_pay_post': self.player.Question_1_payoff_post,
            'Question_2_pay_post': self.player.Question_2_payoff_post,
            'Question_3_pay_post': self.player.Question_3_payoff_post,
            'Question_1_pay_pre': self.player.Question_1_payoff_pre,
            'Question_2_pay_pre': self.player.Question_2_payoff_pre,
            'Question_3_pay_pre': self.player.Question_3_payoff_pre,
            'profit': self.player.profit,
            'asset_value': self.player.asset_value,
            'cash_flow': self.player.settled_cash,
            'payoff_from_survey': self.player.survey_avg_pay, 
            'payoff_from_trading': self.player.payoff_from_trading,
            'total_pay':self.player.total_payoff,
            'state': state,
            'shares': self.player.shares
        }


page_sequence = [Pre_Trading_Survey, Wait_for_trading, Market, Post_Trading_Survey, Wait, Results]
