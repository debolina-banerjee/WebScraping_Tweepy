from flask import Flask, render_template, request, send_file, send_from_directory
from werkzeug.utils import secure_filename
import time
import shutil
from io import BytesIO
import zipfile
import os
import nltk
from helper import *
import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# Stopword remove
from nltk.stem import WordNetLemmatizer
nltk.download('stopwords')
nltk.download('omw-1.4')
lemm = WordNetLemmatizer()

from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
sentiments = SentimentIntensityAnalyzer()

from nltk.corpus import stopwords
stopwords = set(stopwords.words('english'))

from nltk.tokenize import TweetTokenizer
tokenzr = TweetTokenizer()

search_query={}



app = Flask(__name__, static_url_path='/static')

upload_folder = os.path.join('static', 'uploadFiles')
app.config['UPLOAD_FOLDER'] = upload_folder
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/download', methods=['GET', 'POST'])
def download():   
    root_dir = "static/uploadFiles"
    filepath = "static/zipFiles/dump_data_summary"
    if os.path.exists(filepath):
        os.remove(filepath)
    shutil.make_archive("static/zipFiles/dump_data_summary", "zip", root_dir)
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    # return render_template('download.html' , filename = 'dump_data_summary.zip')
    return send_file('static/zipFiles/dump_data_summary.zip', as_attachment=True)


@app.route("/show_data",methods=['POST'])
def sentiment_analysis():
    global search_query
    search_query = fetch_tweet(api,request.form.get('search_query'),request.form.get('n_tweets'))
    df = get_df_from_db(search_query)
    if request.method=='POST':
        return render_template('show_data.html' , search_query = request.form['search_query'])
    elif request.method=='GET':
        return render_template('show_data.html')
    else:
        return 'Not allowed'
@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route('/show_data')
def show_data():
    global df
    df = get_target_df_from_db(search_query)
    df = df['target'].value_counts()   
    return render_template('show_data.html', tweets=df.items())

@app.route('/wordcloud', methods=['GET', 'POST'])
def wordcloud():
    df = get_target_df_from_db(search_query)
    url_image = gen_wordcloud(df)
    cloud_image = os.path.join(app.config['UPLOAD_FOLDER'], url_image)
    return render_template('wordcloud.html', url_image=cloud_image)

@app.route('/piechart', methods=['GET', 'POST'])
def piechart():
    df = get_target_df_from_db(search_query)
    url_image = plot_pie_chart(df)
    cloud_image = os.path.join(app.config['UPLOAD_FOLDER'], url_image)
    return render_template('piechart.html', url_image=cloud_image)

if __name__ == '__main__':
    app.run(debug=True)
