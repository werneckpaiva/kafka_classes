from confluent_kafka import Consumer, KafkaError

topic="playground1"

# --- Configuração do Consumidor ---
consumer_config = {
    'bootstrap.servers': '172.20.0.101:9092',
    'group.id': 'meu-grupo-consumidor',
    'auto.offset.reset': 'latest',
    'enable.auto.commit': False,
    'isolation.level': 'read_committed'  # Só lê mensagens commitadas
}
consumer = Consumer(consumer_config)
consumer.subscribe([topic])

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Erro: {msg.error()}")
            continue

        print(f"Message: {msg.key().decode('utf-8')}:{msg.value().decode('utf-8')}")

except KeyboardInterrupt:
    print("Encerrando...")
finally:
    consumer.close()