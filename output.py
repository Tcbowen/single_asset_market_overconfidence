from otree_markets.output import DefaultJSONMarketOutputGenerator,  BaseCSVMarketOutputGenerator

class Overconfidence_Output_Gen(BaseCSVMarketOutputGenerator):
	def get_header(self):
		return ['round_number',
				'group_id',
				'player_id', 
				'pcode',
				'ranking', 
    			'profit', 
    			'total_payoff', 
    			'world_state',
   	 			'signal1_black',
    			'signal1_white',
    			'signal_nature', 
    			'total_black_balls', 
    			'total_white_balls', 
    			'total_black_low',
    			'total_black_high', 
    			'Question_1_payoff_pre',
    			'Question_2_payoff_pre', 
    			'Question_3_payoff_pre', 
   				'Question_1_payoff_post', 
    			'Question_2_payoff_post',
   				'Question_3_payoff_post',
    			'profit', 
    			'payoff_from_trading',
    			'shares',
    			'Question_1_pre',
    			'Question_2_pre',
    			'Question_3_pre', 
   				'Question_1_post', 
    			'Question_2_post',
   				'Question_3_post', 
    			]

	def get_group_output(self, group):
		if group.round_number > group.subsession.config.num_rounds:
			return 
		for player in group.get_players():
			yield [
				group.round_number,
				group.id_in_subsession,
				player.id_in_group,
				player.participant.code,
				player.ranking, 
    			player.profit, 
    			player.total_payoff, 
    			player.world_state,
   	 			player.signal1_black,
    			player.signal1_white,
    			player.signal_nature, 
    			player.total_black, 
    			player.total_white, 
    			player.total_black_low,
    			player.total_black_high, 
    			player.Question_1_payoff_pre,
    			player.Question_2_payoff_pre, 
    			player.Question_3_payoff_pre, 
   				player.Question_1_payoff_post, 
    			player.Question_2_payoff_post,
   				player.Question_3_payoff_post,
    			player.profit, 
    			player.payoff_from_trading,
    			player.shares,
    			player.Question_1_pre,
    			player.Question_2_pre,
    			player.Question_3_pre, 
   				player.Question_1_post, 
    			player.Question_2_post,
   				player.Question_3_post,
			]

output_generators = [DefaultJSONMarketOutputGenerator, Overconfidence_Output_Gen]