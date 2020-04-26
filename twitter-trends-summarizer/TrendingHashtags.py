import tweepy
import time, sys 

import warnings
warnings.filterwarnings("ignore")

CONSUMER_KEY= 'p9smvhLm9SXh9z2EUNYyakFe7'
CONSUMER_SECRET= 'Fu6f5YWPyEfrUwpGS02Ojm2eMSxanySYzvkhP7ypVLtlCvIvgy'
ACCESS_TOKEN= '809287937351249920-2S2imOpJVEy0oxDlGwVADh3wM2WPVpY'
ACCESS_TOKEN_SECRET= 'EkF2JQx9jcsBOyyMU4UsZYgFqLWJ1UH0W8NCDPL7Axnbs'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

trending = api.trends_place(1)

#Trending topics
topics = [x['name'] for x in trending[0]['trends']]
for topic in topics:
	print(topic.encode('utf-8').strip())
	
# Trending hash tags
#hashtags = [x['name'] for x in trending[0]['trends'] if x['name'].startswith('#')]
#print hashtags
