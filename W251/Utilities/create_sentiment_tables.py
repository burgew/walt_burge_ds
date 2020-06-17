import sys
from cassandra.cluster import Cluster

cluster=Cluster(['cassandra1','cassandra2','cassandra3'])
session=cluster.connect('w251twitter')
session.execute(
	"""
        CREATE TABLE w251twitter.HASHTAG (tweet_id text, hashtag text, PRIMARY KEY (tweet_id, hashtag))
	""")
session.execute(
	"""
        INSERT INTO w251twitter.HASHTAG (tweet_id, hashtag) VALUES ('0000001', '#antman')
	""")
session.execute(
	"""
        INSERT INTO w251twitter.HASHTAG (tweet_id, hashtag) VALUES ('0000001', '#Wasp')
	""")
session.execute(
	"""
        INSERT INTO w251twitter.HASHTAG (tweet_id, hashtag) VALUES ('0000001', '#Trump')
	""")
session.execute(
	"""
	CREATE TABLE w251twitter.SENTIMENT (tweet_id text, hashtags text, tweet text, geo text, user_id text,
				 tweet_time text, screen_name text, sentiment int, insertion_time timestamp,
				 PRIMARY KEY (tweet_id))
	""")
session.execute(
	"""
	INSERT INTO w251twitter.SENTIMENT (tweet_id, hashtags, tweet, geo, user_id,
				 tweet_time, screen_name, sentiment, insertion_time) VALUES
                              ('0000001', '#antman, #Wasp, #Trump', 'I went to see a good movie today.', 'Lithuania', '1000000',
                                 '2018-08-03 23:49', 'RangerMaverick', 0, toTimestamp(now()))
	""")

