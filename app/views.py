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

@app.route('/output')
def output():
    #Set defaults
    username = 'StumbLr'
    tweet = 'stumbLr is the best app ever! It even fills in the tweet field when you leave it blank! #theater :-)'
    lat = '37.763296'
    lng = '-122.421752'
    chour = datetime.now().hour
    #pull 'ID' from input field and store it
    api = tw_api.connect()
    tweet_fail = False
    if request.args.get('username'):
        tweet_fail = True
        try:
            username = request.args.get('username')
            query = api.statuses.user_timeline(**{'screen_name': username, 'count': 10})
            print query[0]
            tweet = query[0]['text']
            lng = str(query[0]['coordinates']['coordinates'][0])
            lat = str(query[0]['coordinates']['coordinates'][1])
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

    if request.args.get('tweet'):
        tweet = request.args.get('tweet')

    #Find likely category you're talking about
    fc = findcategory()
    category, nextvenue = fc.GetVenueYelp14time(tweet, chour)

    #Now find top three venues in the next category
    categories = ['restaurants', 'shopping', 'beauty & spas', 'nightlife',
      'fitness & instruction', 'fast food', 'hotels', 'arts & entertainment',
      'coffee & tea', 'bakeries', 'ice cream & frozen yogurt', 'jewelry',
      'parks', 'desserts', 'breakfast & brunch', 'drugstores']

    categories_forapi = ['restaurants', 'shopping', 'beautysvc', 'nightlife',
      'fitness', 'hotdogs', 'hotels', 'arts',
      'coffee', 'bakeries', 'icecream', 'jewelry',
      'parks', 'desserts', 'breakfast_brunch', 'drugstores']

    nextvenue_forapi = categories_forapi[categories.index(nextvenue)]

    response = yelp_api.top_five_venues(nextvenue_forapi, "San Francisco")
    #nextvenue = response[0]['name']

    if nextvenue:
        newloc = nextvenue
    else:
        newloc = 'coffee'

    maplink = "https://www.google.com/maps/embed/v1/place"
    #maplink += quote(lat+','+lng)
    maplink += "?q="+quote(response[0]['name'])
    #maplink += "?q="+quote(newloc)+'+near+'+lat+','+lng
    #maplink += "&zoom=10"
    maplink += "&key="+credentials["googleplaces"]

    if tweet_fail == True:
        return render_template("fail.html", username = username)
    else:
        return render_template("output.html", tweet = tweet, lat = lat, lng = lng, category = category,\
        username = username, newloc = newloc, nextvenue = nextvenue, maplink = maplink, response = response)


@app.route('/outputmap')
def outputmap():
    #Set defaults
    username = 'StumbLr'
    tweet = 'stumbLr is the best app ever! It even fills in the tweet field when you leave it blank! #theater :-)'
    lat = '37.763296'
    lng = '-122.421752'
    chour = datetime.now().hour
    #pull 'ID' from input field and store it
    api = tw_api.connect()
    tweet_fail = False
    if request.args.get('username'):
        tweet_fail = True
        try:
            username = request.args.get('username')
            query = api.statuses.user_timeline(**{'screen_name': username, 'count': 10})
            print query[0]
            tweet = query[0]['text']
            lng = str(query[0]['coordinates']['coordinates'][0])
            lat = str(query[0]['coordinates']['coordinates'][1])
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

    if request.args.get('tweet'):
        tweet = request.args.get('tweet')

    #Find likely category you're talking about
    fc = findcategory()
    category, nextvenue = fc.GetVenueYelp14time(tweet, chour)

    #Now find top three venues in the next category
    categories = ['restaurants', 'shopping', 'beauty & spas', 'nightlife',
      'fitness & instruction', 'fast food', 'hotels', 'arts & entertainment',
      'coffee & tea', 'bakeries', 'ice cream & frozen yogurt', 'jewelry',
      'parks', 'desserts', 'breakfast & brunch', 'drugstores']

    categories_forapi = ['restaurants', 'shopping', 'beautysvc', 'nightlife',
      'fitness', 'hotdogs', 'hotels', 'arts',
      'coffee', 'bakeries', 'icecream', 'jewelry',
      'parks', 'desserts', 'breakfast_brunch', 'drugstores']

    nextvenue_forapi = categories_forapi[categories.index(nextvenue)]

    response = yelp_api.top_five_venues_ll(nextvenue_forapi, lat, lng)
    #nextvenue = response[0]['name']

    if nextvenue:
        newloc = nextvenue
    else:
        newloc = 'coffee'

    maplink = "https://www.google.com/maps/embed/v1/place"
    #maplink += quote(lat+','+lng)
    maplink += "?q="+quote(response[0]['name'])
    #maplink += "?q="+quote(newloc)+'+near+'+lat+','+lng
    #maplink += "&zoom=10"
    maplink += "&key="+credentials["googleplaces"]

    mapcenter = [lat, lng]
    fc.make_map(mapcenter, response)


    if tweet_fail == True:
        return render_template("fail.html", username = username)
    else:
        return render_template("outputmap.html", tweet = tweet, lat = lat, lng = lng, category = category,\
        username = username, newloc = newloc, nextvenue = nextvenue, maplink = maplink, response = response)
