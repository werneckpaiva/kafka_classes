from confluent_kafka import Consumer
import json

# Configuração do consumidor
consumer = Consumer({
    'bootstrap.servers': '172.20.0.101:9092',
    'group.id': 'meu-grupo-consumidor2',
    'auto.offset.reset': 'latest',
    'enable.auto.commit': True,
})
consumer.subscribe(['sensor-metrics'])

state = dict()

try:
    cnt = 10
    while True:
        msg = consumer.poll(timeout=1.0)  # Timeout de 1 segundo
        if msg is None:  # Nenhum dado recebido no timeout
            continue
        if msg.error():
            print(str(msg.error()))
        else:
            key = msg.key().decode("utf-8") if msg.key() else None
            event = json.loads(msg.value().decode("utf-8"))
            state[event['sensor']] = max(state.get(event['sensor'], -1), event["temp"])
            cnt+=1
            if cnt % 10 == 0:
                cnt=0
                for sensor, max_temp in state.items():
                    print(f"{sensor}: max temp {max_temp}")

except KeyboardInterrupt:
    print('Encerrando consumidor...')
finally:
    consumer.close()



