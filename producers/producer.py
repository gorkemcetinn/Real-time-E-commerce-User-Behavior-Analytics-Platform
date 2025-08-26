"""
Real-time E-commerce Event Producer (Simulator)

Amaç:
- Kullanıcı davranışlarını (page_view, search_query, cart_add, favorite_add) simüle etmek.
- Bu eventleri JSON formatında Kafka'ya göndermek.
"""


import os
import sys
import json
import time
import uuid
import random
import signal
import atexit
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple
from kafka import KafkaProducer



# ------------------------------------------------------
# Yardımcı Fonksiyonlar
# ------------------------------------------------------

def now_iso() -> str:
    """UTC zaman damgasını ISO formatında döndürür."""
    return datetime.now(timezone.utc).isoformat()

def rand_id(prefix: str) -> str:
    """prefix + random uuid'den kısa ID üretir."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def weighted_choice(items: List[Tuple[str, float]]) -> str:
    """Ağırlıklı rastgele seçim yapar."""
    vals, weights = zip(*items)
    return random.choices(vals, weights=weights, k=1)[0]


# ------------------------------------------------------



# ------------------------------------------------------
# Demo Veri Havuzları (ürünler, aramalar, cihazlar vs.)
# ------------------------------------------------------

POPULAR_PRODUCTS = [f"prod_{i:04d}" for i in range(1, 51)]
LONG_TAIL_PRODUCTS = [f"prod_{i:04d}" for i in range(51, 501)]

SEARCH_TERMS_POPULAR = ["iphone", "samsung", "airpods", "kulaklik", "laptop"]
SEARCH_TERMS_TAIL = ["usb hub", "ergonomik sandalye", "nvme kutu", "oyun mouse"]

TRAFFIC_SOURCES = [("direct", 0.4), ("seo", 0.4), ("ads", 0.2)]
DEVICE_OS = [("android", 0.45), ("ios", 0.35), ("web", 0.20)]
PAGE_TYPES = ["home", "category", "product", "search"]


# ------------------------------------------------------
# Event Üretici Fonksiyonlar
# ------------------------------------------------------

def make_base(user_id: str,session_id: str) -> Dict[str, Any]:
    """Tüm eventler için ortak alanları oluşturur."""
    event = {
        "event_id": uuid.uuid4().hex,
        "ts": now_iso(),
        "user_id": user_id,
        "session_id": session_id,
        "app_version": f"1.{random.randint(0,9)}.{random.randint(0,9)}",
        "device_os": weighted_choice(DEVICE_OS),
        "traffic_source": weighted_choice(TRAFFIC_SOURCES),
    }
    return event


def make_page_view(user_id: str, session_id: str) -> Dict[str, Any]:
    """page_view eventi oluşturur."""

    base = make_base(user_id, session_id)
    page_type = random.choices(PAGE_TYPES)
    event = {
        **base,
        "event_type": "page_view",
        "page_type": page_type,
        "page_id": rand_id("page"),
        "referrer": random.choice(["/home", "/campaign", "/search", None]),
    }
    return event

def pick_product() -> str:
    """Popüler ve uzun kuyruktan ürün seçer."""
    if random.random() < 0.7:
        return random.choice(POPULAR_PRODUCTS)
    else:
        return random.choice(LONG_TAIL_PRODUCTS)



def make_cart_add(user_id: str, session_id: str) -> Dict[str, Any]:
    """cart_add eventi oluşturur."""
    base = make_base(user_id, session_id)
    event = {
        **base,
        "event_type": "cart_add",
        "product_id": pick_product(),
        "quantity": f"cat_{random.randint(1,30):02d}",
        "price": round(random.uniform(5.0, 1500.0), 2),
    }
    return event


def make_favorite_add(user_id: str, session_id: str) -> Dict[str, Any]:
    """favorite_add eventi oluşturur."""
    base = make_base(user_id, session_id)
    event = {
        **base,
        "event_type": "favorite_add",
        "product_id": pick_product(),
        "category_id": f"cat_{random.randint(1,30):02d}",
        "price": round(random.uniform(5.0, 1500.0), 2)
    }
    return event


def make_search_query(user_id: str, session_id: str) -> Dict[str, Any]:
    """search_query eventi oluşturur."""
    base = make_base(user_id, session_id)
    term = random.choice(SEARCH_TERMS_POPULAR) if random.random() < 0.7 else random.choice(SEARCH_TERMS_TAIL)
    event = {
        **base,
        "event_type": "search_query",
        "search_term": term,
       "filters": {"min_price": random.choice([None, 0, 500])},
        "results_count": random.randint(0, 5000),
    }
    return event

# ------------------------------------------------------
# Bozuk Veri Enjeksiyonu (DLQ testleri için)
# ------------------------------------------------------

def inject_corruption(event: Dict[str, Any], rate: float) -> Dict[str, Any]:
    if random.random() >= rate:
        return event

    e = dict(event)
    choice = random.choice(["missing_product", "bad_price", "future_ts"])
    if choice == "missing_product" and "product_id" in e:
        e["product_id"] = None
    elif choice == "bad_price" and "price" in e:
        e["price"] = "not-a-number"
    elif choice == "future_ts":
        e["ts"] = datetime.now(timezone.utc).isoformat()
    return e



# ------------------------------------------------------
# Oturum Bazlı Event Üretimi
# ------------------------------------------------------
def session_events(user_id: str):
    """Tek bir kullanıcı oturumunda event zinciri üret."""
    session_id = rand_id("sess")

    # 3–10 page_view
    for _ in range(random.randint(3, 10)):
        yield make_page_view(user_id, session_id)

    # %70 oturumda 0–3 search_query
    if random.random() < 0.7:
        for _ in range(random.randint(0, 3)):
            yield make_search_query(user_id, session_id)

    # 0–2 cart_add, 0–1 favorite_add
    for _ in range(random.randint(0, 2)):
        yield make_cart_add(user_id, session_id)
    for _ in range(random.randint(0, 1)):
        yield make_favorite_add(user_id, session_id)


# ------------------------------------------------------
# Kafka Producer Ayarı
# ------------------------------------------------------


def make_producer(broker: str) -> KafkaProducer:
    """Kafka Producer oluşturur."""
    return KafkaProducer(
        bootstrap_servers= broker,
        acks="all",
        linger_ms=10,
        retries=5,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8")
        )

# ------------------------------------------------------
# Main Çalışma Döngüsü
# ------------------------------------------------------


def main():
    broker = os.getenv("KAFKA_BROKER", "localhost:29092")
    topic = os.getenv("KAFKA_TOPIC", "ecommerce.events.raw")
    eps = int(os.getenv("EPS", "100"))  # events per second
    corruption = float(os.getenv("CORRUPTION_RATE", "0.02"))  # bozuk veri oranı

    print(f"[producer] broker={broker} topic={topic} eps={eps} corruption={corruption}")
    
    producer = make_producer(broker)

    running = True
    def handle_sig(*_):
        nonlocal running
        running = False
        print("\n[producer] Stopping...")

    signal.signal(signal.SIGINT, handle_sig)
    signal.signal(signal.SIGTERM, handle_sig)
    atexit.register(lambda: producer.flush(timeout=5))

    try:
        users = [f"user_{i:05d}" for i in range(1, 2001)]
        while running:
            u = random.choice(users)
            for ev in session_events(u):
                ev = inject_corruption(ev, corruption)
                producer.send(topic, value=ev, key=ev["user_id"])
            producer.flush(timeout=5)
            time.sleep(1)
    finally:
        producer.close()
        print("[producer] Closed.")


if __name__ == "__main__":
    main()



