from flask import Flask, render_template, request
from requests_oauthlib import OAuth1
import requests
import json
import re
import urllib.parse
from datetime import datetime, timedelta, timezone
from dateutil import parser

import dateutil.parser
from authentication import bearer_token
import traceback

def bearer_oauth(r):
    r.headers["Authorization"] = bearer_token
    r.headers["User-Agent"] = "v2TweetLookupPython"
    return r

# def search_tweets():
#     search_query = 'trump'

#     query_tweet_fields = 'created_at,lang,context_annotations,entities'
#     query_user_fields = 'username,profile_image_url,location'

#     url = "https://api.twitter.com/2/tweets/search/recent?query=" + search_query + "&expansions=author_id,referenced_tweets.id&tweet.fields=" + query_tweet_fields + "&user.fields=" + query_user_fields + '&max_results=100'

#     raw_json_tweets = requests.request("GET", url, auth=bearer_oauth).json()
#     print(raw_json_tweets)
#     tweets = []
#     time_posted = ''

#     for i in range(len(raw_json_tweets['data'])):
#         for j in range(len(raw_json_tweets['includes']['users'])):
#             if (raw_json_tweets['data'][i]['author_id'] == raw_json_tweets['includes']['users'][j]['id']
#             #and raw_json_tweets['includes']['users'][j]['profile_image_url'] != None
#             and raw_json_tweets['data'][i]['lang'] == 'en'
#             ):

#                 time_posted = dateutil.parser.isoparse(raw_json_tweets['data'][j]['created_at'])
#                 time_posted = time_posted.strftime('%B %d, %Y %I:%M %p %z')

#                 profile_image = raw_json_tweets['includes']['users'][j]['profile_image_url'] or ''

#                 try:
#                     tweets.append(
#                         {
#                         'tweet_id': raw_json_tweets['data'][i]['id'] or '',
#                         'handle': raw_json_tweets['includes']['users'][j]['username'] or '',
#                         'name': raw_json_tweets['includes']['users'][j]['name'] or '',
#                         'profile_image': profile_image,
#                         'text': raw_json_tweets['data'][i]['text'],
#                         # replace this text with full text from the includes
#                         #'text': raw_json_tweets['data'][i]['text'],
#                         'created_at': time_posted,
#                         'referenced_tweet_id': raw_json_tweets['data'][i]['referenced_tweets'][0]['id']
#                         #,'context_annotations':  raw_json_tweets['data'][j]['context_annotations'],
#                         }
#                     )
#                 except:
#                     print('thats problematic')
#         try:
#             if raw_json_tweets['data'][i]['referenced_tweets'][0]['type'] == 'retweeted':
#                 for j in range(len(raw_json_tweets['includes']['tweets'])):
#                     for k in range(len(tweets)):
#                         #if raw_json_tweets['data'][i]['referenced_tweets'][0]['id'] == raw_json_tweets['includes']['tweets'][j]['id']:
#                         if tweets[k]['referenced_tweet_id'] == raw_json_tweets['data'][i]['referenced_tweets'][0]['id']:
#                             tweets[k]['text'] = '[RETWEET]: ' + raw_json_tweets['includes']['tweets'][j]['text']
#         except:
#             print('no referenced tweets?')

def search_tweets():
    #keywords = request.form.get('search_query')

# def search_tweets():
    keywords = 'test'

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
    print(json_format)

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
                    'time': newtime,
                    'username': raw_json_tweets['includes']['users'][j]['username'],
                    'text': i['text'],
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
                        'time': newtime,
                        'username': raw_json_tweets['includes']['users'][j]['username'],
                        'text': i['text'],
                    })
                    count+=1
    
    print('tweets',count)
    print(tweets)

def get_trending():
    url = 'https://api.twitter.com/1.1/trends/place.json?id=1'
    request = requests.request("GET", url, auth=bearer_oauth).json()
    srcDict = request[0]['trends'][0]
    newDict = {}

    for key in srcDict:
        if (srcDict[key] != None):
            newDict[key] = srcDict[key]

    #print(srcDict)
    maxItem = max(newDict, key=lambda x: newDict['tweet_volume'])
    print(maxItem)
    #newDict = newDict.sort(key=lambda x: x['tweet_volume'])

    #print(json.dumps(srcDict, indent=2))
    #print(json.dumps(request, indent=4))


search_tweets()
#get_trending()
