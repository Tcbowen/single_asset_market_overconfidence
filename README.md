# single_asset_market_overcondfidence

Example session config:

```python
dict(
   name='single_asset_market_overconfidence',
   display_name='Single Asset Market Overconfidence',
   num_demo_participants=2,
   app_sequence=['single_asset_market_overconfidence'],
   config_file='demo.csv',
),
```

Config files are located in the "configs" directory. They're CSVs where each row configures a round of trading. The columns are described below.

* `period_length` - the length of the round in seconds
* `asset_endowment` - the amount of asset each player is endowed with
* `cash_endowment` - the amount of cash each player is endowed with
* `allow_short` - either "true" or "false". if true, players are allowed to have negative cash and asset holdings
