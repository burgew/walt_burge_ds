import datetime
import time
import json
import sys

from datetime import timedelta

from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext
from pyspark.sql.types import *

from pyspark_cassandra import streaming

#import pyspark-cassandra
#$import pyspark_cassandra.streaming
#$from pyspark_cassandra import CassandraSparkContext
#import org.apache.spark.sql.cassandra.CassandraSQLContext


from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pycorenlp import StanfordCoreNLP


def derive_sentiment(sent, sentValue):
    if sent == 'Negative':
        return -1*sentValue
    else:
        return sentValue


def remove_non_ascii(s): return "".join(filter(lambda x: ord(x)<128, s))


def get_sentiment(tweet_text):
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


def get_tweet_sentiment(tweet):
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


def setup_kafka_stream():
    kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers})

    return kvs


def mapTweetDict(tweet_dict):
    #print("Tweet dict:\n{}".format(tweet_dict))
    #mappedID = tweet_dict['id']
    mappedID = "TEST_ID"
    mappedText = tweet_dict['text']
    mappedSentiment = 0
    mappedHashtags = "TEST_HASHTAGS"
    mappedGeo = "TEST_GEO"
    mappedUserID = "TEST_USERID"
    mappedTimestamp = "TEST_TIMESTAMP"
    mappedScreenName = "TEST_SCREEN_NAME"

    # flattenedMap = (mappedID,
    # mappedHashtags, mappedText, mappedGeo, mappedUserID, mappedTimestamp, mappedScreenName, mappedSentiment)
    flattenedMap = (tweet_dict['id'],
                    mappedGeo,
                    mappedHashtags,
                    datetime.datetime.now(),
                    mappedScreenName,
                    tweet_dict['sentiment'],
                    tweet_dict['text'],
                    mappedTimestamp,
                    mappedUserID)
#    flattenedMap = (tweet_dict['id'], tweet_dict['hashtags'], tweet_dict['text'],
#                    tweet_dict['geo'], tweet_dict['user_id'], tweet_dict['timestamp'],
#                    tweet_dict['screen_name'], tweet_dict['sentiment'], datetime.datetime.now())
    return flattenedMap


def save_tweet_to_cassandra(tweet_rdd):
    print("RDD:\n{}".format(tweet_rdd))
    schema = StructType([StructField("tweet_id",StringType(), nullable = False), \
                         StructField("hashtags",StringType(), nullable = True), \
                         StructField("tweet",StringType(), nullable = False), \
                         StructField("geo",StringType(), nullable = True), \
                         StructField("user_id",StringType(), nullable = True), \
                         StructField("tweet_time",StringType(), nullable = True), \
                         StructField("screen_name",StringType(), nullable = True), \
                         StructField("sentiment",IntegerType(), nullable = False)])
#             StructField("insertion_time",TimestampType(), nullable = False)])

    try:
        firstRow=tweet_rdd.first()
        tweet_rdd=tweet_rdd.filter(lambda row:row != firstRow)

        if not tweet_rdd.isEmpty():
            sqlContext.createDataFrame(tweet_rdd, schema).write \
                                                         .format("org.apache.spark.sql.cassandra") \
                                                         .mode('append') \
                                                         .options(table="sentiment", keyspace="w251twitter") \
                                                         .save()
    except ValueError:
        print("The RDD was empty...continuing...")

if __name__ == "__main__":
    sparkConf = SparkConf().setAppName("TwitterSentimentAnalysis") \
        .set("spark.cassandra.connection.host", "cassandra1, cassandra2, cassandra3")

    sc = SparkContext(conf=sparkConf)
    session = SparkSession(sc)
    sqlContext = SQLContext(sc)
    ssc = StreamingContext(sc, 2)
    brokers, topic = sys.argv[1:]

    kvs = setup_kafka_stream()

    nlp = StanfordCoreNLP('http://localhost:9000')

    tweets = kvs.filter(lambda x: x is not None).filter(lambda x: x is not '').map(lambda x: json.loads(x[1]))
    tweets.count().map(lambda x: 'Tweets in this batch: %s' % x).pprint()

    sentiment_stream = tweets.map(lambda tweet: get_tweet_sentiment(tweet)).filter(lambda x: x is not None)
    # sentiment_stream.foreachRDD(lambda rdd : save_tweet_to_cassandra(rdd))
    # replaced by this line:
    sentiment_stream.saveToCassandra("w251twitter", "sentiment")

    ssc.start()
    ssc.awaitTermination()
