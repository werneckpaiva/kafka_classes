# Guia de Instalação do Apache Kafka 4.1.1 (Modo KRaft)

Este guia descreve os passos para instalar e configurar um cluster de 3 nós do Apache Kafka 4.1.1 utilizando o modo KRaft, dividido em dois métodos: instalação direta em máquinas virtuais no Google Cloud ou localmente usando Docker Compose.

---

## Instalação no Google Cloud

O Google Cloud oferece $300 de crédito por 90 dias quando você cria uma nova conta, mas também disponibiliza um conjunto de serviços gratuitos (Free Tier) sem restrição de tempo. É possível usá-los indefinidamente, desde que você não exceda os [limites definidos](https://cloud.google.com/free/docs/free-cloud-features#free-tier-usage-limits). Acesse [https://cloud.google.com/free](https://cloud.google.com/free) para saber mais.

Iremos usar máquinas virtuais para instalar nosso Cluster Kafka. O Free Tier permite criar instâncias e2-micro que podem permanecer em execução durante todo o mês. Como criaremos 3 servidores Kafka, utilizaremos 3 instâncias que podem rodar de maneira contínua e gratuita por até ⅓ do mês (10 dias).

Para ter acesso ao Free Tier, você precisa de uma conta no Google Cloud, e ela deve estar com o pagamento habilitado, para o caso de você exceder os limites gratuitos. Caso esteja no período de teste (primeiros 90 dias), não é necessário habilitar o pagamento.

Certifique-se de que você já tem um projeto em sua conta. Se não tiver, siga este passo a passo: [https://www.youtube.com/watch?v=yt56ICdAJEk](https://www.youtube.com/watch?v=yt56ICdAJEk)


### Criando as VMs
Crie 3 instâncias com as configurações a seguir. Se tiver alguma dúvida, siga este vídeo: [https://www.youtube.com/watch?v=FLLnxIDPUMQ](https://www.youtube.com/watch?v=FLLnxIDPUMQ)

#### Configuração da Máquina (Machine Configuration)
- **Names**: `kafka-broker-1` (`kafka-broker-2` e `kafka-broker-3` para os outros nós).
- **Region**: Mesma região para as 3 (ex: `us-central1`). Selecione entre **us-west1, us-central1 ou us-east1** para o Free Tier.
- **Zone**: Mesma zona para as 3 (ex: `us-central1-a`). Não use Any.
- **Machine**: E2 (Low cost)
- **Machine Type**: `e2-micro` (2 vCPU, 1 GB RAM).

#### Sistema Operacional e Armazenamento (OS and storage)
- **Operating System**: Debian ou Ubuntu.
- **Boot Disk type**: Selecione **Standard Persistent Disk** (o tipo "Balanced", que é o default, não está incluso no Free Tier).
- **Size (GB)**: 10

#### Proteção de Dados (Data Protection)
- **Backups**: Selecione **No Backups** (para evitar cobranças de armazenamento de backups).

### Networking e Firewall
As VMs criadas no Google cloud, apesar de terem um IP público na Internet (sem custo adicional) não têm nenhuma porta exposta.
- **Network tags**: Adicione a tag `kafka-broker` em cada VM.

Crie uma regra no firewall para abrir a porta do Kafka. Todas as máquinas do cluster que tiverem a Network Tag `kafka-broker` poderão receber conexão externa.
1. Vá em **Network Security** > **Firewall Policies** (busque por Firewall na barra de busca).
2. Clique em **+ Create Firewall Rule**.
3. **Name**: `allow-kafka-broker`.
4. **Targets**: `Specified target tags`.
5. **Target tags**: `kafka-broker`
6. **Source IPv4 ranges**: `0.0.0.0/0` (ou o IP da sua rede para maior segurança).
7. **Protocols and ports**: TCP `9092`.
8. Clique em **Create**.

### Instalação e Configuração dos Servidores

Acesse o shell SSH da máquina clicando em “SSH”. Isso abrirá uma nova janela que exibirá o prompt de comando do shell.

#### Instalando o Java
O Kafka 4.1.1 requer Java 17 ou superior. No terminal de cada VM, execute:

```bash
sudo apt update
sudo apt install -y default-jdk
java --version
```

#### Download e Instalação
Vamos instalar os binários em `/opt/kafka`:

```bash
wget https://archive.apache.org/dist/kafka/4.1.1/kafka_2.13-4.1.1.tgz
tar -xzf kafka_2.13-4.1.1.tgz
sudo mv kafka_2.13-4.1.1 /opt/kafka
```

#### Configuração do Cluster (KRaft)
Edite o arquivo `/opt/kafka/config/server.properties` em cada nó usando o editor de sua preferência (ex: `nano` ou `vi`).

Abaixo um exemplo para o **Nó 1** (`kafka-broker-1`). Ajuste o `node.id` e `advertised.listeners` para os outros nós.

```properties
# A função do nó no cluster
process.roles=broker,controller

# ID único do nó (1, 2 ou 3)
node.id=1

# Configuração do Quorum (Kafka 4.1+)
controller.quorum.bootstrap.servers=kafka-broker-1:9093,kafka-broker-2:9093,kafka-broker-3:9093

# Endereços de escuta
listeners=PLAINTEXT://:9092,CONTROLLER://:9093
inter.broker.listener.name=PLAINTEXT
controller.listener.names=CONTROLLER

# Endereço anunciado para clientes externos (substitua pelo IP público se necessário)
advertised.listeners=PLAINTEXT://kafka-broker-1:9092

# Diretório de dados
log.dirs=/var/kafka/data
```

#### Formatação do Armazenamento
Crie o diretório de dados e atribua as permissões:

```bash
sudo mkdir -p /var/kafka/data
sudo chown -R $USER:$USER /var/kafka
```

Gere o **Cluster ID** e os **Directory IDs** para formatar o armazenamento. Este passo de geração deve ser feito **apenas uma vez** (no Nó 1), e os valores resultantes devem ser usados em todos os nós.

```bash
# 1. Gere os IDs (Apenas no Nó 1)
KAFKA_CLUSTER_ID=$(/opt/kafka/bin/kafka-storage.sh random-uuid)
DIR_ID_1=$(/opt/kafka/bin/kafka-storage.sh random-uuid)
DIR_ID_2=$(/opt/kafka/bin/kafka-storage.sh random-uuid)
DIR_ID_3=$(/opt/kafka/bin/kafka-storage.sh random-uuid)

# Exiba os valores para copiar nos outros nós
echo "KAFKA_CLUSTER_ID=$KAFKA_CLUSTER_ID"
echo "DIR_ID_1=$DIR_ID_1"
echo "DIR_ID_2=$DIR_ID_2"
echo "DIR_ID_3=$DIR_ID_3"
```

**Formate o armazenamento em cada um dos 3 nós** usando os mesmos IDs gerados acima:

```bash
/opt/kafka/bin/kafka-storage.sh format \
    -t $KAFKA_CLUSTER_ID \
    -c /opt/kafka/config/server.properties \
    --initial-controllers "1@kafka-broker-1:9093:$DIR_ID_1,2@kafka-broker-2:9093:$DIR_ID_2,3@kafka-broker-3:9093:$DIR_ID_3"
```

#### Iniciando o Serviço e Verificação de Logs
Inicie o servidor Kafka em modo daemon:

```bash
/opt/kafka/bin/kafka-server-start.sh -daemon /opt/kafka/config/server.properties
```

Para acompanhar o funcionamento e depurar problemas:

```bash
# Exibir o log principal do servidor
tail -f /opt/kafka/logs/server.log
```

### Teste de Acesso
Para validar se o cluster está operacional, liste os tópicos e crie um tópico de teste:

```bash
# Listar tópicos existentes
/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list

# Criar um tópico de teste
/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create \
    --topic aula-kafka --partitions 3 --replication-factor 3
```

---

## Usando Docker Compose

### Configurando um cluster com 3 brokers
`docker-compose.yml`

```yaml
services:
  kafka1:
    image: apache/kafka:4.1.1
    hostname: kafka1
    container_name: kafka1
    networks:
      my_network:
        ipv4_address: 172.20.0.101
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://172.20.0.101:9092
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka1:9093,2@kafka2:9093,3@kafka3:9093
      CLUSTER_ID: 'fEhAzqLPS8aklU4iXPqqbA'
      KAFKA_LOG_DIRS: /var/kafka/data
    volumes:
      - ./kafka-data1:/var/kafka/data

  kafka2:
    image: apache/kafka:4.1.1
    hostname: kafka2
    container_name: kafka2
    networks:
      my_network:
        ipv4_address: 172.20.0.102
    environment:
      KAFKA_NODE_ID: 2
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://172.20.0.102:9092
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka1:9093,2@kafka2:9093,3@kafka3:9093
      CLUSTER_ID: 'fEhAzqLPS8aklU4iXPqqbA'
      KAFKA_LOG_DIRS: /var/kafka/data
    volumes:
      - ./kafka-data2:/var/kafka/data

  kafka3:
    image: apache/kafka:4.1.1
    hostname: kafka3
    container_name: kafka3
    networks:
      my_network:
        ipv4_address: 172.20.0.103
    environment:
      KAFKA_NODE_ID: 3
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://172.20.0.103:9092
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka1:9093,2@kafka2:9093,3@kafka3:9093
      CLUSTER_ID: 'fEhAzqLPS8aklU4iXPqqbA'
      KAFKA_LOG_DIRS: /var/kafka/data
    volumes:
      - ./kafka-data3:/var/kafka/data

networks:
  my_network:
    name: kafka-network
    ipam:
      config:
        - subnet: 172.20.0.0/16
          gateway: 172.20.0.1
```

Para subir os 3 brokers de seu cluster kafka rodando localmente, rode este comando na pasta onde o arquivo `docker-compose.yml` estiver localizado:

```bash
docker-compose up -d
```

Para acessar seu cluster, utilize os IPs que foram definidos (ex: `172.20.0.101`).

### 4.2 Usuários Mac
Se você está usando Mac, o Docker não faz a ponte entre a rede que acabamos de criar e a sua máquina. Precisamos instalar uma ferramenta para nos ajudar:

```bash
# Instale usando Homebrew
brew install chipmk/tap/docker-mac-net-connect

# Inicie o serviço e o registre para rodar na inicialização
sudo brew services start chipmk/tap/docker-mac-net-connect
```

## 5. Dicas Adicionais

### 5.1 Ferramentas Úteis (kcat)
O `kcat` (antigo `kafkacat`) é uma excelente ferramenta de linha de comando para testar o cluster:

#### Windows (WSL) e Linux
```bash
sudo apt install kcat
```

#### Mac
```bash
brew install kcat
```

# Listar metadados do cluster
```bash
kcat -L -b kafka-broker-1:9092
```
