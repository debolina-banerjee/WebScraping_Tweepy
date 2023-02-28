from io import BytesIO
import re
import nltk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from nltk.corpus import stopwords
import sqlite3
import base64
import os

from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
sentiments = SentimentIntensityAnalyzer()


# Stopword remove
nltk.download('stopwords')
nltk.download('omw-1.4')

stopwords = set(stopwords.words('english'))

punctuation = '!"$%&\’()*+,-./”/“/:;<=>?[\\]^_`{|}~•@'
def clean_tweet(text):
    if type(text) == np.float:
        return ""
    text = text.lower()
    text = re.sub("'", "", text) # to avoid removing contractions in english
    text = re.sub("@[A-Za-z0-9_]+","", text) # Remove mention
    text = re.sub("#[A-Za-z0-9_]+","", text) # remove hashtags
    text = re.sub(r'http\S+', '', text) # remove htt
    text = re.sub('[()!?]', ' ', text)
    text = re.sub('\[.*?\]',' ', text)
    text = re.sub("[^a-z0-9]"," ", text)
    text = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', text)
    text = re.sub(r'([A-Za-z])\1{2,}', r'\1', text)
    text = re.sub(r'\b\w\b', ' ',text)
    text = " ".join([word for word in text.split(' ') if word not in stopwords])
    text  = "".join([char for char in text if char not in punctuation])
    
    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                "]+", re.UNICODE)
    return re.sub(emoj, '', text)

# Get data from darabase
def get_df_from_db(search_query):
    try:
        conn = sqlite3.connect('Database/Scrapped_data.db')
        c = conn.cursor()
        c.execute(f"""SELECT * FROM {search_query}""")
        df = pd.DataFrame(c.fetchall())
        # print(df.head())
        df.columns = ['CREATED_AT', "USER", 'REVIEW', 'LIKES', 'RETWEETS', 'LOCATION']
        conn.close()
        return df
    except sqlite3.Error as e:
        print(f"Failed to read data from database: {e}")

def assign_sentiment(dframe):
    dframe['Clean_tweet'] = dframe['REVIEW'].apply(lambda x: clean_tweet(x))
    dframe["Positive"] = [sentiments.polarity_scores(i)["pos"] for i in dframe["REVIEW"]]
    dframe["Negative"] = [sentiments.polarity_scores(i)["neg"] for i in dframe["REVIEW"]]
    dframe["Neutral"] = [sentiments.polarity_scores(i)["neu"] for i in dframe["REVIEW"]]
    filepath = "static/uploadFiles/Scrapped_tweets.csv"
    if os.path.exists(filepath):
        os.remove(filepath)
    dframe.to_csv(filepath)
    dframe.drop(columns=['CREATED_AT', 'LIKES', 'RETWEETS', 'LOCATION'], axis=1, inplace=True)
    dframe.drop_duplicates(subset=['REVIEW'] ,keep='first',inplace=True)
    dframe.reset_index(inplace=True, drop=True)
    # dframe['Clean_tweet'] = dframe['REVIEW'].apply(lambda x: clean_tweet(x))
    # dframe["Positive"] = [sentiments.polarity_scores(i)["pos"] for i in dframe["REVIEW"]]
    # dframe["Negative"] = [sentiments.polarity_scores(i)["neg"] for i in dframe["REVIEW"]]
    # dframe["Neutral"] = [sentiments.polarity_scores(i)["neu"] for i in dframe["REVIEW"]]
    return dframe


def categorise(row):  
    if row['Positive'] >  row['Negative'] and row['Positive'] >  row['Neutral'] :
        return 'Positive'
    elif row['Negative'] > row['Neutral']:
        return 'Negative'
    else:
        return 'Neutral'
    
    
def get_target_df(dframe):
    dframe['target'] = dframe.apply(lambda x: categorise(x), axis=1)
    return dframe

def gen_wordcloud(dframe):  
  
    text2 = " ".join(tweet for tweet in dframe.Clean_tweet.astype(str))
    wordcloud = WordCloud(stopwords=stopwords, background_color="white", width=800, height=400).generate(text2)
    img = BytesIO()
    plt.axis("off")
    plt.figure(figsize=(20,10))
    plt.tight_layout(pad=0)
    plt.imshow(wordcloud, interpolation='bilinear')
    wordcloud.to_file('static/uploadFiles/wordcloud.png')
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    return plot_url


def plot_pie_chart(dframe):
    labels =  list(dict(dframe['target'].value_counts()).keys()) # 'Neutral', 'Positive', 'Negative'
    sizes = dframe['target'].value_counts().tolist()
    colors = ['green', 'red', 'cyan']
    img = BytesIO()
    plt.axis("off")
    plt.title('Tweet Sentiment Pie chart')
    plt.figure(figsize=(6,4))
    patches, _ ,_ = plt.pie(sizes,  labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=150)
    plt.legend(patches, labels, loc="best")

    plt.axis('equal')
    plt.savefig('static/uploadFiles/piechart.png')
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    plot_url_pie = base64.b64encode(img.getvalue()).decode('utf8')
    return plot_url_pie
