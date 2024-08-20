#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import time
import cci
import tsn_adapter
from icecream import ic

if __name__ == "__main__":
   adapter = tsn_adapter.TsnAdapter()
   cci = cci.TwitterCci()
   while True:
      jobs = ic(adapter.read_recent_jobs("f235dda4-2a52-4a2c-b8ff-5a963967e464"))
      ic(jobs)
      if len(jobs['result']) > 0:
         jobid = jobs['result'][0]['jobid']
         params = ic(adapter.read_params(jobid))
         daily_sentiment_cci, weighted_survey_score, combined_cci =  \
            cci.compute_cci("U.S. Economy")
         ic(adapter.write_result(daily_sentiment_cci))
         print(f"Social Media Sentiment CCI Score: {daily_sentiment_cci}")
         print(f"Survey CCI Score: {weighted_survey_score}")
         print(f"Combined CCI Score: {combined_cci}")
      time.sleep(5)


                
