from cassandra.cluster import Cluster

cluster=Cluster(['cassandra1','cassandra2','cassandra3'])
session=cluster.connect('w251twitter')
session.execute(
	"""
        INSERT INTO w251twitter.CONCEPTS (concept, hashtag_list)
        VALUES ('Trump',
        ['#Trump', '#trump', '#maga'])
	""")
session.execute(
	"""
        INSERT INTO w251twitter.CONCEPTS (concept, hashtag_list)
        VALUES ('Ant Man and The Wasp',
        ['#antman', '#ant-man', '#antmanandthewasp',
        '#AntMan', '#Ant-Man', '#Ant-man', 'Antman',
        'TheWasp', '#AntManandTheWasp', '#AntManAndTheWasp'])
	""")
session.execute(
	"""
        INSERT INTO w251twitter.CONCEPTS (concept, hashtag_list)
        VALUES ('Obama',
        ['#Obama','#obama','#obamaday'])
	""")
session.execute(
	"""
        INSERT INTO w251twitter.CONCEPTS (concept, hashtag_list)
        VALUES ('K-Pop',
        ['#kpop','#ijin','#jinyoung','#jungkook','#parkjihoon'])
	""")
session.execute(
	"""
        INSERT INTO w251twitter.CONCEPTS (concept, hashtag_list)
        VALUES ('Teen',
        ['#teenchoice','#seventeed','#teen','#choicefandom', '#straykids'])
	""")
session.execute(
	"""
        INSERT INTO w251twitter.CONCEPTS (concept, hashtag_list)
        VALUES ('Careers',
        ['#careerarc','#hiring','#coders'])
	""")
