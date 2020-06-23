import sys
import json
import datetime
import time
import dateutil.parser
from datetime import timedelta
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pycorenlp import StanfordCoreNLP
from pyspark_cassandra import streaming
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext
from pyspark.sql.types import *

# Define batch size in seconds
window_size = 15

def get_concept():
    """ This function will query the Cassandra database to match hashtags
    in a tweet with a corresponding concept.
    """
    concept = "Ant Man and The Wasp"
    return concept

def get_tweet_text(tweet):
    """This function takes the full content of a tweet and extracts the text
    of the tweet with ascii encoding.
    """
    # Manage errors for empty tweets
    if tweet.get('text')==None:
        tweet_text = None
    else:
        tweet_text = tweet['text'].encode('ascii','ignore').split(" ")
    return tweet_text

def get_sentiment(tweet_text):
    """This function takes in the text in a tweet and returns a sentiment
    value using Stanford CoreNLP: https://stanfordnlp.github.io/CoreNLP/
    """
    sentiment = 3
    return sentiment

def summarize_tweets(tweet):
    """This function takes in each tweet and returns a tuple with 4 elements
    for entering into the "summary" Cassandra database:
    concept (primary key), insertion_time, sentiment, tweet_count
    """
    return None

def main():
    # Set up Spark session and connection with Cassandra
    sparkConf = SparkConf().setAppName("TwitterSentimentAnalysisByHashtag") \
        .set("spark.cassandra.connection.host", "cassandra1, cassandra2, cassandra3")
    sc = SparkContext(conf=sparkConf)
    session = SparkSession(sc)
    sqlContext = SQLContext(sc)
    ssc = StreamingContext(sc, window_size)
    # Set up receiving Twitter stream from Kafka
    brokers, topic = sys.argv[1:]
    kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers})
    # Set up connection to Stanford NLP Sentiment analysis
    nlp = StanfordCoreNLP('http://localhost:9000')
    # Parse tweets into RDD
    tweets = kvs.filter(lambda x: x is not None).filter(lambda x: x is not '').map(lambda x: json.loads(x[1]))

    # print statements for testing - remove or comment out for final production
    tweets.count().map(lambda x:'Total number of tweets in this %d-second batch: %s'
                                % (window_size, x)).pprint()
    tweets.map(lambda tweet: get_tweet_text(tweet)).pprint()

    # Create RDD to summarize tweets for each window for summary DB table
    # summary_stream = tweets.map(lambda tweet: summarize_tweets(tweet)).filter(lambda x: x is not None)
    # This stream will also need to aggregate/reduce by key for concept
    # summary_stream.saveToCassandra("w251twitter", "summary")
    # Create RDD to extract tweet data for sentiment DB table
    # Here's where Walt's code for the sentiment_stream will go
    # Need other functions in place to make the sentiment_stream work
    
    # Start Spark
    ssc.start()
    ssc.awaitTermination()



if __name__ == "__main__":
    main()
