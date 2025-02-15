from confluent_kafka import Consumer

# Configuração do consumidor
consumer = Consumer({
    'bootstrap.servers': '172.20.0.101:9092',
    'group.id': 'meu-grupo-consumidor2',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True,
})
consumer.subscribe(['playground1'])
try:
    while True:
        msg = consumer.poll(timeout=1.0)  # Timeout de 1 segundo
        if msg is None:  # Nenhum dado recebido no timeout
            continue
        if msg.error():
            print(str(msg.error()))
        else:
            key = msg.key().decode("utf-8") if msg.key() else None
            print(f'Tópico: {msg.topic()}, Partição: {msg.partition()}, Offset: {msg.offset()}, '
                  f'Chave: {key}, Valor: {msg.value().decode("utf-8")}')
except KeyboardInterrupt:
    print('Encerrando consumidor...')
finally:
    consumer.close()



