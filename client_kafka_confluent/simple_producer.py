from confluent_kafka import Producer

# Função de callback para entrega (opcional)
def delivery_report(err, msg):
    if err is not None:
        print(f'Falha ao entregar a mensagem: {err}')
    else:
        print(f'Mensagem entregue: {msg.topic()} [{msg.partition()}] @ {msg.offset()}')

# Configuração do produtor
producer = Producer({
    'bootstrap.servers': '172.20.0.101:9092,172.20.0.102:9092,172.20.0.103:9092',
    'client.id': 'meu-produtor',
})

# Envio de mensagem (assíncrono)
producer.produce('playground1', key='chave1', value='Minha mensagem', callback=delivery_report)

# Garante que mensagens do buffer sejam enviadas
producer.flush()









