import sys
from cassandra.cluster import Cluster

cluster=Cluster(['cassandra1','cassandra2','cassandra3'])
session=cluster.connect('w251twitter')
session.execute(
	"""
	DROP TABLE w251twitter.HASHTAG 
	""")

session.execute(
	"""
	DROP TABLE w251twitter.SENTIMENT 
	""")

