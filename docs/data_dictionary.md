# Data Dictionary (Taslak)

## Ortak Alanlar
- `event_id` (string, zorunlu)
- `event_type` (enum: cart_add, favorite_add, page_view, search_query)
- `ts` (ISO8601, zorunlu)
- `user_id` (string, zorunlu)
- `session_id` (string, zorunlu)
- `app_version` (string, ops)
- `device_os` (string, ops)
- `traffic_source` (string, ops)

## cart_add / favorite_add
- `product_id` (string, zorunlu)
- `category_id` (string, ops)
- `price` (number, ops)

## page_view
- `page_type` (enum: product|category|home|search, zorunlu)
- `page_id` (string, ops)
- `referrer` (string, ops)
- `engagement_ms` (number, ops)

## search_query
- `query` (string, zorunlu)
- `filters` (json, ops)
- `results_count` (int, ops)
