import sys
from cassandra.cluster import Cluster

if len(sys.argv) != 6:
	print("Usage : %s username access_token access_token_secret consumer_key consumer_secret")
	sys.exit()

cluster=Cluster(['cassandra1','cassandra2','cassandra3'])
session=cluster.connect('w251twitter')
session.execute(
	"""
	INSERT INTO twitter_connections (username, access_token, access_token_secret, consumer_key, consumer_secret)
	VALUES(%s, %s, %s, %s, %s)
	""",
	(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]))

