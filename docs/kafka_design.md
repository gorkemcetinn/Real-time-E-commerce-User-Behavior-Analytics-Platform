# Kafka Tasarımı (Taslak)

## Topic'ler
- `ecommerce.events.raw` — ham event akışı
- `ecommerce.events.dlq` — (opsiyonel) bozuk/şema dışı eventler

## Partition / Replication
- Lokal: 3–6 partition, RF=1
- Prod düşüncesi: 6–12 partition, RF≥2

## Keying
- `key = user_id` (session bazlı korelasyon kolaylığı)
- Alternatif: `session_id`

## Retention
- Dev: 72 saat
- Prod: 7 gün

## Şema
- V1: JSON (hızlı başlamak için)
- V2: Avro + Schema Registry (geriye uyumluluk)
