# Exemplos de uso do Kafkacat (kcat)

O `kafkacat` (agora chamado de `kcat`) é uma ferramenta de linha de comando versátil para interagir com o Kafka, permitindo produzir e consumir mensagens, além de verificar metadados.

## 1. Listando Metadados (List Mode)

O modo `-L` exibe informações sobre o cluster, brokers, tópicos e partições.

```bash
kcat -b 172.20.0.101:9092,172.20.0.102:9092 -L
```

## 2. Produzindo Mensagens (Producer Mode)

O modo `-P` permite enviar mensagens para um tópico.

### Produção Simples (Interativa)
```bash
kcat -b 172.20.0.101:9092,172.20.0.102:9092 -P -t meu-topico
# Digite a mensagem e pressione Enter. Use Ctrl+D para sair.
```

### Produção com Chave (Key:Value)
Use `-K` para definir o delimitador entre chave e valor.
```bash
kcat -b 172.20.0.101:9092,172.20.0.102:9092 -P -t meu-topico -K:
# Exemplo de input:
# ID123:Dados do usuario
```

### Produção a partir de Pipe (echo)
```bash
echo "Minha mensagem" | kcat -b 172.20.0.101:9092,172.20.0.102:9092 -P -t meu-topico
```

### Produção em Loop (Simulando Fluxo)
Útil para testar consumidores em tempo real com um fluxo constante de dados.

**Loop com limite (100 mensagens):**
```bash
for i in $(seq 100); do echo "Mensagem $i: $RANDOM"; sleep 1; done | kcat -b 172.20.0.101:9092,172.20.0.102:9092 -P -t meu-topico
```

**Loop Infinito (Ctrl+C para parar):**
```bash
while true; do 
  echo "Data: $(date +%H:%M:%S) - Valor: $RANDOM" | kcat -b 172.20.0.101:9092,172.20.0.102:9092 -P -t meu-topico
  sleep 1
done
```

### Produção a partir de arquivo
```bash
cat mensagens.txt | kcat -b 172.20.0.101:9092,172.20.0.102:9092 -P -t meu-topico
```

## 3. Consumindo Mensagens (Consumer Mode)

O modo `-C` permite ler mensagens de um tópico.

### Consumo Padrão (Tail)
Lê mensagens novas chegando no tópico.
```bash
kcat -b 172.20.0.101:9092,172.20.0.102:9092 -C -t meu-topico
```

### Ler desde o início
```bash
kcat -b 172.20.0.101:9092,172.20.0.102:9092 -C -t meu-topico -o beginning
```

### Ler últimas N mensagens
Para ler as últimas 5 mensagens:
```bash
kcat -b 172.20.0.101:9092,172.20.0.102:9092 -C -t meu-topico -o -5
```

### Consumir N mensagens e sair
Use `-c` (count) para limitar o número de mensagens lidas.
```bash
kcat -b 172.20.0.101:9092,172.20.0.102:9092 -C -t meu-topico -c 10
```

### Formatação de Saída (JSON)
Exibe metadados, chave e valor em formato JSON. Útil para debug.
```bash
kcat -b 172.20.0.101:9092,172.20.0.102:9092 -C -t meu-topico -J
```

### Formatação Personalizada
Exibe apenas o offset e a mensagem.
```bash
kcat -b 172.20.0.101:9092,172.20.0.102:9092 -C -t meu-topico -f '"%T Topic: %t, Partition: %p, Offset: %o, Key: %k, Payload: %s\n'
```

### Consumir como um Grupo de Consumidores
Use `-G` para atuar como parte de um Consumer Group.
```bash
kcat -b 172.20.0.101:9092,172.20.0.102:9092 -f "%T Topic: %t, Partition: %p, Offset: %o, Key: %k, Payload: %s\n" -G meu-grupo-1 meu-topico
```