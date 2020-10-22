from otree_markets.pages import BaseMarketPage
from django.contrib.staticfiles.templatetags.staticfiles import static

class Market(BaseMarketPage):

    def is_displayed(self):
        return self.round_number <= self.subsession.config.num_rounds

    def vars_for_template(self):
        ##load signal
        img_sig_url = static(
            'otree_single_asset_market/signal_{}.jpg'.format(self.player.signal_nature))
        ## load balls
        img_url = static(
            'otree_single_asset_market/balls2/balls_{}.jpg'.format(self.player.signal1_black))
        return {
            'signal1black': self.player.signal1_black,
            'signal1white': self.player.signal1_white,
            'img_url': img_url,
            'img_sig_url': img_sig_url,
        }

page_sequence = [Market]
