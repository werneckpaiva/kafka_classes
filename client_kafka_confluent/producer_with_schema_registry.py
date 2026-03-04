import random
from time import sleep
import hashlib

from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka import SerializingProducer, KafkaException

# Create the topic first!
# ./kafka/bin/kafka-topics.sh --create \
#   --bootstrap-server 172.20.0.101:9092 \
#   --topic users \
#   --partitions 4 \
#   --replication-factor 3 \
#   --config retention.ms=259200000 \
#   --config segment.bytes=16777216

# Kafka Connect config
# curl -X POST -H "Content-Type: application/json" -d '{
# "name": "redis-users-sink",
# "config": {
#     "connector.class": "com.redis.kafka.connect.RedisSinkConnector",
#     "redis.uri": "redis://172.20.0.6:6379",
#     "topics": "users",
#     "tasks.max": "2",
#     "key.converter": "org.apache.kafka.connect.storage.StringConverter",
#     "key.converter.schemas.enable": "false",
#     "value.converter": "io.confluent.connect.json.JsonSchemaConverter",
#     "value.converter.schema.registry.url": "http://172.20.0.45:8081",
#     "redis.keyspace": "users",
#     "redis.type": "HASH",
#     "errors.tolerance": "all"
# }
# }' http://172.20.0.10:8083/connectors | jq .

# Verificando os dados no Redis:
# docker exec my-redis redis-cli KEYS "users:*"
# docker exec my-redis redis-cli HGETALL "users:1"
# docker exec my-redis redis-cli HGET "users:1" name
# docker exec my-redis redis-cli HGET "users:1" age
# docker exec my-redis redis-cli HGET "users:1" email


# Schema Registry configuration
schema_registry_conf = {'url': 'http://172.20.0.45:8081'}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

# Define the JSON schema
schema_str = """
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "User",
  "type": "object",
  "properties": {
    "user_id": { "type": "string" },
    "name": { "type": "string" },
    "age": { "type": "integer", "minimum": 0, "maximum": 120 },
    "email": { "type": "string" },
    "points": { "type": "integer" }
  },
  "required": ["user_id", "name", "age", "email", "points"]
}
"""

def generate_contact_points() -> dict[str, any]:
    first_name = random.choice([
        "Adriano", "Bruno", "Caio", "Daniel", "Eduardo",
        "Fabio", "Gabriel", "Heitor", "Igor", "Joao",
        "Kleber", "Leonardo", "Marcelo", "Nelson", "Otavio",
        "Paulo", "Queiroz", "Ricardo", "Samuel", "Tiago",
        "Ulysses", "Vitor", "Wagner", "Xavier", "Yuri", "Zeca"
    ])
    last_name = random.choice([
        "Almeida", "Barbosa", "Costa", "Duarte", "Esteves",
        "Freitas", "Gomes", "Henrique", "Ibrahim", "Jorge",
        "Koury", "Lima", "Mendes", "Nunes", "Oliveira",
        "Pereira", "Queiros", "Ribeiro", "Silva", "Teixeira",
        "Uchoa", "Vieira", "Werneck", "Ximenes", "Yamada", "Zonta"
    ])
    name = f"{first_name} {last_name}"
    user_id = hashlib.sha256(name.encode('utf-8')).hexdigest()[:12]
    
    contact_points = {
        "user_id": user_id,
        "name": name,
        "age": random.randint(10, 60),
        "email": f"{first_name.lower()}.{last_name.lower()}@example.com",
        "points": random.randint(0, 100)
    }
    return contact_points

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

try:
    print(f"Producing messages to topic {topic}")
    while True:
        try:
            contact_points = generate_contact_points()
            producer.produce(topic=topic, key=contact_points["user_id"].encode('utf-8'), value=contact_points)
        except KafkaException as e:
            print(f"Error sending message: {e}")
        except BufferError as e:
            producer.flush()
        
        print(".", end='', flush=True)

        sleep(random.uniform(0, 1))

except KeyboardInterrupt:
    print(" done")
finally:
    # Send all pending messages
    producer.flush()

print(f"Finished producing to topic {topic}")