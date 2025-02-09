## Projeto de Disciplina \- Infraestrutura Kafka O Projeto de Disciplina será dividido em **duas partes**:

* **Parte teórica**: Você deverá fazer design de um sistema de detecção de fraude em tempo real, conforme os requisitos abaixo. Nessa parte, você irá definir a arquitetura do sistema, identificar tecnologias apropriadas e especificar os fluxos de dados, incluindo a integração com o Kafka e a utilização de Machine Learning.  
* **Parte prática:** Você deverá implementar a parte de detecção de fraude processando as mensagens do Kafka. O objetivo aqui é focar na lógica de processamento e detecção de comportamentos suspeitos, utilizando os dados das transações. Ao invés de usarmos Machine Learning, vamos definir algumas regras.

## Parte Teórica

### **Design de Sistema: Detecção de Fraude em Tempo Real para Transações com Cartão de Crédito**

**Objetivo:**  
Seu objetivo é projetar um **Sistema de Detecção de Fraude** que analisa transações de cartão de crédito **em tempo real** e identifica atividades suspeitas. O sistema deve fornecer uma **resposta imediata** se a transação envolver um cartão, usuário ou site previamente identificado como fraudulento, ou se for identificada com base em um conjunto de regras de negócio específicas.

Para transações que não possuem histórico de fraude, o sistema utilizará **Machine Learning** para identificar comportamentos suspeitos. Esses dados serão usados para alimentar a lista de bloqueio usada pelo módulo de resposta imediata, ajudando a prevenir futuras transações fraudulentas.

As transações são originadas nas maquininhas de pagamento, distribuídas pelos estabelecimentos comerciais ou via API, em caso de pagamento online.

As regras de negócio devem ser cadastradas e armazenadas, não sendo hardcoded, para garantir que possam ser facilmente acessadas e atualizadas.

**Dados:**

* Uma transação é composta pelos campos: timestamp, transaction\_id, user\_id, card\_id, site\_id, value, location\_id, country  
* Você terá acesso aos dados do usuário e dados de referência. Precisará determinar como armazená-los e para que usá-los:  
  * Usuário: user\_id, nome, endereço, email  
  * Estabelecimento: site\_id, nome, endereço, categoria de produtos (bens de consumo, viagens, restaurantes etc.)

**Requisitos não funcionais:**

* **Escalabilidade**: O sistema deve suportar até **10 mil transações por segundo (TPS)**.  
* **Disponibilidade**: **99,9% de uptime**.  
* **Latência:**  
  * Resposta imediata:  
    * P50: **1 segundo**  
    * P90: **5 segundos**  
  * **Identificação de comportamentos suspeitos**:  
    * P50: **10 minutos**  
    * P90: **30 minutos**  
* **Armazenamento**:  
  * Todas as transações devem ser armazenadas por **180 dias**.  
  * Transações **suspeitas** também devem ser armazenadas.

**O que você deve entregar:**

* **Diagrama de Arquitetura**: Apresente a arquitetura do sistema, mostrando os diversos módulos e como eles interagem.  
* **Casos de Uso**: Detalhe os casos de uso, explicando os fluxos de dados, como transações verdadeiras, fraudulentas, e falsos positivos.  
* **Tecnologias**: Identifique as tecnologias a serem usadas, explicando, por exemplo, a escolha do banco de dados (relacional, NoSQL, grafos, busca etc.).  
* **Machine Learning**: Identifique como e quando o modelo será treinado.  
* **Evitar SPOF**: Garanta que o sistema não tenha **pontos únicos de falha (SPOF)**.  
* **Monitoramento**: Identifique que métricas você utilizará para definir se o sistema está saudável

## Parte prática

#### **Objetivo:**

O objetivo deste exercício é desenvolver uma aplicação que processe dados de transações financeiras em tempo real a partir de um tópico Kafka e identifique transações fraudulentas com base em um conjunto de regras específicas. Não iremos implementar todo o sistema da parte teórica, mas apenas o módulo de detecção. Também não iremos fazer uso de Machine Learning. Iremos simplificar o problema criando algumas regras que levam em conta o contexto de cada usuário e podem ser caracterizadas por atividades suspeitas. 

### **Regras de Fraude**

Sua solução deverá identificar fraudes com base nas seguintes regras:

1. **Alta Frequência**: Um usuário realizou duas transações com valores diferentes em um intervalo inferior a 5 minutos entre elas.  
2. **Alto Valor**: Um usuário realizou uma transação que excede o dobro do maior valor que ele já gastou em transações anteriores.  
3. **Outro País**: Um usuário fez uma transação em um país diferente menos de 2 horas após ter feito uma transação em outro país.

### **Fornecimento de Dados**

Para facilitar o desenvolvimento, uma função Python será fornecida para gerar dados de transações. Algumas dessas transações serão fraudulentas.

* Essa função retornará um objeto da classe `Transaction`, cujo formato estará disponível para consulta.  
* Você precisará criar um **produtor Kafka** que execute essa função em looping, enviando as mensagens geradas para um tópico Kafka.

### **Tecnologias**

Você deverá desenvolver uma aplicação que consuma as mensagens do Kafka e identifique fraudes com base nas regras descritas acima.

* Você deve utilizar um **consumidor Kafka em Python** para processar os eventos.  
* Caso prefira explorar outras tecnologias além das abordadas no curso, você pode utilizar Kafka Streams, Flink ou Spark Streaming para implementar a detecção de fraude.  
* A aplicação deverá publicar os resultados em um **novo tópico Kafka**, contendo informações dos usuários com suspeitas de fraude, bem como o tipo de fraude e os parâmetros da fraude.  
* Os dados dos usuários suspeitos deverão também ser armazenados em um **banco de dados** de sua escolha.

**O que você deve entregar:**

1. O **código fonte** do **produtor** e do **consumidor Kafka**.  
2. Caso utilize alguma tecnologia além de Python (como Kafka Streams, Flink ou Spark Streaming), a entrega deve incluir um docker-compose que permita a execução da solução.  
3. Um **README** com informações sobre seu código e o banco de dados que você usou para extrair os dados.

