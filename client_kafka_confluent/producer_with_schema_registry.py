import random
from time import sleep

from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka import SerializingProducer, KafkaException

# Create the topic first!
# ./kafka_2.13-3.9.0/bin/kafka-topics.sh --create \
#   --bootstrap-server 172.20.0.101:9092 \
#   --topic users \
#   --partitions 4 \
#   --replication-factor 3 \
#   --config retention.ms=259200000 \
#   --config segment.bytes=16777216

# Kafka Connect config
# curl -X POST -H "Content-Type: application/json" -d '{
# "name": "postgres-users-sink",
# "config": {
#     "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
#     "connection.url": "jdbc:postgresql://172.20.0.5:5432/kafka_example",
#     "connection.user": "my_user",
#     "connection.password": "abcd1234",
#     "topics": "users",
#     "insert.mode": "insert",
#     "pk.mode": "none",
#     "pk.fields": "id",
#     "auto.create": "false",
#     "auto.evolve": "false",
#     "table.name.format": "users",
#     "tasks.max": "2",
#     "key.converter": "org.apache.kafka.connect.storage.StringConverter",
#     "key.converter.schemas.enable": "false",
#     "value.converter": "io.confluent.connect.json.JsonSchemaConverter",
#     "value.converter.schema.registry.url": "http://172.20.0.20:8081",
#     "errors.tolerance": "all",
#     "errors.deadletterqueue.topic.name": "my-connector-errors",
#     "errors.deadletterqueue.topic.replication.factor": "3",
#     "errors.deadletterqueue.context.headers.enable": "true"
# }
# }' http://172.20.0.10:8083/connectors | jq .


# Schema Registry configuration
schema_registry_conf = {'url': 'http://172.20.0.20:8081'}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

# Define the JSON schema
schema_str = """
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "User",
  "type": "object",
  "properties": {
    "name": { "type": "string" },
    "age": { "type": "integer", "minimum": 0, "maximum": 120 },
    "email": { "type": "string" }
  },
  "required": ["name", "age", "email"]
}
"""

def generate_contact() -> dict[str, any]:
    first_name = random.choice([
        "Alice", "Bob", "Charlie", "Diana", "Eve",
        "Frank", "Grace", "Hank", "Ivy", "Jack"
    ])
    last_name = random.choice([
        "Smith", "Johnson", "Williams", "Brown", "Jones",
        "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"
    ])
    message = {
        "name": f"{first_name} {last_name}",
        "age": random.randint(10, 50),
        "email": f"{first_name.lower()}.{last_name.lower()}@example.com"
    }
    return message

json_serializer = JSONSerializer(schema_str, schema_registry_client)


topic='users'

producer = SerializingProducer({
    'bootstrap.servers': '172.20.0.101:9092,172.20.0.102:9092,172.20.0.103:9092',
    'client.id': topic,
    'acks': 'all',
    'batch.size': 500,
    'linger.ms': 1_000,
    'message.timeout.ms': 5_000,
    'retries': 3,
    'value.serializer': json_serializer
})

count_messages = 0
try:
    print(f"Producing messages to topic {topic}")
    while True:
        try:
            contact = generate_contact()
            producer.produce(topic=topic, value=contact)
        except KafkaException as e:
            print(f"Error sending message: {e}")
        except BufferError as e:
            producer.flush()
        count_messages += 1
        print(".", end='', flush=True)

        sleep(random.uniform(0, 1))

except KeyboardInterrupt:
    print(" done")
finally:
    # Send all pending messages
    producer.flush()

print(f"{count_messages} messages sent to topic {topic}")