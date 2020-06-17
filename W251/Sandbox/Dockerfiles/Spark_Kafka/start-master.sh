cd /opt
spark/bin/spark-class org.apache.spark.deploy.master.Master -h master & \
kafka/bin/zookeeper-server-start.sh -daemon config/zookeeper.properties & \
kafka/bin/kafka-server-start.sh -daemon config/server.properties
