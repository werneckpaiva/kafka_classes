from confluent_kafka import Consumer
from confluent_kafka.cimpl import TopicPartition

topic="test_ricardo"

consumer = Consumer({
    'bootstrap.servers': '172.20.0.101:9092,172.20.0.102:9092,172.20.0.103:9092',
    'group.id': 'sandbox-consumer-2',
    'auto.offset.reset': 'earliest',    # Start consuming from the beginning of the topic
    'enable.auto.commit': True,         # Enable auto-commit
    'auto.commit.interval.ms': 2_000,   # Commit offsets every 2 seconds
    'session.timeout.ms': 10_000,       # Session timeout in milliseconds (10 seconds)
    'heartbeat.interval.ms': 3_000,     # Heartbeat interval in milliseconds (3 seconds)
    'max.poll.interval.ms': 300_000,    # Tempo máximo entre chamadas sucessivas ao método poll()
})

def on_rebalance(consumer:Consumer, assignment:list[TopicPartition]):
    topics = ", ".join({str(tp.topic) for tp in assignment})
    partitions = ", ".join([str(tp.partition) for tp in assignment])
    print(f"Partitions assignment: Topic {topics}, paritions: {partitions}")

try:
    consumer.subscribe([topic], on_assign=on_rebalance)
    print(f"Consuming messages from {topic}")
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        elif msg.error():
            print(str(msg.error()))
        topic = msg.topic()
        partition = msg.partition()
        offset = msg.offset()
        key = int(msg.key().decode('utf-8')) if msg.key() else -1
        value = int(msg.value().decode('utf-8')) if msg.value() else 0
        print(f"Topic:{topic}, Partition:{partition:2d}, Offset:{offset:6d}, Key:{key:2d}, Payload:{value:13_d}")

except KeyboardInterrupt:
    # Handle Ctrl+C to gracefully stop the consumer
    print("Consumer stopped by user.")
finally:
    # Close the consumer connection
    consumer.close()
