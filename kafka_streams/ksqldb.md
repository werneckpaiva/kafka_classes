# Usando o KSQLDB

## Acessando o KSQL
```
docker run --rm -it --network kafka-network confluentinc/ksqldb-cli:latest ksql http://ksqldb-server:8088
```

##Exibindo os tópicos
```
show topics;
```

## Consumindo um tópico e exibindo na tela
```
print "meu-topico";
```

## Criando um stream tipado
Exemplo 1:
```
CREATE STREAM users (
    name VARCHAR,
    age INT,
    email VARCHAR)
WITH (KAFKA_TOPIC='users', VALUE_FORMAT='JSON');
```
Exemplo 2:
```
CREATE STREAM "random_numbers" (
    num_key VARCHAR KEY,
    num_value VARCHAR)
WITH (KAFKA_TOPIC='random-numbers',
      KEY_FORMAT = 'KAFKA',
      VALUE_FORMAT='KAFKA');

CREATE STREAM "random_numbers_avro" 
WITH(VALUE_FORMAT='Avro') AS 
    SELECT
        num_key,
        CAST(num_value AS BIGINT) as num_value
    FROM "random_numbers";
```


## Criando uma agregação
```
CREATE TABLE AVERAGE_NUMBERS_BY_KEY AS
SELECT
    num_key,
    ROWTIME as window_start_time,
    MAX(num_value) AS max_value,
    MIN(num_value) AS min_value,
    AVG(num_value) AS average_value,
    COUNT(num_value) AS count_value
FROM "random_numbers_avro"
WINDOW TUMBLING (SIZE 10 SECONDS)
GROUP BY num_key
EMIT CHANGES;
```

## Consultando uma tabela
```
SELECT * FROM AVERAGE_NUMBERS_BY_KEY;
```

# Excluindo um stream
```
DROP STREAM "meu_stream";
```

# Excluindo uma tabela
```
DROP TABLE MY_TABLE_NAME;
```