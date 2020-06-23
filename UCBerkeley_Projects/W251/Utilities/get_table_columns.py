from cassandra.cluster import Cluster

cluster=Cluster(['cassandra1','cassandra2','cassandra3'])
session=cluster.connect('w251twitter')
rows = session.execute(
                       """
                       SELECT * FROM system_schema.columns
                       WHERE keyspace_name='w251twitter';
                       """)
for row in rows:
    print(row.table_name + ": " + row.column_name + ", Type: " + row.type + ", Column Type: " + row.kind)
