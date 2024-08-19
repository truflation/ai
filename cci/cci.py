#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import re
import os
import tweepy
from loguru import logger
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline
import numpy as np
from dotenv import load_dotenv
load_dotenv()

class TwitterCci:
    def __init__(
            self,
            bearer_token = os.environ['TWITTER_TOKEN']):
        self.client =  tweepy.Client(bearer_token=bearer_token)
    @staticmethod
    def clean_tweet(tweet):
        # Remove links, mentions, hashtags, and special characters
        tweet = re.sub(r"http\S+|www\S+|https\S+|@\S+|#\S+|[^A-Za-z0-9\s]+",
                       '', tweet)
        return tweet

    def fetch_tweets(self, query, max_results=100):
        tweets = self.client.search_recent_tweets(
            query=query, tweet_fields=['created_at'],
            max_results=max_results
        )
        filtered_tweets = [
            tweet for tweet in tweets.data if not tweet.text.startswith('RT') and 'http' not in tweet.text
        ]
        return [(self.clean_tweet(tweet.text), tweet.created_at) for tweet in filtered_tweets]

    def calculate_sentiment_scores(self, texts):
        tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment-latest")
        model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment-latest")
        sentiment_classifier = TextClassificationPipeline(model=model, tokenizer=tokenizer)  # Assuming using GPU
    
        sentiment_scores = []
        for text, date in texts:
            result = sentiment_classifier(text)
            sentiment_label = result[0]['label']
            sentiment_score = result[0]['score']
            sentiment_scores.append((sentiment_label, sentiment_score, date))
        return sentiment_scores

    @staticmethod
    def calculate_cci(row):
        score = row['Score']
        label = row['Label']
        if label == 'positive':
            return 100 * (score + 0.5)  # Example scaling
        if label == 'negative':
            return 100 * (1.5 - score)  # Example scaling
        return 100 * score  # Neutral value

    def calculate_combined_cci(self, sentiment_scores, survey_scores):
        sentiment_cci_scores = [
            self.calculate_cci(
                {'Score': score, 'Label': label}
            ) for label, score, _ in sentiment_scores]
        daily_sentiment_cci = np.mean(sentiment_cci_scores)
        combined_cci = (daily_sentiment_cci + survey_scores) / 2
        return daily_sentiment_cci, survey_scores, combined_cci

    def compute_cci(self, query):
        query = f'"{query}" -is:retweet -is:reply -has:links'
        tweets = self.fetch_tweets(query)
        
        # Print tweets and their dates
        for text, date in tweets:
            logger.debug(f"{date}: {text}\n")

        # Calculate sentiment scores
        sentiment_scores = self.calculate_sentiment_scores(tweets)

        # Print sentiment scores
        for label, score, date in sentiment_scores:
            logger.debug(
                f"Sentiment label: {label}, Score: {score}, Date: {date}"
            )

        # Survey data (weights in percentage)
        survey_data = {
            'OECD': {'weight': 1.48, 'score': 98.85863},  # Most recent value for Survey1 (OECD)
            'UofM': {'weight': 4.93, 'score': 68.2},      # Most recent value for Survey2 (UofM)
            'ConferenceBoard': {'weight': 93.60, 'score': 100.4}  # Most recent value for Survey3 (Conference Board)
        }

        # Calculate the weighted survey CCI score
        weighted_survey_score = sum(survey['weight'] * survey['score'] for survey in survey_data.values()) / sum(survey['weight'] for survey in survey_data.values())

        # Calculate and print combined CCI score
        daily_sentiment_cci, survey_scores, combined_cci = \
            self.calculate_combined_cci(
                sentiment_scores, weighted_survey_score
            )
        return daily_sentiment_cci, weighted_survey_score, combined_cci

if __name__ == "__main__":
    import sys
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
    cci = TwitterCci()
    daily_sentiment_cci, weighted_survey_score, combined_cci =  \
        cci.compute_cci("U.S. Economy")
    print(f"Social Media Sentiment CCI Score: {daily_sentiment_cci}")
    print(f"Survey CCI Score: {weighted_survey_score}")
    print(f"Combined CCI Score: {combined_cci}")
