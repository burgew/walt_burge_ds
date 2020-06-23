from cassandra.cluster import Cluster

cluster=Cluster(['cassandra1','cassandra2','cassandra3'])
session=cluster.connect('w251twitter')
session.execute(
	"""
        CREATE TABLE w251twitter.SUMMARY (concept text,
										  sentiment int,
										  insertion_time timestamp,
										  PRIMARY KEY (concept, insertion_time))
	""")
