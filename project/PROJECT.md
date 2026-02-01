## Projeto de Disciplina \- Infraestrutura Kafka O Projeto de Disciplina será dividido em **duas partes**:

* **Parte teórica**: Você deverá fazer design de um sistema de detecção de fraude em tempo real, conforme os requisitos abaixo. Nessa parte, você irá definir a arquitetura do sistema, identificar tecnologias apropriadas e especificar os fluxos de dados, incluindo a integração com o Kafka e a utilização de Machine Learning.  
* **Parte prática:** Você deverá implementar uma pipeline de dados para o rastreamento de entregadores de um aplicativo de delivery em tempo real. O objetivo é configurar um cluster Kafka e uma pipeline de integração que garanta que o estado mais recente de cada entregador esteja disponível no Redis.

## Parte Teórica

#### **Objetivo:**

Seu objetivo é projetar um Sistema de Detecção de Fraude que analisa transações de cartão de crédito em tempo real e identifica atividades suspeitas. O sistema deve fornecer uma resposta imediata se a transação envolver um cartão, usuário ou site previamente identificado como fraudulento.

Para transações que não possuem histórico de fraude, o sistema utilizará um modelo de  **Machine Learning** para identificar comportamentos suspeitos. O modelo irá prever quais transações são suspeitas e esse resultado será usado para alimentar a lista de bloqueio usada pelo módulo de resposta imediata, ajudando a prevenir futuras transações fraudulentas.

As transações são originadas nas maquininhas de pagamento, distribuídas pelos estabelecimentos comerciais ou via API, em caso de pagamento online. Pense em casos de uso como transações verdadeiras, transações de um usuário marcado como fraudulento, transações suspeitas, confirmação ou cancelamento de que a transação é fraudulenta etc.

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
* **Machine Learning**: Detalhe a estratégia para coletar dados históricos e o fluxo de treinamento de modelos para detecção de transações  suspeitas. Você NÃO precisa especificar qual modelo de ML será usado..  
* **Evitar SPOF**: Garanta que o sistema não tenha **pontos únicos de falha (SPOF)**.  
* **Monitoramento**: Identifique que métricas você utilizará para definir se o sistema está saudável

## Parte prática

#### **Objetivo:**

Você deve implementar uma pipeline de dados para **rastreamento de entregadores de um aplicativo de delivery em tempo real**. O sistema precisa ser eficiente: o histórico completo de movimentação é irrelevante para o despacho imediato; o que importa para a operação é saber onde cada entregador está exatamente agora.

Sua tarefa é configurar um cluster Kafka e uma pipeline de integração que garanta que o estado mais recente de cada entregador esteja disponível de forma rápida e persistente em um banco de dados em memória (Redis).

#### **Requisitos Técnicos:**

##### **1\. Infraestrutura Kafka**

* Suba um cluster Kafka com 3 nós (brokers) para garantir tolerância a falhas.  
* O sistema deve ser configurado de forma que o Kafka não armazene o histórico infinito de posições, mas sim a última localização conhecida por entregador. Cabe a você configurar o tópico adequadamente para este comportamento de otimização de armazenamento.

##### **2\. Ingestão de Dados (Produtor)**

* Utilize o código Python fornecido que simula a geração de eventos de localização.  
* Você deverá desenvolver o produtor que envia essas mensagens para o Kafka, garantindo que a estrutura da mensagem permita a atualização correta do estado no destino.  
* Esquema da Mensagem**:** `driver_id`, `latitude`, `longitude`, `timestamp`, `status`.

##### **3\. Integração com Redis (Kafka Connect)**

* Configure o Kafka Connect (Sink Connector) para realizar o transporte automático dos dados do Kafka para o Redis.  
* O Redis deve atuar como um espelho do estado atual. Para cada `driver_id`, deve existir apenas um registro refletindo sua posição e status mais recentes.

##### **4\. Monitoramento (Prometheus & Grafana)**

* Implemente o monitoramento do ambiente usando Prometheus.  
* Forneça um Dashboard no Grafana com as métricas mais relevantes..

#### **O que você deve entregar:**

1. **Topologia do Ambiente:** Arquivo `docker-compose.yml` ou documentação dos comandos de instalação/arquivos de configuração (Cluster Kafka, Connect, Redis e Monitoramento).  
2. **Configuração de Tópicos:** Documente o comando de criação dos tópicos.  
3. **Configuração do Conector:** O arquivo JSON (ou comando `curl`) utilizado para instanciar o conector Redis Sink.  
4. **Evidência de Monitoramento:** Screenshots do dashboard do Grafana.  
5. **Validação de Estado:** Demonstração (via `redis-cli`) de que o banco contém informações atualizadas e sem duplicidade por entregador.  
6. **Vídeo Explicativo:** Explique a arquitetura montada e as decisões de configuração de tópico.  
   1. Explique como você garantiu a unicidade dos dados no Redis.  
   2. Demonstração de Resiliência: Durante a gravação, pare uma das instâncias (nós) do Kafka e exiba em tempo real o impacto disso no seu dashboard de monitoramento.