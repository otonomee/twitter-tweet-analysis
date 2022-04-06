from flask import Flask, render_template, request
from requests_oauthlib import OAuth1
import requests
import json
import re
import urllib.parse
from datetime import datetime
from dateutil import tz
import dateutil.parser
from authentication import bearer_token

app = Flask(__name__)

@app.route('/')
def start():
    if request.method == 'POST':
        search_tweets()
    return render_template('home.html')

def bearer_oauth(r):
    r.headers["Authorization"] = bearer_token
    r.headers["User-Agent"] = "v2TweetLookupPython"
    return r

@app.route('/', methods=['POST'])
def search_tweets():
    keywords = request.form.get('search_query')

    search_query = keywords.strip()
    search_query = re.sub(r"\W+", "", search_query) # only alphanumeric
    search_query = urllib.parse.quote(search_query) # url encode

    highlight_words = keywords.split(' ')

    query_tweet_fields = 'created_at,lang,context_annotations,entities'
    query_user_fields = 'username,profile_image_url,location'

    url = "https://api.twitter.com/2/tweets/search/recent?&query=" + search_query + "%20-is%3Aretweet&expansions=author_id,referenced_tweets.id&tweet.fields=" + query_tweet_fields + "&user.fields=" + query_user_fields + '&max_results=100'

    raw_json_tweets = requests.request("GET", url, auth=bearer_oauth).json()

    tweets = []
    time_posted = ''

    for i in range(len(raw_json_tweets['data'])):
        for j in range(len(raw_json_tweets['includes']['users'])):
            if (raw_json_tweets['data'][i]['author_id'] == raw_json_tweets['includes']['users'][j]['id']
            #and raw_json_tweets['includes']['users'][j]['profile_image_url'] != None
            and raw_json_tweets['data'][i]['lang'] == 'en'
            ):

                
                time_posted = dateutil.parser.isoparse(raw_json_tweets['data'][j]['created_at'])
                time_posted = time_posted.strftime('%B %d, %Y %I:%M %p')

                profile_image = raw_json_tweets['includes']['users'][j]['profile_image_url'] or ''

                try:
                    tweets.append(
                        {
                        'tweet_id': raw_json_tweets['data'][i]['id'] or '',
                        'handle': raw_json_tweets['includes']['users'][j]['username'] or '',
                        'name': raw_json_tweets['includes']['users'][j]['name'] or '',
                        'profile_image': profile_image,
                        'text': " ".join(['<span style="font-weight:500">{}</span>'.format(word) if word.strip() in highlight_words else word for word in raw_json_tweets['data'][i]['text'].split(' ')]),
                        'created_at': time_posted,
                        'referenced_tweet_id': raw_json_tweets['data'][i]['referenced_tweets'][0]['id']
                        #,'context_annotations':  raw_json_tweets['data'][j]['context_annotations'],
                        }
                    )
                except:
                    print('thats problematic')
        try:
            if raw_json_tweets['data'][i]['referenced_tweets'][0]['type'] == 'retweeted':
                for j in range(len(raw_json_tweets['includes']['tweets'])):
                    for k in range(len(tweets)):
                        #if raw_json_tweets['data'][i]['referenced_tweets'][0]['id'] == raw_json_tweets['includes']['tweets'][j]['id']:
                        if tweets[k]['referenced_tweet_id'] == raw_json_tweets['data'][i]['referenced_tweets'][0]['id']:
                            tweets[k]['text'] = '[RETWEET]: ' + raw_json_tweets['includes']['tweets'][j]['text']
        except:
            print('no referenced tweets?')

    return render_template('home.html', tweets=tweets)
    #return tweets[0]

if __name__ == '__main__':
    #get_resource_token()
    app.run(debug=True)
