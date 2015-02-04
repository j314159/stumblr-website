from nltk.corpus import stopwords
from collections import defaultdict
import nltk.classify
import re
import pickle
import json
import operator
import numpy as np

class findcategory():
	def __init__(self):
		pass


	def ModelIt(self, tweet = 'Default'):
		f = open('stumblr_nb_classifier_yelp.pickle')
		classifier = pickle.load(f)
		f.close()

		category = classifier.classify(self.word_indicator(tweet))
		return category


	def ModelItPDF(self, tweet = 'Default'):
		f = open('stumblr_nb_classifier.pickle')
		classifier = pickle.load(f)
		f.close()

		with open('nextvenuedict.json', 'rb') as fp:
			nextvenuedict = json.load(fp)

		categories = classifier.labels()

		probs = [classifier.prob_classify(self.word_indicator(tweet)).prob(n) for n in categories]
		class_probs = sorted(zip(categories, probs), key=lambda x: x[1], reverse=True)

		for n in range(len(probs)):
		    print (class_probs[n][0]+' accuracy: {0:.2f}%'.format(100 * class_probs[n][1]))

		print ' '

		output_dict = {el:0 for el in nextvenuedict}
		#print len(class_probs)
		for n_current in range(len(class_probs)):
		    currentcat = class_probs[n_current][0]
		    #print currentcat, class_probs[n_current][1]
		    sorted_suggestions = sorted(nextvenuedict[currentcat].items(), key=operator.itemgetter(1), reverse=True)
		    total_suggestions = sum([nextvenuedict[currentcat][nextcat] for nextcat in nextvenuedict[currentcat]])
		    for n_next in range(len(sorted_suggestions)):
		        #print ' ', sorted_suggestions[n_next][0], 1.0*sorted_suggestions[n_next][1]/total_suggestions
		        addprob = (class_probs[n_current][1])*(1.0*sorted_suggestions[n_next][1]/total_suggestions)
		        if sorted_suggestions[n_next][0] in output_dict:
		            output_dict[sorted_suggestions[n_next][0]] += addprob
		        #else:
		            output_dict[sorted_suggestions[n_next][0]] = addprob

		output_probs_sorted = sorted(output_dict, key=lambda key: output_dict[key], reverse=True)

		for n in range(20):
		    print output_probs_sorted[n] + ': {0:.2f}%'.format(100 * output_dict[output_probs_sorted[n]])

		return class_probs[0][0] #, output_probs_sorted[0], 


	def GetVenueYelpCurrent(self, tweet = 'Default'):
		f = open('stumblr_nb_classifier_yelp.pickle')
		classifier = pickle.load(f)
		f.close()

		with open('nextvenue_markov.txt', 'rb') as fp:
			temp = json.load(fp)
		markov = np.array(temp)

		categories = ['restaurants', 'shopping', 'beauty & spas', 'nightlife']

		probs = [classifier.prob_classify(self.word_indicator(tweet)).prob(n) for n in categories]
		print probs
		venue_index = probs.index(max(probs))
		currentvenue = categories[venue_index]

		probs_array = np.array(probs)
		nextvenue_probs = np.dot(probs_array, markov)
		nextvenue_probs = nextvenue_probs.tolist()
		print nextvenue_probs
		nextvenue_index = nextvenue_probs.index(max(nextvenue_probs))

		nextvenue = categories[nextvenue_index]

		return (currentvenue, nextvenue)


	def GetVenueYelp16(self, tweet = 'Default'):
		f = open('stumblr_nb_classifier_yelp16.pickle')
		classifier = pickle.load(f)
		f.close()

		with open('nextvenue_markov16.txt', 'rb') as fp:
			temp = json.load(fp)
		markov = np.array(temp)

		categories = ['restaurants', 'shopping', 'beauty & spas', 'nightlife',
		  'fitness & instruction', 'fast food', 'hotels', 'arts & entertainment',
		  'coffee & tea', 'bakeries', 'ice cream & frozen yogurt', 'jewelry',
		  'parks', 'desserts', 'breakfast & brunch', 'drugstores']

		print categories

		probs = [classifier.prob_classify(self.word_indicator_lemmas(tweet)).prob(n) for n in categories]
		print probs
		venue_index = probs.index(max(probs))
		currentvenue = categories[venue_index]

		probs_array = np.array(probs)
		nextvenue_probs = np.dot(probs_array, markov)
		nextvenue_probs = nextvenue_probs.tolist()
		print 'ONE'
		print nextvenue_probs
		nextvenue_index = nextvenue_probs.index(max(nextvenue_probs))

		nextvenue = categories[nextvenue_index]
		print 'TWO'
		return (currentvenue, nextvenue)

	def GetVenueYelp14time(self, tweet = 'Default', chour = 0):
		f = open('stumblr_nb_classifier_yelp14.pickle')
		classifier = pickle.load(f)
		f.close()

		#Check for day or night time
		if chour >= 5 and chour <= 15:
			with open('nextvenue_markov14_day.txt', 'rb') as fp:
				print "Loading days"
				temp = json.load(fp)
		else:
			with open('nextvenue_markov14_night.txt', 'rb') as fp:
				print "Loading nights"
				temp = json.load(fp)
		markov = np.array(temp)

		categories = ['shopping', 'beauty & spas', 'nightlife',
		  'fitness & instruction', 'fast food', 'hotels', 'arts & entertainment',
		  'bakeries', 'ice cream & frozen yogurt', 'jewelry',
		  'parks', 'desserts', 'breakfast & brunch', 'drugstores']

		probs = [classifier.prob_classify(self.word_indicator_lemmas(tweet)).prob(n) for n in categories]

		#Testing different probs scenarios
		'''probs = [0.07142857142857138, 0.07142857142857138, 0.07142857142857138, 0.07142857142857138,
			     0.149999999999, 0.16, 0.15000000001, 0.20, 
			     0.07142857142857138, 0.07142857142857138, 0.07142857142857138, 0.07142857142857138, 
			     0.07142857142857138, 0.07142857142857138]'''

		print probs

		tol = 0.05
		maxprob = max(probs)
		max_indices = [i for i, prob in enumerate(probs) if maxprob - prob < tol]

		#max_indices = [i for i, x in enumerate(probs) if x == max(probs)]
		#Make sure we some idea where you are (random = 0.07142857142857138)
		if probs[max_indices[0]] >= 0.10:
			if len(max_indices) == 1:
				venue = categories[max_indices[0]]
				currentvenue = "Looks like you've had "+venue+" on your mind."
			elif len(max_indices) == 2:
				venue = []
				for index in max_indices:
					venue += categories[index]
				currentvenue = "Looks like you've had "+categories[max_indices[0]]+" or "+categories[max_indices[1]]+" on your mind."
			else:
				venue = []
				currentvenue = "Looks like you've had "
				count = 0
				for index in max_indices:
					venue = categories[index]
					count += 1
					if count < len(max_indices):
						currentvenue += venue+", "
					else:
						currentvenue += "or "+venue+" on your mind."

			probs_array = np.array(probs)
			nextvenue_probs = np.dot(probs_array, markov)
			nextvenue_probs = nextvenue_probs.tolist()
			#print nextvenue_probs
			nextvenue_index = nextvenue_probs.index(max(nextvenue_probs))

			#Remove possibility of staying where you're at
			if len(max_indices) == 1 and nextvenue_index == max_indices[0]:
				nextvenue_probs[nextvenue_index] = 0
				nextvenue_index = nextvenue_probs.index(max(nextvenue_probs))

			nextvenue = categories[nextvenue_index]

		else:
			currentvenue = "stumbLr couldn't determine what you were thinking about."
			nextvenue = categories[np.random.randint(len(categories))]

		#venue_index = probs.index(max(probs))
		#currentvenue = categories[venue_index]

		return (currentvenue, nextvenue)


	def word_indicator(self, msg, **kwargs):
	    '''
	    Create a dictionary of entries {word: True} for every unique
	    word in a message.

	    Note **kwargs are options to the word-set creator,
	    get_msg_words().
	    '''
	    features = defaultdict(list)
	    msg_words = self.get_textlist(msg, **kwargs)
	    for  w in msg_words:
	            features[w] = True
	    return features

	def get_textlist(self, words):
	    #words = str(existing_tweet[0])
	    
	    # wordpunct_tokenize doesn't split on underscores. We don't
	    # want to strip them, since the token first_name may be informative
	    # moreso than 'first' and 'name' apart. But there are tokens with long
	    # underscore strings (e.g. 'name_________'). We'll just replace the
	    # multiple underscores with a single one, since 'name_____' is probably
	    # not distinct from 'name___' or 'name_' in identifying spam.
	    words = re.sub('_+', '_', words)
	    words = re.sub('\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', words)
	    
	    #Remove links
	    '''links = words[words.find("http://"):]
	    print words
	    print links
	    words = re.sub(links, '', words)'''

	    #words = re.compile(r'[^A-Z^a-z@_]+').split(words)
	    words = re.compile(r'[^A-Z^a-z_]+').split(words)

	    sw = stopwords.words('english')
	    sw.extend(['ll', 've', 'don'])

	    cleaned_words = []
	    for word in words:
	        '''# Get rid of punctuation, tagged users, and single letters.
	        if word!='' and word[0]!='@' and len(word) > 1 and word not in sw:
	            #print word.lower()
	            cleaned_words.append(word)'''
	        # Get rid of punctuation and single letters.
	        if word!='' and len(word) > 1 and word not in sw:
	            #print word.lower()
	            cleaned_words.append(word)
	    return cleaned_words


	def word_indicator_lemmas(self, msg, **kwarg):
	    '''
	    Create a dictionary of entries {word: True} for every unique
	    word in a message.

	    Note **kwargs are options to the word-set creator,
	    get_msg_words().
	    '''
	    lemmas = self.text2lemmas(msg)
	    lemmas_string = " ".join(lemmas)
	    features = self.word_indicator(lemmas_string)
	    return features


	def text2pos(self, string):
	    """
	    Convert text input to part of speech tags.
	    """
	    pos_tags = []

	    # Split string into sentences and operate on each sentence
	    sentences = nltk.sent_tokenize(string)
	    for sentence in sentences:
	        tokens = nltk.word_tokenize(sentence)
	        tokens = [x.lower() for x in tokens]
	        pos_tags.extend(nltk.pos_tag(tokens))

	    return pos_tags



	def pos2lemmas(self, pos_tags):
	    """
	    Return list of word, pos-tags in which each word has been lemmatized.
	    pos_tags is a list of word, pos-tag pairs returned by text2pos.
	    """

	    from nltk.corpus import wordnet as wn

	    # Lemmatizer to use
	    wnl = nltk.stem.WordNetLemmatizer()

	    # mapping of PennTreebank part of speech tags to input for lemmatizer
	    pos_mapper = {'NN':wn.NOUN,'VB':wn.VERB,'JJ':wn.ADJ,'RB':wn.ADV}

	    lemmas = []
	    pos    = []
	    for pair in pos_tags:

	        # Include pos tags when lemmatizing nouns, verbs, adjectives, and adverbs
	        if pair[1][0:2] in pos_mapper.keys():
	            thispos = pos_mapper[pair[1][0:2]]
	            thislemma = wnl.lemmatize(pair[0],thispos)
	        else:
	            thispos = pair[1]
	            thislemma = wnl.lemmatize(pair[0])
	        lemmas.append(thislemma)
	        pos.append(thispos)

	    return (lemmas, pos)


	def handle_negation(self, lemmas,pos):
	    """
	    If "not" or "n't" occurs immediately before a verb or adjective,
	    replace the verb or adjective with not_verb or not_adjective
	    """

	    from nltk.corpus import wordnet as wn

	    # Prepend "not_" to words following "not" or "n't"
	    not_index = []
	    for ii in range(1,len(lemmas)):
	        if (lemmas[ii-1].lower() in ["not","n't"]) & (pos[ii] in [wn.VERB,wn.ADJ]):
	            lemmas[ii] = 'not_' + lemmas[ii]
	            not_index.append(ii-1)
	    
	    # Remove instances of "not" and "n't"
	    lemmas = [value for index,value in enumerate(lemmas) if index not in not_index]
	    pos    = [value for index,value in enumerate(pos) if index not in not_index]

	    return lemmas,pos


	def addNgrams(self, lemmas,pos,N_gram,N_return=20,min_occur=3):
	    """
	    Adds N_return most common N-grams to the lemmas already created.
	    N-grams must occur at least min_occur times.

	    lemmas - list of lemmas as returned by pos2lemmas or handle_negation
	    pos - list of parts of speech as returned by pos2lemmas or handle_negation
	    N_gram - integer (2 or 3 currently supported). return N-grams
	    N_return - Return N_return most common N-grams
	    min_occur - Filter out N-grams that occur less than min_occur times
	    """

	    import pdb

	    from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
	    from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures

	    # Determine whether finding bi or tri grams
	    if N_gram==2: 
	        finder = BigramCollocationFinder.from_words(lemmas)
	        test   = BigramAssocMeasures.chi_sq
	    if N_gram==3: 
	        finder = TrigramCollocationFinder.from_words(lemmas)
	        test   = TrigramAssocMeasures.chi_sq

	    # Find N-grams
	    finder.apply_freq_filter(min_occur)
	    try:
	        ngrams = finder.nbest(test,N_return)
	    except:
	        ngrams = []

	    # Add N grams to list of lemmas, replacing the adjacent terms that form the N grams
	    for gram in ngrams:
	        lemmas.append('_'.join(gram))
	        pos.append(str(N_gram)+'gram')

	    return lemmas, pos


	def remove_pos(slef, lemmas,pos,keep=[]):
	    """
	    Remove lemmas with parts of speech in the list remove.
	    
	    lemmas - list of lemmas as returned by pos2lemmas, 
	             handle_negation, or addNgrams
	    pos - list of parts of speech as returned by pos2lemmas, 
	          handle_negation, or addNgrams
	    keep - list of parts of speech to keep from the list of lemmas
	    """

	    temp = [(l,p) for l,p in zip(lemmas,pos) if p in keep]
	    if len(temp)!=0: 
	        new_lemmas, new_pos = zip(*temp)
	    else:
	        new_lemmas = lemmas
	        new_pos = pos
	    return new_lemmas, new_pos

	def remove_punctuation(self, lemmas,pos):
	    """
	    Return lemma and pos lists with all items removed that contain 
	    punctuation (other than an apostraphe and underscore).
	    """

	    import string
	    import re

	    table = string.maketrans("","")
	    punct = string.punctuation
	    keep = ["'","_"]
	    for k in keep:
	        punct = punct.replace(k,'')

	    regex = re.compile('[%s]' % re.escape(punct))
	    newlemmas = [regex.sub('',l) for l in lemmas]

	    # Remove empty strings
	    try:
	        temp = [(l,p) for l,p in zip(newlemmas,pos) if l!=""]
	        newlemmas, newpos = zip(*temp)
	        newlemmas = list(newlemmas)
	        newpos = list(newpos)
	    except:
	        nostrings_here = True
	        newlemmas = []
	        newpos = []

	    return newlemmas, newpos


	def text2lemmas(self, string):
		"""
		Converts a string of text into a list of lemmas extracted from the text.
		"""
		from nltk.corpus import wordnet as wn

		# Array to hold lemmas for output
		lemmas = []

		# Calculate pos_tag for each word in the string
		pos_tags = self.text2pos(string)

		# Lemmatize each word in the string
		lemmas, pos = self.pos2lemmas(pos_tags)

		# Remove lemmas with punctuation
		lemmas, pos = self.remove_punctuation(lemmas,pos)

		# Negation handling
		#   If "not" or "n't" occurs immediately before a verb or adjective,
		#   replace the verb or adjective with not_verb or not_adjective
		lemmas,pos = self.handle_negation(lemmas,pos)

		# N-gram identification
		lemmas, pos = self.addNgrams(lemmas,pos,2)   # bigrams
		lemmas, pos = self.addNgrams(lemmas,pos,3)   # trigrams
		# lemmas, pos = remove_duplicate_grams(lemmas, pos). obsolete 1/25/2015

		# Remove parts of speech that are not noun, verb, adjective, adverb, or Ngram
		lemmas, pos = self.remove_pos(lemmas,pos,keep=[wn.NOUN,wn.VERB,wn.ADJ,wn.ADV,'2gram','3gram'])

		return lemmas

	def make_map(self, venues, mapcenter=False):

		import os
		import folium
		import seaborn as sns

		lats = []
		lngs = []
		labels = []
		for venue in venues:
			lats   += [venue['location']['coordinate']['latitude']]
			lngs   += [venue['location']['coordinate']['longitude']]
			#labels += [str(venue['name'])]
			try:
				labels += [str(venue['name'])]
			except:
				labels += ['Map could not handle string']

		    #labels += unicode(raw_input(), 'utf8')
		    #labels += str(venue['name'])

		maxlen = 0.0
		mapcenter_given = False
		if mapcenter:
			mapcenter_given = True
		else:
			mapcenter_given = False
			#Define map center
			mapcenter = [np.mean(lats), np.mean(lngs)]
		
		yelp_map = folium.Map(location=mapcenter, width='100%', height=500, tiles='OpenStreetMap', zoom_start=11)

		for n in range(len(venues)):
		    yelp_map.simple_marker(location=[lats[n],lngs[n]], popup_on=True, #marker_icon='eject',
                  popup=labels[n], marker_color='red')

		if mapcenter_given:
			yelp_map.simple_marker(location=mapcenter, popup_on=True, marker_icon='ok-sign',
                  popup='Tweet Location', marker_color='blue')

		# Check if map file already exists
		if os.path.exists('app/templates/currentname.txt'):
			with open('app/templates/currentname.txt', 'rb') as fp:
				mapname = json.load(fp)
		else:
			mapname = '0'

		mapname = int(mapname)
		mapname += 1
		mapname = str(mapname)

		with open('app/templates/currentname.txt', 'wb') as fp:
			json.dump(mapname, fp)

		yelp_map.create_map(path='app/templates/maps/map'+mapname+'.html')# % (config.paths['templates']))

		return mapname


