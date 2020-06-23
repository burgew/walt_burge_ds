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
from cassandra.cluster import Cluster

# Define batch size in seconds
window_size = 60

# Connect to Cassandra to get data from database
cluster=Cluster(['cassandra1','cassandra2','cassandra3'])
session=cluster.connect('w251twitter')
# Get concepts and related hashtags from Cassandra
tags = session.execute('select * from concepts')
hashtag_map = {}
for tag in tags:
    hashtag_map[tag.concept] = tag.hashtag_list


def derive_sentiment(sent, sentValue):
    """This function is used by the get_sentiment function below.
    This function takes sentiment values output by the Stanford NLP
    Sentiment Analysis and normalizes them for use as positive and negative
    integers.
    """
    if sent == 'Negative':
        return -1*sentValue
    else:
        return sentValue

def get_sentiment(tweet_text):
    """ This function is used in the get_tweet_sentiment function below.
    This function takes the text of a tweet, processes the tweet via the
    Stanford NLP Sentiment Analysis and returns a sentiment value as an integer.
    """
    sentiment = 0
    if tweet_text != None:

        print("Text to corenlop:\n{}".format(tweet_text))

        response = nlp.annotate(tweet_text,
                                properties={
                                    'annotators': 'sentiment',
                                    'outputFormat': 'json',
                                    'timeout': 10000,
                                })

        print("Sentiment response:\n{}".format(response))

        if isinstance(response, dict):
            for s in response['sentences']:
                print("\n****Sentence: \"{}\"i\n".format(s))
                ind = s["index"]
                print("ind: {}".format(ind))
                words = " ".join([t["word"] for t in s["tokens"]])
                print("words: {}".format(words))
                sent = s["sentiment"]
                print("sent: {}".format(sent))
                sent_value = s["sentimentValue"]
                print("sent_value: {}".format(sent_value))
                sentiment += derive_sentiment(sent, int(sent_value))

    print("Returning derived sentiment: {}".format(sentiment))

    return sentiment

def remove_non_ascii(s): return "".join(filter(lambda x: ord(x)<128, s))

def mapTweetDict(tweet_dict):
    """This function is used in the get_tweet_sentiment function below.
    This function maps tweet data to specific values for inserting
    into the Cassandra database.
    """
    mappedID = "TEST_ID"
    mappedText = tweet_dict['text']
    mappedSentiment = 0
    mappedHashtags = "TEST_HASHTAGS"
    mappedGeo = "TEST_GEO"
    mappedUserID = "TEST_USERID"
    mappedTimestamp = "TEST_TIMESTAMP"
    mappedScreenName = "TEST_SCREEN_NAME"

    flattenedMap = (tweet_dict['id'],
                    mappedGeo,
                    mappedHashtags,
                    datetime.datetime.now(),
                    mappedScreenName,
                    tweet_dict['sentiment'],
                    tweet_dict['text'],
                    mappedTimestamp,
                    mappedUserID)

    return flattenedMap

def get_tweet_sentiment(tweet):
    """This function takes a tweet and maps it to a set of values to be
    inserted into the "sentiment" table in the Cassandra database.
    """
    tweet_dict = json.loads(tweet)
    print("tweet dict:\n{}".format(tweet_dict))

    hashtags = tweet_dict['hashtags']
    if (hashtags):
        tweet_text = remove_non_ascii(json.loads(tweet)['text'])
        sentiment = get_sentiment(tweet_text)
        tweet_dict['sentiment'] = sentiment

        return mapTweetDict(tweet_dict)
    else:
        return None

def get_concept(hashtags):
    """ This function will query the Cassandra database to match hashtags
    in a tweet with a corresponding concept.
    """
    # Concepts and related hashtags are imported from Cassandra above
    if hashtags:
        for tag in hashtags:
            for concept_name, hashtag_list in hashtag_map.items():
                if tag in hashtag_list:
                    concept = concept_name
                    break
                else:
                    concept = None
    else:
        concept = None
    return concept

def summary_to_db(summary):
    concept = summary[0]
    insertion_time = datetime.datetime.now()
    sentiment = summary[1]
    return concept, insertion_time, sentiment

def tweet_summary(tweet):
    """This function takes in each tweet and returns elements
    for the summary table in the Cassandra database.
    """
    tweet_dict = json.loads(tweet)
    hashtags = tweet_dict['hashtags']
    if (hashtags):
        tweet_text = remove_non_ascii(json.loads(tweet)['text'])
        sentiment = get_sentiment(tweet_text)
        concept = get_concept(hashtags)
        return concept, sentiment
    else:
        return None

def main():
    """This function is where Spark is connected to Kafka and Cassandra,
    where the RDD processing happens, and where the resulting data is
    saved into Cassandra from the RDD.
    """
    # Set up Spark session and connection with Cassandra
    sparkConf = SparkConf().setAppName("TwitterSentimentAnalysis") \
        .set("spark.cassandra.connection.host",
             "cassandra1, cassandra2, cassandra3")
    sc = SparkContext(conf=sparkConf)
    session = SparkSession(sc)
    sqlContext = SQLContext(sc)
    ssc = StreamingContext(sc, window_size)
    # Set up receiving Twitter stream from Kafka
    brokers, topic = sys.argv[1:]
    kvs = KafkaUtils.createDirectStream(ssc,
                                        [topic],
                                        {"metadata.broker.list": brokers})
    # Set up DStream of tweets
    tweets = kvs.filter(lambda x: x is not None) \
                .filter(lambda x: x is not '') \
                .map(lambda x: json.loads(x[1]))
    # Create RDD to process tweet data for sentiment table in Cassandra
    sentiment_stream = tweets \
                       .map(lambda tweet: get_tweet_sentiment(tweet)) \
                       .filter(lambda x: x is not None)
    sentiment_stream.saveToCassandra("w251twitter", "sentiment")
    # Create RDD to summarize tweets for summary table in Cassandra
    summary_stream = tweets \
                     .map(lambda tweet: tweet_summary(tweet)) \
                     .filter(lambda x: x is not None) \
                     .filter(lambda x: x[0] is not None) \
                     .reduceByKey(lambda x, y: x + y) \
                     .map(lambda x: (summary_to_db(x)))
    summary_stream.saveToCassandra("w251twitter", "summary")
    # Start Spark
    ssc.start()
    ssc.awaitTermination()


if __name__ == "__main__":
    # Set up connection to Stanford NLP Sentiment analysis
    # Placed here so that it will be available to all functions
    nlp = StanfordCoreNLP('http://localhost:9000')
    main()
