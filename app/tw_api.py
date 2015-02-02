# Twitter Mining Examples
import twitter, json

def connect():
	# All my app information
	API_KEY = 'gBr4zEd0m7dnrrFvvlyHZElTi'
	API_SECRET = 'ExNOxlcBCaET2bXsXFWU9VRXnH8FcV6DYauxSGkBHkb5nIifmR'
	TOKEN = '1905706489-GIc3TvvkrCrZyXLdw3mGZbohzmKsrGfVZnkKdpw'
	TOKEN_SECRET = 'R4lGt5efDSJmm0XFC8cQwViRiDQqTGeae8DliMqcWcK4B'
	auth = twitter.oauth.OAuth(TOKEN, TOKEN_SECRET, API_KEY, API_SECRET)
	twitter_api = twitter.Twitter(auth=auth)
	return twitter_api
	
api = connect()

statuses = api.statuses.user_timeline(**{'screen_name': '@bathompso', 'count': 4})
#print(statuses)

#min_id = min([s['id'] for s in statuses])

# Get some more stuff
#for i in range(5):
#	more_statuses = api.statuses.user_timeline(**{'screen_name': username, 'count': 200, 'max_id': min_id})
#	for s in more_statuses: statuses.append(s)
#	min_id = min([s['id'] for s in more_statuses])
		
# Write JSON response to file
#of = open(username+'.json', 'w')
#json.dump(statuses, of)
#of.close()
	
