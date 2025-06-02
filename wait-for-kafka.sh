#!/bin/bash

HOST="kafka"
PORT=9092

echo "Waiting for Kafka at $HOST:$PORT..."

while ! (echo > /dev/tcp/$HOST/$PORT) >/dev/null 2>&1; do
  echo "Kafka not available yet..."
  sleep 1
done

echo "Kafka is up!"
