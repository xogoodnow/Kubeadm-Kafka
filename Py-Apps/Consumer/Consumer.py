from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
import os
import datetime
import time

# get the environment variables
KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS')
KAFKA_INPUT_TOPIC_NAME = os.environ.get('KAFKA_INPUT_TOPIC_NAME')
KAFKA_OUTPUT_TOPIC_NAME = os.environ.get('KAFKA_OUTPUT_TOPIC_NAME')
normal_client = KafkaConsumer(bootstrap_servers=f"{KAFKA_BOOTSTRAP_SERVERS}:9092")
server_topics = normal_client.topics()
if KAFKA_OUTPUT_TOPIC_NAME not in server_topics:
    admin_client = KafkaAdminClient(bootstrap_servers=f"{KAFKA_BOOTSTRAP_SERVERS}:9092")
    topics_list = [NewTopic(name=KAFKA_OUTPUT_TOPIC_NAME, num_partitions=3, replication_factor=3)]
    admin_client.create_topics(new_topics=topics_list,validate_only=False)

while True:
    consumer = KafkaConsumer(KAFKA_INPUT_TOPIC_NAME, bootstrap_servers=f"{KAFKA_BOOTSTRAP_SERVERS}:9092")
    producer = KafkaProducer(bootstrap_servers=f"{KAFKA_BOOTSTRAP_SERVERS}:9092")
    for message in consumer:
        # convert message to rfc3339 format
        # https://stackoverflow.com/questions/10607759/python-convert-epoch-to-rfc-3339-timestamp
        rfc3339 = datetime.datetime.fromtimestamp(int(message.value.decode())/1000).isoformat()
        producer.send(KAFKA_OUTPUT_TOPIC_NAME, rfc3339.encode())
        producer.flush()
        print(f"Sent {rfc3339} to {KAFKA_OUTPUT_TOPIC_NAME}")
    time.sleep(1)