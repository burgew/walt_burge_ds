I've been running this in three separate terminal windows so I can see what's going on. Also I haven't yet figured out how to run this code all in one shell script.  (--Laura) :-)

This should work on any standalone server set up with our current instructions (may need a few mods, I'll add that to the standalone instructions shortly),

It can be run on the server I set up as follows (with three terminal windows).  First log into the gateway server, then into this server:
```
ssh root@laura
```

First window:
##### Start up the Stanford NLP server
You'll see the server start up.  It will also print some results once it's processing tweets.
```
cd stanford-corenlp-full-2018-02-27
java -mx5g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -timeout 10000
```

Second window:
##### Start up a twitter stream
For testing, this can be set up to print tweets to the screen: Un-comment the print line in the on-data method in the StdOutListener class.  

IMPORTANT:  The `twitter_connect_integrated.py` file is currently set up to work with a Kafka cluster instead of a single server.  If using these instructions to run this process on a single server, change the kafka variable to this instead: `kafka = KafkaClient("localhost:9092")`
```
python3.6 /root/MIDS_W251_Benchmarking/streaming/twitter_connect_integrated.py
```
To send results to a log:
```
python3.6 /root/MIDS_W251_Benchmarking/streaming/twitter_connect_integrated.py &> /var/log/w251/twitter_connect_integrated.log
```
To see the log:
```
tail -f /var/log/w251/twitter_connect_integrated.log
```

Third window:
##### Start up the Spark process
IMPORTANT:  If this is being run on a different machine, change the servername on the --master argument below (currently set to laura).  
```
/opt/spark/bin/spark-submit \
--packages anguenot:pyspark-cassandra:0.9.0 \
--jars /opt/spark/jars/spark-streaming-kafka-0-8-assembly_2.11-2.3.1.jar \
--master spark://laura.w251.mids:7077  \
--conf spark.cassandra.connection.host=cassandra1,cassandra2,cassandra3  \
/root/MIDS_W251_Benchmarking/streaming/spark_integrated.py localhost:9092 twitter
```
To send results to a log:
```
/opt/spark/bin/spark-submit \
--packages anguenot:pyspark-cassandra:0.9.0 \
--jars /opt/spark//jars/spark-streaming-kafka-0-8-assembly_2.11-2.3.1.jar \
--master spark://laura.w251.mids:7077  \
--conf spark.cassandra.connection.host=cassandra1,cassandra2,cassandra3  \
/root/MIDS_W251_Benchmarking/streaming/spark_integrated.py localhost:9092 twitter \
&> /var/log/w251/spark_integrated.log &
```
To see the log:
```
tail -f /var/log/w251/spark_integrated.log
```

##### Configuration
The batch size in seconds can be set inside the spark_integrated.py file with the window_size variable (currently at the top of the file).  

Which Twitter account being used to get tweets can be set inside the twitter_connect_integrated.py file. It's inside the call to the Cassandra database for credentials.  Currently it's set to my account (Laura).

Both of these could presumably be set to be configurable when calling the files if necessary.

Concepts (i.e., movie names) and associated hashtags are stored in the "concepts" table in Cassandra. The Kafka producers uses the aggregated list of all hashtags to filter the twitter stream. A sample script for inserting more concept/hastag combinations is in the Utilities folder.
