import org.apache.kafka.clients.consumer.ConsumerConfig
import org.apache.kafka.common.serialization.Serdes
import org.apache.kafka.streams.kstream.{KStream, Produced, TimeWindows}
import org.apache.kafka.streams.{KafkaStreams, KeyValue, StreamsBuilder, StreamsConfig}

import java.time.{Duration, Instant, ZoneId}
import java.time.format.DateTimeFormatter
import java.util.Properties

object MessageCounter {

  def main(args: Array[String]): Unit = {

    // Definindo configurações do Kafka Streams
    val props: Properties = new Properties()
    props.put(StreamsConfig.APPLICATION_ID_CONFIG, "message-count-app")
    props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "172.20.0.101:9092,172.20.0.102:9092,172.20.0.103:9092")
    props.put(ConsumerConfig.GROUP_ID_CONFIG, "message-count-group")
    props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass.getName)
    props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass.getName)

    // Configuração de Kafka Streams
    val builder = new StreamsBuilder()

    // Lendo o tópico de entrada
    val inputStream: KStream[String, String] = builder.stream("random-numbers")

    // Contando mensagens em janelas de 30 segundos
    val messageCounts = inputStream
      .groupByKey()  // Agrupa por chave (a chave pode ser qualquer valor, aqui usamos o "key" da mensagem)
      .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofSeconds(10))) // Janela de 10 segundos
      .count()  // Conta o número de mensagens em cada janela

    val formatter: DateTimeFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
      .withZone(ZoneId.systemDefault())


    // Convert both key (window start) and value (count) to String.
    val outputStream: KStream[String, String] = messageCounts.toStream.map { (windowedKey, count) =>
      val key = windowedKey.key()
      val windowTime = formatter.format(Instant.ofEpochMilli(windowedKey.window().start()))
      KeyValue.pair(key, s"{\"window\": $windowTime, \"key\": \"$key\", \"count\": $count}")
    }

    // Enviando o resultado para um tópico de saída
    outputStream.to("random-numbers-count", Produced.`with`(Serdes.String(), Serdes.String()))

    outputStream.peek { (_, value) =>
      println(value)
    }

    // Iniciando o Kafka Streams
    println("Initiating Kafka Streams")
    val streams: KafkaStreams = new KafkaStreams(builder.build(), props)
    streams.start()

    sys.ShutdownHookThread {
      streams.close()
    }
  }
}
