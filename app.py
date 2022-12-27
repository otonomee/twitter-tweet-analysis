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

# @app.route('/', methods=['POST'])
# def get_trending():
#     url = 'https://api.twitter.com/1.1/trends/place.json/'
#     request = requests.request("GET", url, auth=bearer_oauth).json()
#     print(json.dumps(request))


@app.route('/', methods=['POST'])
def search_tweets():
    keywords = request.form.get('search_query')

# def search_tweets():
#     keywords = 'test'

    search_query = keywords.strip()
    search_query = re.sub(r"\W+", "", search_query) # only alphanumeric
    search_query = urllib.parse.quote(search_query) # url encode

    highlight_words = keywords.split(' ')

    query_tweet_fields = 'created_at,lang,source'
    query_user_fields = 'username,profile_image_url,location'

    url = "https://api.twitter.com/2/tweets/search/recent?&query=" + search_query + "&expansions=author_id,referenced_tweets.id&tweet.fields=" + query_tweet_fields + "&user.fields=" + query_user_fields + '&max_results=100'

    raw_json_tweets = requests.request("GET", url, auth=bearer_oauth).json()

    json_format = json.dumps(raw_json_tweets, indent=2)
    tweets = []
    time_posted = ''
    count=0
    #print(json_format)

    for i in raw_json_tweets['data']:
        for j in range(len(raw_json_tweets['includes']['users'])):
            #print(raw_json_tweets['includes']['users'][j]['id'])
            #print(i['author_id'])
            if (i['author_id'] == raw_json_tweets['includes']['users'][j]['id']):
                time = str(dateutil.parser.parse(i['created_at']))
                hr = str(int(time[11:13])-7)
                newtime = "%s %s:%s " % (time[0:10], hr, time[14:])
                tweets.append({
                    'author_id': i['author_id'],
                    'created_at': newtime,
                    'username': raw_json_tweets['includes']['users'][j]['username'],
                    'name': raw_json_tweets['includes']['users'][j]['name'],
                    'profile_image_url': raw_json_tweets['includes']['users'][j]['profile_image_url'],
                    'text': " ".join(['<span style="font-weight:500">{}</span>'.format(word) if word.strip().lower() in highlight_words else word for word in i['text'].split(' ')]),
                })
                count+=1
    print('tweets',count)
    print(tweets)

    next_token = raw_json_tweets['meta']['next_token']

    firstrun = True
    for i in range(5):
        if firstrun:
            newquery = "https://api.twitter.com/2/tweets/search/recent?&query=" + search_query + "&expansions=author_id,referenced_tweets.id&tweet.fields=" + query_tweet_fields + "&user.fields=" + query_user_fields + '&max_results=100&next_token=' + next_token
            next_json_tweets = requests.request("GET", newquery, auth=bearer_oauth).json()
            next_loop_token = next_json_tweets['meta']['next_token']
            firstrun = False
        else:
            newquery = "https://api.twitter.com/2/tweets/search/recent?&query=" + search_query + "&expansions=author_id,referenced_tweets.id&tweet.fields=" + query_tweet_fields + "&user.fields=" + query_user_fields + '&max_results=100&next_token=' + next_loop_token
            next_json_tweets = requests.request("GET", newquery, auth=bearer_oauth).json()
            next_loop_token = next_json_tweets['meta']['next_token']
        
        for i in next_json_tweets['data']:
            for j in range(len(next_json_tweets['includes']['users'])):
                #print(next_json_tweets['includes']['users'][j]['id'])
                #print(i['author_id'])
                if (i['author_id'] == next_json_tweets['includes']['users'][j]['id']):
                    time = str(dateutil.parser.parse(i['created_at']))
                    hr = str(int(time[11:13])-7)
                    newtime = "%s %s:%s " % (time[0:10], hr, time[14:])
                    tweets.append({
                        'author_id': i['author_id'],
                        'created_at': newtime,
                        'username': next_json_tweets['includes']['users'][j]['username'],
                        'name': next_json_tweets['includes']['users'][j]['name'],
                        'profile_image_url': next_json_tweets['includes']['users'][j]['profile_image_url'],
                        'text': " ".join(['<span style="font-weight:500">{}</span>'.format(word) if word.strip().lower() in highlight_words else word for word in i['text'].split(' ')]),
                        
                    })
                    count+=1
    
    # print('tweets',count)
    # print(tweets)

    #return tweets

    #print(tweets)
    return render_template('home.html', tweets=tweets)
    #return tweets[0]

if __name__ == '__main__':
    #get_resource_token()
    app.run(debug=True)
