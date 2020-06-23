from cassandra.cluster import Cluster

cluster=Cluster(['cassandra1','cassandra2','cassandra3'])
session=cluster.connect('w251twitter')
rows = session.execute('select * from twitter_connections')
for row in rows:
	print ("username: %s\naccess_token: %s\naccess_token_secret: %s\nconsumer_key: %s\nconsumer_secret: %s\n" % 
		(row.username,row.access_token, row.access_token_secret,row.consumer_key, row.consumer_secret))
