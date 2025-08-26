# Real-time E-commerce User Behavior Analytics Platform

Gerçek zamanlı e-ticaret etkileşimlerini (page_view, cart_add, favorite_add, search_query) **Kafka → Spark Structured Streaming → PostgreSQL → Superset** hattında toplayıp analiz eden uçtan uca bir veri boru hattı.

## Amaç
- Gerçek zamanlı akıştan metrik üretmek (Top Cart/Favorite Products, Trending Search Terms, Page Dwell Time)
- Ölçeklenebilir ve gözlemlenebilir bir streaming mimarisi kurmak
- BI/dashboards üzerinden karar vericiye anlık içgörü sağlamak

## Mimari (yüksek seviye)
Producer → **Kafka** (topic: `ecommerce.events.raw`) → **Spark Structured Streaming** (window + watermark + state) → **PostgreSQL** (sonuç tabloları) → **Superset** (dashboard)

## Teknoloji Yığını
- **Akış**: Apache Kafka (veya Redpanda)
- **İşleme**: Apache Spark (Structured Streaming, PySpark)
- **Depolama**: PostgreSQL (+ opsiyonel MongoDB ham arşiv)
- **Görselleştirme**: Apache Superset
- **Orkestrasyon (ileri aşama)**: Airflow / Prefect
- **Konteyner**: Docker Compose

## Dizin Yapısı
- docs/
- infra/
- producers/
- pipelines/
- storage/
- monitoring/


Ayrıntı:
- `docs/` — mimari diyagramlar, veri sözlüğü, çalışma talimatları
- `infra/` — docker-compose, .env şablonları, port/servis planı
- `producers/` — event simülatörü (oturum & davranış modeli)
- `pipelines/` — Spark streaming job(lar)ı
- `storage/` — PostgreSQL DDL, indeks planı, saklama politikası
- `monitoring/` — Kafka/Spark/DB metrikleri ve uyarı planı

## Başlangıç (Sprint 1 hedefleri)
1. Repo iskeleti (bu dosya ve klasörler) ✅  
2. Yüksek seviye mimari diyagram (docs/architecture.*)  
3. Event sözlüğü (docs/data_dictionary.md)  
4. Kafka topic tasarımı (docs/kafka_design.md)  
5. Yerel altyapı bileşen listesi (docs/run_local.md)  
6. `.env.example` & başlatma adımları (infra/)

> Sprint görevlerinin tamamı `docs/` altındaki sprint md dosyalarında.

## Lisans
TBD


