from confluent_kafka import Producer, KafkaException
import time
import random

brokers=[]

topic="test-ricardo"

producer = Producer({
    'bootstrap.servers': '172.20.0.101:9092,172.20.0.102:9092,172.20.0.103:9092',
    'client.id': 'test-ricardo',
    'acks': 'all', # or "1" or "0"
    'batch.size': 10_000, # 10_000 bytes
    'linger.ms': 2_000,   # 2 seconds
})

count_messages = 0
try:
    print(f"Producing messages to topic {topic}")
    # Continuously send messages
    while True:
        key = random.randint(1, 50)
        # Generate a random value between 1 and 1 billion
        value = random.randint(1, 1_000_000_000)

        # Send the message to the Kafka topic with the specified key
        try:
            producer.produce(topic,
                         key=str(key).encode('utf-8'),
                         value=str(value).encode('utf-8')
            )
        except KafkaException as e:
            print(f"Error sending message: {e}")
        except BufferError as e:
            producer.flush()
        count_messages += 1
        print(".", end='', flush=True)

        time.sleep(random.uniform(0, .5))

except KeyboardInterrupt:
    # Handle Ctrl+C to gracefully stop the producer
    print(" done")
finally:
    # Send all pending messages
    producer.flush()

    print(f"{count_messages} messages sent to topic {topic}")
