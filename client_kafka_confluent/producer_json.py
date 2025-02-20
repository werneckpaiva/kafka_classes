from confluent_kafka import Producer, KafkaException
import time
import random
import json

brokers=[]

topic="topic-em-4-brokers"

producer = Producer({
    'bootstrap.servers': '172.20.0.101:9092,172.20.0.102:9092,172.20.0.103:9092',
    'client.id': 'sensor-producer',
    'acks': 'all', # or "1" or "0"
    'batch.size': 10_000, # 10_000 bytes
    'linger.ms': 2_000,   # 2 seconds
    'message.timeout.ms': 10_000, # 10 seconds
    'retries': 3,
})

count_messages = 0
try:
    print(f"Producing messages to topic {topic}")
    # Continuously send messages
    while True:
        sensor_id=random.randint(1, 10)
        event = {
            "sensor": f"sensor_{sensor_id}",
            "value": random.randint(1, 1_000_000),
            "temp": random.random() * 40
        }
        try:
            producer.produce(topic,
                         key=str(sensor_id).encode('utf-8'),
                         value=json.dumps(event).encode('utf-8')
            )
        except KafkaException as e:
            print(f"Error sending message: {e}")
        except BufferError as e:
            producer.flush()
        count_messages += 1
        print(".", end='', flush=True)

        time.sleep(random.uniform(0, 1))

except KeyboardInterrupt:
    # Handle Ctrl+C to gracefully stop the producer
    print(" done")
finally:
    # Send all pending messages
    producer.flush()

    print(f"{count_messages} messages sent to topic {topic}")
