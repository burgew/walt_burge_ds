import sys
from cassandra.cluster import Cluster

if len(sys.argv) != 2:
	print("Usage : %s username")
	sys.exit()

cluster=Cluster(['cassandra1','cassandra2','cassandra3'])
session=cluster.connect('w251twitter')
# FOR SOME REASON THE DELETE MUST BE IN LOWERCASE
session.execute("delete from twitter_connections where username = %s",(sys.argv[1],))
