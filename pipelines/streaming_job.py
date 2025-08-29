"""
Spark Structured Streaming - Smoke Test

Amaç:
- Kafka'dan JSON event'leri okumak
- Şemaya göre parse etmek
- Basit bir metrik: son 1 dakikada event_type sayısı
- Şimdilik konsola yaz (Postgres'e yazma bir sonraki adım)

Çalıştırma (container içinde spark-submit ile):
  docker exec -it spark spark-submit \
    --master spark://spark:7077 \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
    --conf spark.sql.shuffle.partitions=2 \
    /opt/pipelines/streaming_job.py
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, window
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, LongType, TimestampType, MapType
)

# Spark Session

spark = ( 
    SparkSession.builder
    .appName("rt-ecom-stream-smoke")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

# Kafkadan veriyi oku.

kafka_brokers = "kafka:9092"
topic = "ecommerce.events.raw"

raw = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", kafka_brokers)
    .option("subscribe", topic)
    .option("startingOffsets", "latest")
    .option("failOnDataLoss", "false")
    .load()
)

# value'yi stringe çevir ve JSON parse et

json_str = raw.select(col("value").cast("string").alias("value_str"))


# JSON şeması


event_schema = StructType([
    StructField("event_id", StringType(), False),
    StructField("ts", StringType(), False),        
    StructField("user_id", StringType(), False),
    StructField("session_id", StringType(), False),
    StructField("app_version", StringType(), True),
    StructField("device_os", StringType(), True),
    StructField("traffic_source", StringType(), True),
    StructField("event_type", StringType(), False),

    # page_view
    StructField("page_type", StringType(), True),
    StructField("page_id", StringType(), True),
    StructField("referrer", StringType(), True),
    StructField("engagement_ms", DoubleType(), True),

    # cart/favorite
    StructField("product_id", StringType(), True),
    StructField("category_id", StringType(), True),
    StructField("price", DoubleType(), True),

    # search_query
    StructField("query", StringType(), True),
    StructField("filters", MapType(StringType(), StringType(), True), True),
    StructField("results_count", LongType(), True),
])


parsed = json_str.select(from_json(col("value_str"), event_schema).alias("e")).select("e.*")

# 5) Zaman alanını Timestamp'e çevir + watermark
# ts ISO8601 geldiği için to_timestamp kullanabiliriz ama timezone + mikro saniye farkları
# olabildiğinden Spark bazen None döndürebilir. Basitlik için burada window'u event_time
# yerine işlem zamanı (processing time) ile yapacağız. Bir sonraki adımda event-time'a geçeriz.
#
# NOT: Eğer event-time yapmak istersen:
#   from pyspark.sql.functions import to_timestamp
#   parsed_ts = parsed.withColumn("event_time", to_timestamp("ts"))
#   sonra withWatermark("event_time", "10 minutes") kullan.
#


# 3) ts → event_time (TimestampType) + watermark
parsed_ts = (
    parsed
    .withColumn("event_time", to_timestamp(col("ts")))  # ISO8601 → TimestampType
    .withWatermark("event_time", "10 minutes")          # 10 dk gecikmeye tolerans
)

counts = (
    parsed_ts
    .groupBy(
        window(col("event_time"), "1 minute"),
        col("event_type")
    )
    .count()
)

# 6) Konsola yaz (geliştirme için)
query = (
    counts.writeStream
         .outputMode("update")          # veya "complete"; prod’da "append" tercih edilir
         .format("console")
         .option("truncate", "false")
         .trigger(processingTime="10 seconds")
         .start())

query.awaitTermination()
