# Yerel Çalıştırma (Taslak)

## Servisler (Docker Compose)
- Kafka / Redpanda
- Kafka UI (Kafdrop / Redpanda Console)
- PostgreSQL
- Superset
- Spark (master/worker veya standalone + spark-submit)

## Port Planı (öneri)
- Kafka Broker: 9092
- Kafka UI: 8080 (veya 8081)
- PostgreSQL: 5432
- Superset: 8088
- Spark Master UI: 8080
- Spark History Server: 18080

## Adımlar (ileride güncellenecek)
1) `.env` oluştur (.env.example’dan kopyala)
2) `docker-compose up -d` (infra/ altında)
3) UI’lara bağlan ve health-check yap
