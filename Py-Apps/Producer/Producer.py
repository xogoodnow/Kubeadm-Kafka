from kafka import KafkaProducer, KafkaConsumer
import time
import os
from kafka.admin import KafkaAdminClient, NewTopic

PRODUCER_INTERVAL=int(os.environ.get('PRODUCER_INTERVAL',2))
KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS')
KAFKA_INPUT_TOPIC_NAME = os.environ.get('KAFKA_INPUT_TOPIC_NAME')
normal_client = KafkaConsumer(bootstrap_servers=f"{KAFKA_BOOTSTRAP_SERVERS}:9092")
producer = KafkaProducer(bootstrap_servers=f"{KAFKA_BOOTSTRAP_SERVERS}:9092")
server_topics = normal_client.topics()
if KAFKA_INPUT_TOPIC_NAME not in server_topics:
    admin_client = KafkaAdminClient(bootstrap_servers=f"{KAFKA_BOOTSTRAP_SERVERS}:9092")
    topics_list = [NewTopic(name=KAFKA_INPUT_TOPIC_NAME, num_partitions=3, replication_factor=3)]
    admin_client.create_topics(new_topics=topics_list,validate_only=False)

while True:
    # send message containing the current time in milliseconds
    ms = int(time.time() * 1000)
    producer.send(KAFKA_INPUT_TOPIC_NAME, str(ms).encode())
    producer.flush()
    print(f'Sent {ms} to KAFKA')
    time.sleep(PRODUCER_INTERVAL)
~             