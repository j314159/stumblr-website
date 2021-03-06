import json
import tw_api
import yelp_api
from urllib2 import urlopen, quote
from datetime import datetime
from itertools import islice
from flask import render_template, request
from app import app
from process_tweet_pdf import findcategory

import folium

with open('keys.json') as keyfile:
  credentials = json.load(keyfile)
#passwd = credentials['foursquare']['password']

@app.route('/')

@app.route('/input')
def input():
    return render_template("input.html")

@app.route('/outputmap')
def outputmap():
    #Set defaults
    username = 'StumbLr'
    tweet = 'stumbLr is the best app ever! It even fills in the fields when you leave them blank! #theater :-)'
    lat = '37.763296'
    lng = '-122.421752'
    location = 'San Francisco, CA'
    chour = datetime.now().hour
    #pull 'ID' from input field and store it
    api = tw_api.connect()
    tweet_fail = False
    tweet_ll = False
    if request.args.get('username'):
        tweet_fail = True
        try:
            username = request.args.get('username')
            query = api.statuses.user_timeline(**{'screen_name': username, 'count': 10})
            print query[0]
            tweet = query[0]['text']
            try:
                lng = str(query[0]['coordinates']['coordinates'][0])
                lat = str(query[0]['coordinates']['coordinates'][1])
                tweet_ll = True
            except:
                if request.args.get('location'):
                    location = request.args.get('location')
                tweet_ll = False
            ctime = query[0]['created_at']
            fmt = '%a %b %d %H:%M:%S +%f %Y'
            chour = datetime.strptime(ctime,fmt).hour
            #Assume UTC because twitter doesn't really provide corrected PDT time
            #Also assuming person lives in PDT
            chour = (chour - 8) % 24
            tweet_fail = False
        except:
            tweet = "Could not retrieve your tweet."
            tweet_fail = True
    else:
        #This will overwrite the person's tweet if they also entered twitter username
        if request.args.get('tweet'):
            tweet = request.args.get('tweet')

        #This will overwrite the person's location if they also entered twitter username
        #But it won't matter since it tries looking up ll before location
        if request.args.get('location'):
            location = request.args.get('location')

    #Find likely category you're talking about
    fc = findcategory()
    category, nextvenue = fc.GetVenueYelp14time(tweet, chour)
 
    categories = ['shopping', 'beauty & spas', 'nightlife',
      'fitness & instruction', 'fast food', 'hotels', 'arts & entertainment',
      'bakeries', 'ice cream & frozen yogurt', 'jewelry',
      'parks', 'desserts', 'breakfast & brunch', 'drugstores']

    #Need category names that the Yelp API requires
    categories_forapi = ['shopping', 'beautysvc', 'nightlife',
      'fitness', 'hotdogs', 'hotels', 'arts',
      'bakeries', 'icecream', 'jewelry',
      'parks', 'desserts', 'breakfast_brunch', 'drugstores']

    nextvenue_forapi = categories_forapi[categories.index(nextvenue)]

    if tweet_ll:
        response = yelp_api.top_five_venues_ll(nextvenue_forapi, lat, lng)
    else:
        response = yelp_api.top_five_venues(nextvenue_forapi, location)
    #nextvenue = response[0]['name']

    if tweet_ll:
        tweetcenter = [lat, lng]
    else:
        tweetcenter = False
    mapname = fc.make_map(response, tweetcenter)


    if tweet_fail == True:
        return render_template("fail.html", username = username)
    else:
        return render_template("outputmap.html", tweet = tweet, lat = lat, lng = lng, category = category,\
        username = username, newloc = nextvenue, nextvenue = nextvenue, response = response, mapname=mapname)
