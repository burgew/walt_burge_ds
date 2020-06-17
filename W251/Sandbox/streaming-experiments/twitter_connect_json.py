import sys
from cassandra.cluster import Cluster
import dateutil.parser
import json
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from tweepy.streaming import StreamListener
import time
from tweepy import OAuthHandler
from tweepy import Stream
import twitter
from kafka import SimpleProducer, KafkaClient

access_token = "934581358344790016-yq3GrSkXlZoTM0Yskv9b2DoTNBz5YUW"
access_token_secret = "yaG9Qpjm5fmSyE2L5hU8uM54pvLbY5eC0iAzWms9Xd2CB"
consumer_key = "lMHMMbmNxtlLHcZA9Bqxh8h6w"
consumer_secret = "KAT8bFoZknI1TYnx19Gx6p4cQqMbTtFAUOoBf1ndmHQ7eskgEX"


class StdOutListener(StreamListener):


    def __init__(self):
        cluster=Cluster(['cassandra1','cassandra2','cassandra3'])
        self.session=cluster.connect('w251twitter')
        self.insert_stmt = self.session.prepare("""
                INSERT INTO TWEETS(tweet, insertion_time) VALUES (?, toTimestamp(now()))
        """)

    def on_data(self, data):
        if data and ('delete' not in data):

            tweet_json = get_tweet_json(data)
            if tweet_json:

                # Insert tweet JSON into the DB
                self.session.execute(self.insert_stmt, [tweet_json])

                producer.send_messages("twitter", tweet_json.encode('utf-8'))
                print(tweet_json)
        return True


    def on_error(self, status):
        print(status)


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


def connect_twitter():
    access_token = "934581358344790016-yq3GrSkXlZoTM0Yskv9b2DoTNBz5YUW"
    access_secret = "yaG9Qpjm5fmSyE2L5hU8uM54pvLbY5eC0iAzWms9Xd2CB"
    consumer_key = "lMHMMbmNxtlLHcZA9Bqxh8h6w"
    consumer_secret = "KAT8bFoZknI1TYnx19Gx6p4cQqMbTtFAUOoBf1ndmHQ7eskgEX"
    auth = twitter.OAuth(token=access_token,
                         token_secret=access_secret,
                         consumer_key=consumer_key,
                         consumer_secret=consumer_secret)
    return twitter.TwitterStream(auth=auth)


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


def get_next_tweet(twitter_stream, i):
    """
    Return : JSON
    """
    block = False  # True
    stream = twitter_stream.statuses.sample()
    tweet_in = None
    while not tweet_in or 'delete' in tweet_in:
        tweet_in = stream.next()
        tweet_parsed = Tweet(tweet_in)

    return json.dumps(tweet_parsed)


# def process_rdd_queue(twitter_stream, nb_tweets=5):
#    """
#     Create a queue of RDDs that will be mapped/reduced one at a time in 1 second intervals.
#    """
#    rddQueue = []
#    for i in range(nb_tweets):
#        json_twt = get_next_tweet(twitter_stream, i)
#        dist_twt = ssc.sparkContext.parallelize([json_twt], 5)
#        rddQueue += [dist_twt]
#
#    lines = ssc.queueStream(rddQueue, oneAtATime=False)
#    lines.pprint()


# sc = SparkContext(appName="PythonStreamingQueueStream")
# ssc = StreamingContext(sc, 1)

# twitter_stream = connect_twitter()
# process_rdd_queue(twitter_stream)

# try:
#    ssc.stop(stopSparkContext=True, stopGraceFully=True)
# except:
#    pass

# ssc.start()
# time.sleep(2)
# ssc.stop(stopSparkContext=True, stopGraceFully=True)

#tweet_json = get_tweet_json(SAMPLE_TWEET)
#print("tweet JSON:\n {}".format(tweet_json))

kafka = KafkaClient("localhost:9092")
producer = SimpleProducer(kafka)
l = StdOutListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
stream = Stream(auth, l)
#stream.sample()
stream.filter(languages = ['en'], \
              track = [ '#antman', '#ant-man', '#antmanandthewasp', '#AntMan', '#Ant-Man', '#Ant-man', 'Antman', 'TheWasp', '#AntManandTheWasp', '#AntManAndTheWasp', '#Trump', '#trump'])
# '#Obama', '#obama', '#mtvhottest', '#mmvas', '#happyexolday', '#kcamexico', '#iheartradiommvas', '#obamaday', '#exo', '#got7', '#ffgroupbts', '#4yearsasexol', '#tbworld2018', '#wewantjustice', '#wannaone', '#gg4eva', '#southkorea', '#bts', '#eyesonyouinsg', '#kcaargentina', '#army', '#redvelvet', '#baekhyun', '#kpop', '#teenchoice']) , '#choicefandom', '#bambam', '#ikon', '#bebest', '#got7worldtour', '#kai', '#btsarmy', '#ffsingleinmyblood', '#sjxoshopping', '#seventeen', '#ffsinglewolves', '#suho', '#exol_abyrinth', '#sotocatop', '#nct', '#lalobrito', '#rt', '#nowplaying', '#kangdaniel', '#bighitprotectbts', '#job', '#bbacharityconcert12', '#saveshadowhunters', '#sofiareyes123', '#cd9', '#gnbgarantiadepaz', '#bryanmouquetrendy', '#rm', '#coders', '#eyesonyou', '#axel', '#biggbosstelugu2', '#taehyung', '#karolsevilla', '#ffsinglenotears', '#summermagic', '#haash', '#jimin', '#powerup', '#peckpalitchoke', '#hiring', '#carolinakopelioff', '#naniunfitforbb2host', '#elf', '#losiento', '#twice', '#fifaeworldcup', '#mya', '#kaushalarmy', '#mark', '#quran', '#4yearswithexol', '#jungkook', '#ruggeropasquarelli', '#maga', '#micaviciconteig', '#blackpink', '#np', '#4ago', '#nintendoswitch', '#bbacharityconcert', '#jinyoung', '#micaelistas', '#careerarc', '#jin', '#newprofilepic', '#ps4share', '#hdpyidestekliyoruz', '#lutteo', '#aldubendures', '#got7insg', '#ffartistcamila', '#parkjihoon', '#straykids', '#soyluna', '#cncowners', '#trapadrive' ])

