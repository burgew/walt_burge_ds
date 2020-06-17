# Set up Spark ThriftServer for connecting to Tableau

Spark ThriftServer must be running and connected to the Cassandra cluster in order for BI software such as Tableau to display the contents. The Spark TS configures the Hive metastore using schema information from Cassandra. When a SQL query comes through from Tableau, the query is validated against the metastore, compiled, and run against the Cassandra backing store using the Cassandra connector. Larger or more complex queries may require scaling the ThriftServer up/out, but we will provision only one since our queries tend to be simpler. Below, we will set all this up.

## Provision the server with slcli
`slcli vs create -d dal13 -H thriftserver -D w251.mids -m 4096 -c 4 -o CENTOS_7_64 --key [slcli_key] --billing=hourly`

Once the node is ready, continue setup below.

## Write the Cassandra hosts into the hosts file
```
cat > /etc/hosts <<EOF
10.73.183.210 thriftserver.w251.mids thriftserver
127.0.0.1 localhost.localdomain localhost
127.0.0.1 localhost4.localdomain4 localhost4

# The following lines are desirable for IPv6 capable hosts
#::1 thriftserver.w251.mids thriftserver
#::1 localhost.localdomain localhost
#::1 localhost6.localdomain6 localhost6

10.73.183.227 cassandra1
10.88.161.219 cassandra2
10.88.161.251 cassandra3
EOF
```

## Update system packages and install prerequisites
```
yum update -y
yum -y install java-1.8.0-openjdk.x86_64 iptables-services python36u python36u-pip.noarch wget
pip3.6 install --upgrade pip
```

## Configure Java and install Spark, set up passwordless SSH
```
export JAVA_HOME=/usr/lib/jvm/jre-1.8.0-openjdk
export JRE_HOME=/usr/lib/jvm/jre
ssh-keygen -t rsa -b 2048 -C 'auto-generated' -N '' -f /root/.ssh/id_rsa
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
cd /opt
wget -O - http://apache.mirror.globo.tech/spark/spark-2.3.1/spark-2.3.1-bin-hadoop2.7.tgz | tar xzf -
ln -s spark-2.3.1-bin-hadoop2.7 spark
echo export SPARK_HOME=\"/opt/spark\" >> /root/.bash_profile
source /root/.bash_profile
```

## Allow your IP through the firewall
`iptables -A INPUT -p tcp -s [your.ip.goes.here] -j ACCEPT`

## Start Spark
```
$SPARK_HOME/sbin/start-master.sh
$SPARK_HOME/sbin/start-slave.sh spark://thriftserver:7077
```

## Set up the Hive metastore
```
$SPARK_HOME/bin/beeline

!connect jdbc:hive2://thriftserver:10000
CREATE TABLE hashtag USING org.apache.spark.sql.cassandra OPTIONS (keyspace 'w251twitter', table 'hashtag');
CREATE TABLE sentiment USING org.apache.spark.sql.cassandra OPTIONS (keyspace 'w251twitter', table 'sentiment');
CREATE TABLE tweets USING org.apache.spark.sql.cassandra OPTIONS (keyspace 'w251twitter', table 'tweets');
CREATE TABLE twitter_connections USING org.apache.spark.sql.cassandra OPTIONS (keyspace 'w251twitter', table 'twitter_connections');

... repeat for as many tables are in Cassandra in the 'w251twitter' keyspace ...

^C (Ctrl+C to break out of beeline)
```

## Start the ThriftServer
```
$SPARK_HOME/sbin/start-thriftserver.sh --packages com.datastax.spark:spark-cassandra-connector_2.11:2.3.0 --confspark.cassandra.connection.host=cassandra1,cassandra2,cassandra3 --master spark://thriftserver:7077
```

