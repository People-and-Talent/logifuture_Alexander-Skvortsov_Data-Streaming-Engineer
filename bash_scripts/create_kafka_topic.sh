#!/bin/bash

# Wait for Kafka to start up
sleep 10

# Create the Kafka topic
kafka-topics.sh --create --topic transactions_topic --bootstrap-server kafka:9092 --replication-factor 1 --partitions 1

# Keep the container running
#tail -f /dev/null
