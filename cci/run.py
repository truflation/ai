#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import cci
import tsn_adapter

if __name__ == "__main__":
    adapter = tsn_adapter.TsnAdapter()
    cci = cci.TwitterCci()
    def function(params: dict) -> dict:
        if 'text' not in params:
            return {}
        daily_sentiment_cci, weighted_survey_score, combined_cci =  \
            cci.compute_cci(params['text'])
        print(f"Social Media Sentiment CCI Score: {daily_sentiment_cci}")
        print(f"Survey CCI Score: {weighted_survey_score}")
        print(f"Combined CCI Score: {combined_cci}")
        return {
            "social_media_cci": daily_sentiment_cci
        }
    adapter.run_loop(
       "f235dda4-2a52-4a2c-b8ff-5a963967e464",
       function
    )
