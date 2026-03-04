# Usando o KSQLDB

## Acessando o KSQL
```bash
# Versão nativa para Apple Silicon (M1/M2/M3)
docker run --rm -it --network kafka-network confluentinc/cp-ksqldb-cli:7.6.1 http://ksqldb-server:8088
```

## Explorando o ambiente
```sql
-- Exibindo os tópicos
show topics;
```

## Consumindo um tópico e exibindo na tela
```sql
print "users";
```

## Criando um stream tipado
```sql
CREATE STREAM users (
    user_id VARCHAR KEY,
    name VARCHAR,
    age INT,
    email VARCHAR,
    points INT)
WITH (KAFKA_TOPIC='users', VALUE_FORMAT='JSON');
```

## Criando agregações com Janela (Tumbling Window)

Exemplo 1: Estatísticas Globais (a cada 20 segundos)
```sql
CREATE TABLE GLOBAL_STATS AS
SELECT
    'global' as stats_key,
    COUNT(*) AS total_messages,
    AVG(age) AS average_age,
    AVG(points) AS average_points,
    MAX(points) AS max_points
FROM users
WINDOW TUMBLING (SIZE 20 SECONDS)
GROUP BY 'global'
EMIT CHANGES;
```

Exemplo 2: Média de pontos por Usuário (a cada 1 minuto)
```sql
CREATE TABLE USER_POINTS_STATS AS
SELECT
    user_id,
    AVG(points) AS avg_points,
    COUNT(*) AS updates_count
FROM users
WINDOW TUMBLING (SIZE 1 MINUTE)
GROUP BY user_id
EMIT CHANGES;
```

## Consultando os resultados
```sql
SELECT * FROM GLOBAL_STATS EMIT CHANGES;
SELECT * FROM USER_POINTS_STATS EMIT CHANGES;
```

# Limpeza (DCL)

## Excluindo um stream
```sql
DROP STREAM users;
```

## Excluindo tabelas
```sql
DROP TABLE GLOBAL_STATS;
DROP TABLE USER_POINTS_STATS;
```