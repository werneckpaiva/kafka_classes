# Kafka Connect Guide

Este documento detalha como configurar, gerenciar e utilizar o Kafka Connect, cobrindo desde a execução do serviço até a configuração de diferentes tipos de conectores.

---

## 1. Modos de Execução

### Rodando o binário diretamente
O Kafka Connect vem junto com a distribuição do Kafka. Para rodar em modo distribuído (recomendado para produção), edite o arquivo `./config/connect-distributed.properties`:

*   **bootstrap.servers**: Endereço dos brokers.
*   **group.id**: ID do cluster Connect.
*   **plugin.path**: Caminho para os arquivos JAR dos conectores.

Execute com:
```bash
./bin/connect-distributed.sh ./config/connect-distributed.properties
```

### Rodando via Docker Compose
Usar Docker Compose facilita a gerência de dependências como bancos de dados. Exemplo de serviço no `docker-compose.yaml`:

```yaml
services:
  kafka-connect:
    image: confluentinc/cp-kafka-connect:latest
    container_name: kafka-connect
    networks:
      my_network:
        ipv4_address: 172.20.0.10
    depends_on:
      - postgres
      - redis
      - schema-registry
    environment:
      CONNECT_BOOTSTRAP_SERVERS: "172.20.0.101:9092,172.20.0.102:9092,172.20.0.103:9092"
      CONNECT_REST_PORT: 8083
      CONNECT_GROUP_ID: "connect-cluster"
      CONNECT_CONFIG_STORAGE_TOPIC: "connect-configs"
      CONNECT_OFFSET_STORAGE_TOPIC: "connect-offsets"
      CONNECT_STATUS_STORAGE_TOPIC: "connect-status"
      CONNECT_KEY_CONVERTER: "org.apache.kafka.connect.storage.StringConverter"
      CONNECT_VALUE_CONVERTER: "org.apache.kafka.connect.json.JsonConverter"
      CONNECT_KEY_CONVERTER_SCHEMAS_ENABLE: "false"
      CONNECT_VALUE_CONVERTER_SCHEMAS_ENABLE: "false"
      CONNECT_PLUGIN_PATH: "/usr/share/java,/usr/share/confluent-hub-components,/opt/kafka/connectors"
    volumes:
      - ./connectors:/opt/kafka/connectors
```

---

## 2. Gerenciamento via REST API

O Kafka Connect é gerenciado através de uma API HTTP na porta `8083`.

| Ação | Método | Endpoint |
| :--- | :--- | :--- |
| Listar conectores | `GET` | `/connectors` |
| Criar conector | `POST` | `/connectors` |
| Ver configuração | `GET` | `/connectors/{name}` |
| Atualizar config | `PUT` | `/connectors/{name}/config` |
| Ver status | `GET` | `/connectors/{name}/status` |
| Reiniciar conector | `POST` | `/connectors/{name}/restart` |
| Deletar conector | `DELETE` | `/connectors/{name}` |

---

## 3. Exemplos de Conectores

### A. Redis Sink Connector
Utilizado para persistir dados no Redis. Suporta os tipos `JSON` e `HASH`.

#### Configuração (JSON Mode)
```bash
curl -X POST -H "Content-Type: application/json" --data '{
  "name": "redis-sink-json",
  "config": {
    "connector.class": "com.redis.kafka.connect.RedisSinkConnector",
    "tasks.max": "2",
    "topics": "test-redis-connector",
    "redis.uri": "redis://172.20.0.6:6379",
    "redis.type": "JSON",
    "redis.keyspace": "user:contact",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "true"
  }
}' http://172.20.0.10:8083/connectors
```

#### Configuração (HASH Mode)
```bash
curl -X POST -H "Content-Type: application/json" --data '{
  "name": "redis-sink-hash",
  "config": {
    "connector.class": "com.redis.kafka.connect.RedisSinkConnector",
    "tasks.max": "2",
    "topics": "test-redis-connector",
    "redis.uri": "redis://172.20.0.6:6379",
    "redis.type": "HASH",
    "redis.keyspace": "user:contact",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "true"
  }
}' http://172.20.0.10:8083/connectors
```

#### Alterando a configuração (ex: aumentar tasks)
```bash
curl -X PUT -H "Content-Type: application/json" --data '{
    "connector.class": "com.redis.kafka.connect.RedisSinkConnector",
    "tasks.max": "4",
    "topics": "test-redis-connector",
    "redis.uri": "redis://172.20.0.6:6379",
    "redis.type": "HASH",
    "redis.keyspace": "user:contact",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "true"
}' http://172.20.0.10:8083/connectors/redis-sink-hash/config
```

#### Verificando dados no Redis
```bash
# Listando todas as chaves:
docker exec my-redis redis-cli KEYS "user:contact:*"

# Se for JSON:
docker exec my-redis redis-cli JSON.GET "user:contact:34"
docker exec my-redis redis-cli JSON.GET "user:contact:34" ".email"

# Se for HASH:
docker exec my-redis redis-cli HGETALL "user:contact:34"
docker exec my-redis redis-cli HGET "user:contact:34" email
```

---

### B. Postgres Sink (JDBC)
Copia dados de um tópico para uma tabela no PostgreSQL.

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "name": "postgres-sink",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
    "connection.url": "jdbc:postgresql://172.20.0.5:5432/kafka_example",
    "connection.user": "my_user",
    "connection.password": "abcd1234",
    "topics": "contacts",
    "insert.mode": "upsert",
    "pk.mode": "record_value",
    "pk.fields": "id",
    "auto.create": "true",
    "table.name.format": "contacts",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "true"
  }
}' http://172.20.0.10:8083/connectors
```

---

### C. File Stream Sink (Playground)
Simplesmente grava as mensagens em um arquivo de texto. Útil para testes rápidos.

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "name": "file-sink",
  "config": {
    "connector.class": "org.apache.kafka.connect.file.FileStreamSinkConnector",
    "topics": "test-file",
    "file": "/tmp/output.txt"
  }
}' http://172.20.0.10:8083/connectors
```

---

## 4. Enviando dados (Producers)

Para que conectores como o JDBC ou Redis (com schema) funcionem, as mensagens no Kafka devem conter o `schema` e o `payload`.

Exemplo usando `kcat`:

```bash
echo '1:{
  "schema": {
    "type": "struct",
    "fields": [
      { "field": "id", "type": "string" },
      { "field": "name", "type": "string" },
      { "field": "email", "type": "string" }
    ]
  },
  "payload": {
    "id": "1",
    "name": "Ricardo",
    "email": "ricardo@example.com"
  }
}' | kcat -P -b 172.20.0.101:9092 -t test-redis-connector -K :
```

Para enviar múltiplos dados via script:
```bash
for i in {1..10}
do
cat <<EOF | tr -d '\n' | kcat -P -b 172.20.0.101:9092 -t test-topic -K :
$i:{
  "schema": {
    "type": "struct",
    "fields": [
      { "field": "id", "type": "string" },
      { "field": "name", "type": "string" },
      { "field": "email", "type": "string" }
    ]
  },
  "payload": {
    "id": "$i",
    "name": "User $i",
    "email": "user$i@example.com"
  }
}
EOF
done
```
