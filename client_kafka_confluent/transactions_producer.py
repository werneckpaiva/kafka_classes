from confluent_kafka import Producer, KafkaException
import uuid

topic="playground1"

# --- Configuração do Produtor ---
producer_config = {
    'bootstrap.servers': '172.20.0.101:9092',
    'transactional.id': f'produtor-tx-{uuid.uuid4()}',  # ID único!
    'enable.idempotence': True,  # Obrigatório para transações
    "acks": "all"
}
producer = Producer(producer_config)

producer.init_transactions()

try:
    print("Início da primeira transação")
    producer.begin_transaction()
    # --- Envio de Mensagens (dentro da transação) ---
    producer.produce(topic, key='chave1', value='valor1')
    producer.produce(topic, key='chave2', value='valor2')
    # --- Confirmação da Transação (inclui flush) ---
    producer.commit_transaction()
    print("Transação confirmada!")

    print("Início da segunda transação")
    producer.begin_transaction()
    producer.produce(topic, key='chave3', value='valor3')
    producer.produce(topic, key='chave4', value='valor4')
    producer.abort_transaction()
    print("Transação cancelada!")

except KafkaException as e:
    print(f"Erro na transação: {e}")
    producer.abort_transaction()  # Aborta em caso de erro
    print("Transação abortada.")
