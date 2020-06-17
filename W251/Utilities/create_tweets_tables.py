import sys
from cassandra.cluster import Cluster

cluster=Cluster(['cassandra1','cassandra2','cassandra3'])
session=cluster.connect('w251twitter')
session.execute(
	"""
	CREATE TABLE TWEETS (tweet text, insertion_time timestamp, PRIMARY KEY (insertion_time, tweet))
	""")

