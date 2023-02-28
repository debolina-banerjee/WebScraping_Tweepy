import tweepy
import datetime
import time
from datetime import datetime
import unicodedata
from config import *
import pandas as pd
import numpy as np
import sqlite3
import nltk
import matplotlib.pyplot as plt
from helper2 import *


from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
sentiments = SentimentIntensityAnalyzer()

from nltk.corpus import stopwords
stopwords = set(stopwords.words('english'))

from nltk.tokenize import TweetTokenizer
tokenzr = TweetTokenizer()

import warnings
warnings.filterwarnings('ignore')

auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit=True)

def utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset

output = []
def tweetSearch(search_query, t_api, n_tweet):
    try:
        tweets_list = tweepy.Cursor(t_api.user_timeline, screen_name=search_query, tweet_mode='extended').items(n_tweet)
        count = 0
        for tweet in tweets_list:
            if (not tweet.retweeted):
                text = (unicodedata.normalize('NFKD', tweet.full_text))
                print(text)  
                print("==="*45)           
                user = (unicodedata.normalize('NFKD', tweet.user.screen_name))
                   
                like_count = tweet.favorite_count
                retweet_count = tweet.retweet_count
                created_at =str(utc_to_local(tweet.created_at))[:16]
                
                location = (unicodedata.normalize('NFKD', tweet.user.location))
                print(f"user : {user}")
                count += 1
                if user==search_query:                    
                    line = {'CREATED_AT' : created_at, "USER":user,'REVIEW' : text, 'LIKES' : like_count, 'RETWEETS' : retweet_count, 'LOCATION':location}
                    output.append(line)
                time.sleep(1)
        print(count)
    except Exception as e:
        print(f"Got an Error !: {e}")        
        
def get_tweets(search_query, t_api, n_tweets=100):
    tweetSearch(search_query, t_api, n_tweets)
    return output

def fetch_tweet(api, search_query, n_tweets=100):
    while True :
            
        number_of_tweets = int(n_tweets) #int(input("Enter the number of tweets From which you want to search: "))
        tweets_res = get_tweets(search_query,api, number_of_tweets)
        df = pd.DataFrame(tweets_res)  
    
        conn = sqlite3.connect('Database/Scrapped_data.db')
        c = conn.cursor()
        
        c.execute(f"DROP TABLE IF EXISTS {search_query}")
        
        # write the data to a sqlite table
        c.execute(f"""CREATE TABLE IF NOT EXISTS {search_query} (CREATED_AT TEXT, USER TEXT, REVIEW TEXT, LIKES INTEGER, RETWEETS INTEGER, LOCATION TEXT)""")
        df.to_sql(f'{search_query}', conn, if_exists='append', index=False)
        conn.commit()
        conn.close()
        # df['Clean_tweet'] = df['REVIEW'].apply(lambda x: clean_tweet(x))
        # df["Positive"] = [sentiments.polarity_scores(i)["pos"] for i in df["REVIEW"]]
        # df["Negative"] = [sentiments.polarity_scores(i)["neg"] for i in df["REVIEW"]]
        # df["Neutral"] = [sentiments.polarity_scores(i)["neu"] for i in df["REVIEW"]]
        # df.to_csv(f'static/uploadFiles/Scrapped_tweets.csv')
        return search_query

def get_target_df_from_db(search_query):
    df = get_df_from_db(search_query)
    df = assign_sentiment(df)
    df = get_target_df(df)
    return df
