from confluent_kafka import Producer, KafkaException, Consumer
import uuid

input_topic="playground1"
output_topic="playground2"

BOOTSTRAP_SERVERS = '172.20.0.101:9092'

group_id='exactly-once-group'

producer = Producer({
    'bootstrap.servers': BOOTSTRAP_SERVERS,
    'transactional.id': f'produtor-tx-{uuid.uuid4()}',  # ID único!
    'enable.idempotence': True,  # Obrigatório para transações
    "acks": "all"
})

consumer = Consumer({
    'bootstrap.servers': BOOTSTRAP_SERVERS,
    'group.id': group_id,
    'auto.offset.reset': 'latest',
    'enable.auto.commit': False,
    'isolation.level': 'read_committed'  # Só lê mensagens commitadas
})


producer.init_transactions()

consumer.subscribe([input_topic])

try:
    while True:
        msg = consumer.poll(1.0)  # Poll messages

        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        producer.begin_transaction()

        try:
            # Process message
            transformed_value = msg.value().decode("utf-8").upper()  # Example processing
            print(f"Processing: {msg.value()} -> {transformed_value}")

            # Produce transformed message to output topic
            producer.produce(output_topic, key=msg.key(), value=transformed_value)

            # Send offsets to transaction (atomic commit)
            producer.send_offsets_to_transaction(
                consumer.position(consumer.assignment()), 
                consumer.consumer_group_metadata()
            )
            
            # Commit transaction
            producer.commit_transaction()

            print("Transação efetuada")

        except KafkaException as e:
            print(f"Transaction failed: {e}")
            producer.abort_transaction()

except KeyboardInterrupt:
    print("Stopping consumer-producer...")

finally:
    consumer.close()

