FROM centos:7

# Software update and library installation
RUN yum -y update \
  && yum -y install https://centos7.iuscommunity.org/ius-release.rpm \
  && yum -y install wget git java-1.8.0-openjdk.x86_64 python36u python36u-pip.noarch \
  && pip3.6 install --upgrade pip \
  && pip3 install kafka-python python-twitter tweepy

# Java installation
ENV JAVA_HOME /usr/lib/jvm/jre-1.8.0-openjdk
ENV JRE_HOME /usr/lib/jvm/jre
ENV PATH $PATH:$JAVA_HOME/bin
RUN mkdir -p /etc/profile.d
ADD java.sh /etc/profile.d/java.sh

# Install Kafka into /opt and run
WORKDIR /opt
RUN wget -O - http://archive.apache.org/dist/kafka/0.8.2.2/kafka_2.11-0.8.2.2.tgz | tar -xzf - \
  && ln -s kafka_2.11-0.8.2.2/ kafka \

# Install Spark into /opt and run
# TODO: If we don't make these separate Dockerfiles, we need different scripts to run depending on whether we are being provisioned as a master or a slave
WORKDIR /opt
RUN wget -O - http://apache.mirror.globo.tech/spark/spark-2.3.1/spark-2.3.1-bin-hadoop2.7.tgz | tar -xzf - \
  && ln -s spark-2.3.1-bin-hadoop2.7 spark \
  && cd spark \
  && cp conf/log4j.properties.template conf/log4j.properties
  && cat conf/log4j.properties | sed 's/log4j.rootCategory=INFO,/log4j.rootCategory=WARN,/g' > conf/log4j.properties

# Install streaming JAR
WORKDIR /opt/spark/jars
RUN wget http://central.maven.org/maven2/org/apache/spark/spark-streaming-kafka-0-8-assembly_2.11/2.3.1/spark-streaming-kafka-0-8-assembly_2.11-2.3.1.jar

# Clone project repository
WORKDIR /root
RUN git clone https://github.com/daxaurora/MIDS_W251_Benchmarking.git

# Run commands from /opt
# e.g.: in docker-compose.yml:
# worker:
#   image: spark-kafka
#   command: spark/bin/spark-class ...
WORKDIR /opt
ADD start-master.sh start-master.sh
ADD start-slave.sh start-slave.sh

# cd kafka \
# bin/zookeeper-server-start.sh -daemon config/zookeeper.properties \
# bin/kafka-server-start.sh -daemon config/server.properties

