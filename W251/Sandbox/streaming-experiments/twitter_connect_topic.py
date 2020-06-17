from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from kafka import SimpleProducer, KafkaClient
from cassandra.cluster import Cluster

# Connect to Cassandra
cluster=Cluster(['cassandra1','cassandra2','cassandra3'])
session=cluster.connect('w251twitter')
# Get hashtags from Cassandra
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

    def on_data(self,data):
        if data and ('delete' not in data):
            producer.send_messages("twitter", data.encode('utf-8'))
            print(data)
        return True

    def on_error(self, status):
        # If the Twitter account used to produce tweets exceeds the rate limit,
        # continued failed attempts to connect will exponentially increase
        # the time until the next successful connection.
        # This code prevents repeated attempts from delaying reconnection.
        # Not required for an enterprise solution with unlimited streaming
        if status_code == 420:
            return False

# Set up Kafka producer from Twitter
kafka = KafkaClient("localhost:9092")
producer=SimpleProducer(kafka)
l = StdOutListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
stream = Stream(auth, l)
stream.filter(languages = ['en'],
              track = hashtags)
