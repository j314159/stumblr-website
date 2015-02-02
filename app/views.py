from flask import render_template, request
from app import app
from process_tweet_pdf import findcategory
import json
import tw_api
from urllib2 import urlopen, quote
import yelp_api
from datetime import datetime


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
    username = 'Stranger'
    tweet = 'stumbLr is the best app ever! It even fills in the tweet field when I leave it blank! #theater :-)'
    lat = '37.763296'
    lng = '-122.421752'
    chour = datetime.now().hour
    #pull 'ID' from input field and store it
    api = tw_api.connect()
    if request.args.get('username'):
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

    if request.args.get('tweet'):
        tweet = request.args.get('tweet')

    #Find likely category you're talking about
    fc = findcategory()
    category, nextvenue = fc.GetVenueYelp14time(tweet, chour)
    #category = 'restaurants'
    #nextvenue = 'nightlife'
    print ' '
    #category = 'park' #Temp Place Holder'

    #Now find top three venues in the next category
    print category, nextvenue

    categories = ['restaurants', 'shopping', 'beauty & spas', 'nightlife',
      'fitness & instruction', 'fast food', 'hotels', 'arts & entertainment',
      'coffee & tea', 'bakeries', 'ice cream & frozen yogurt', 'jewelry',
      'parks', 'desserts', 'breakfast & brunch', 'drugstores']

    categories_forapi = ['restaurants', 'shopping', 'beautysvc', 'nightlife',
      'fitness', 'hotdogs', 'hotels', 'arts',
      'coffee', 'bakeries', 'icecream', 'jewelry',
      'parks', 'desserts', 'breakfast_brunch', 'drugstores']

    nextvenue_forapi = categories_forapi[categories.index(nextvenue)]

    response = yelp_api.top_five_venues(nextvenue_forapi, 'San Francisco')
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


    return render_template("output.html", tweet = tweet, lat = lat, lng = lng, category = category,\
    username = username, newloc = newloc, nextvenue = nextvenue, maplink = maplink, response = response)


@app.route("/choose", methods=["POST","GET"])
def testpost():

    origin = request.form["origin"]
    origin_name = origin
    destination = request.form["destination"]
    destination_name = destination
    roundtrip = request.form.get('roundtrip')
    if not roundtrip:
        roundtrip = 0
    
    # do geocode with mapquest
    #mquest=mapquest()
    #s1latlng = mquest.revgeo(origin)
    #e1latlng = mquest.revgeo(destination)
    #origin = str(s1latlng[0]) + ',' + str(s1latlng[1])
    #destination = str(e1latlng[0]) + ',' + str(e1latlng[1])

    # geocode with google
    try:
        origin = urllib2.quote(origin)
        geocode_url = "http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false&region=uk" % origin
        req = urllib2.urlopen(geocode_url)
        jsonResponse = json.loads(req.read())
        origin = str(jsonResponse['results'][0]['geometry']['location']['lat']) + ',' + str(jsonResponse['results'][0]['geometry']['location']['lng'])

        destination = urllib2.quote(destination)
        geocode_url = "http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false&region=uk" % destination
        req = urllib2.urlopen(geocode_url)
        jsonResponse = json.loads(req.read())
        destination = str(jsonResponse['results'][0]['geometry']['location']['lat']) + ',' + str(jsonResponse['results'][0]['geometry']['location']['lng'])

        return render_template('index_map.html',origin=origin, destination=destination, roundtrip=roundtrip, origin_name=origin_name, destination_name=destination_name) 

    except:
        return render_template('input.html')
