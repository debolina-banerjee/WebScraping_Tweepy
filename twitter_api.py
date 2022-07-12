#from matplotlib.style import use
import tweepy
import datetime
import time
from datetime import datetime
import unicodedata

def utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset

output = []
def tweetSearch(search_query, t_api):
    try:
        tweets_list = tweepy.Cursor(t_api.search_tweets, q=search_query, tweet_mode='extended', lang='en', include_entities=True).items()
        # output = []
        for tweet in tweets_list:
            if (not tweet.retweeted) and ('RT @' not in tweet.full_text):
                text = (unicodedata.normalize('NFKD', tweet.full_text))
                print(text)  
                print("==="*45)           
                user = (unicodedata.normalize('NFKD', tweet.user.screen_name))
                # userId =  tweet.user.screen_name.id
                # print(userId)   
                like_count = tweet.favorite_count
                retweet_count = tweet.retweet_count
                created_at =str(utc_to_local(tweet.created_at))[:16]
                # location = tweet.user.location.encode('utf-8')
                location = (unicodedata.normalize('NFKD', tweet.user.location))
                print(user)
                if user.lower()==search_query.lower():
                    line = {'CREATED_AT' : created_at, "USER":user,'REVIEW' : text, 'LIKES' : like_count, 'RETWEETS' : retweet_count, 'LOCATION':location}
                    #line = {'created_at' : created_at, "User":user,'text' : text, 'like_count' : like_count, 'retweet_count' : retweet_count, 'location':location}
                    output.append(line)
                time.sleep(1)
    except Exception as e:
        print(f"Got an Error !: {e}")