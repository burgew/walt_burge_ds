from cassandra.cluster import Cluster

cluster=Cluster(['cassandra1','cassandra2','cassandra3'])
session=cluster.connect('w251twitter')
session.execute(
	"""
        CREATE TABLE w251twitter.CONCEPTS (concept text,
                                           hashtag_list list<text>,
                                           PRIMARY KEY (concept))
	""")
