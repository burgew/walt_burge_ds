# MIDS_W251_YetAnotherTwitterSentimentAnalyzer_YATSA
This repo represents group work on a UC Berkeley MIDS  Final Project for the class "W251 - Scaling Up! Really Big Data."

Group members: Paul Durkin, Ye (Kevin) Pang, Laura Williams, Walt Burge, Matt Proetsch

The final paper and presentation are stored in the main directory of this repo.

Directory contents are as follows:

**Ansible** contains configuration playbooks and scripts for managing Kafka, Zookeeper, Spark, and Cassandra cluster nodes.

**documentation** contains instructions for multiple components of this project, including server configuration, user interface setup, NLP server setup, and initiating the Kafka/Spark stream.

**monitor** contains scripts for monitoring the health of servers and services throughout the project architecture.

**Sandbox** contains interim scripts not used in the final solution, including experiments to containerize the process using Docker Swarm, experiments with provisioning via Terraform, and interim streaming scripts.

**SoftlayerTemplates** contains default server configuration options for provisioning machines via Softlayer.

**streaming** contains scripts for initiating the Twitter stream via Kafka and initiating stream processing via Spark.

**Utilities** contains scripts for managing and inspecting components of the Cassandra database.
