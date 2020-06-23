#!/usr/bin/python3.6

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from kafka import SimpleProducer, KafkaClient
from cassandra.cluster import Cluster
import dateutil.parser
import json
import time
import twitter


# Connect to Cassandra
cluster=Cluster(['cassandra1','cassandra2','cassandra3'])
session=cluster.connect('w251twitter')
# Get hashtag list (for filtering Twitter stream) from Cassandra
tags = session.execute('select * from concepts')
hashtags = []
for tag in tags:
    hashtags.extend(tag.hashtag_list)
# Get Twitter credentials from Cassandra
creds = session.execute("select * from twitter_connections where username = 'laura'")
for cred in creds:
    access_token = cred.access_token
    access_token_secret = cred.access_token_secret
    consumer_key = cred.consumer_key
    consumer_secret = cred.consumer_secret

# Define stream
class StdOutListener(StreamListener):

    def __init__(self):
        cluster=Cluster(['cassandra1','cassandra2','cassandra3'])
        self.session=cluster.connect('w251twitter')
        self.insert_stmt = self.session.prepare("""
                INSERT INTO TWEETS(tweet, insertion_time) VALUES (?, toTimestamp(now()))
        """)

    def on_data(self,data):
        if data and ('delete' not in data):
            tweet_json = get_tweet_json(data)
            if tweet_json:
                # Insert tweet JSON into the DB
                self.session.execute(self.insert_stmt, [tweet_json])

                producer.send_messages("twitter", tweet_json.encode('utf-8'))
                # Comment out this print line for production
                #print(tweet_json)
        return True

    def on_error(self, status):
        # If the Twitter account used to produce tweets exceeds the rate limit,
        # continued failed attempts to connect will exponentially increase
        # the time until the next successful connection.
        # This code prevents repeated attempts from delaying reconnection.
        # Not required for an enterprise solution with unlimited streaming
        if status_code == 420:
            return False

# Parse tweet
class Tweet(dict):
    def __init__(self, tweet_raw_json, encoding='utf-8'):
        super(Tweet, self).__init__(self)

        self['id'] = tweet_raw_json['id']
        self['geo'] = tweet_raw_json['geo']['coordinates'] if tweet_raw_json['geo'] else None
        self['text'] = tweet_raw_json['text']
        self['user_id'] = tweet_raw_json['user']['id']
        self['hashtags'] = [x['text'] for x in tweet_raw_json['entities']['hashtags']]
        self['timestamp'] = dateutil.parser.parse(tweet_raw_json[u'created_at']).replace(tzinfo=None).isoformat()
        self['screen_name'] = tweet_raw_json['user']['screen_name']

def get_tweet_json(data):
    if data and ('delete' not in data):
        tweet_raw_json = json.loads(data)

        if ('lang' in tweet_raw_json) and (tweet_raw_json['lang'] == 'en'):
            tweet_parsed = Tweet(tweet_raw_json)
            tweet_json = json.dumps(tweet_parsed)
            return json.dumps(tweet_json)
        else:
            return None
    else:
        return None


# Set up Kafka producer from Twitter
# Updated by Paul, the new one allows us to connect to remote kafka servers
# and spread the load.  If you need to run locally add an alias into /etc/hosts
# for one of these kafka? servers and make it resolve to the local host
#kafka = KafkaClient("localhost:9092")
kafka = KafkaClient("kafka1:9092, kafka2:9092, kafka3:9092, kafka4:9092")
producer=SimpleProducer(kafka)
l = StdOutListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
stream = Stream(auth, l)
stream.filter(languages = ['en'],
              track = hashtags)
