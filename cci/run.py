#!/usr/bin/env python3

import time
import cci
import tsn_adapter
from icecream import ic

if __name__ == "__main__":
   adapter = tsn_adapter.TsnAdapter()
   cci = cci.TwitterCci()
   while True:
      jobs = ic(adapter.read_recent_jobs())
      daily_sentiment_cci, weighted_survey_score, combined_cci =  \
        cci.compute_cci("U.S. Economy")
      ic(adapter.write_result(daily_sentiment_cci))
      time.sleep(30)


                
