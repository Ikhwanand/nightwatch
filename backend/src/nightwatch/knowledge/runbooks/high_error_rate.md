# SOP: High HTTP 5xx Error Rate Incident

## Scope
Peringatan ini dipicu ketika persentase respon HTTP 5xx pada endpoint melebihi 10% dari total request.

## Indikasi & Gejala
- Alert `HighErrorRate` berstatus FIRING.
- Peningkatan tajam pada `sample_app_requests_total{status=~"5.."}`.
- Pengguna mengalami error 500 Internal Server Error atau 502/504 Bad Gateway.

## Langkah Investigasi
1. Query Loki log: Cari pesan error spesifik seperti `ConnectionRefusedError`, `Database connection timed out`, atau `NullPointerException`.
2. Query Prometheus: Bandingkan request rate total dengan error rate untuk mengetahui skala dampaknya.
3. Periksa ketergantungan (dependencies): Pastikan database PostgreSQL, Redis cache, atau upstream microservice aktif dan sehat.

## Rencana Mitigasi Resmi
1. Jika akibat koneksi database jenuh: Scale pool connection atau restart database connection pool.
2. Jika akibat upstream dependency mati: Aktifkan fallback response atau caching layer.
3. Jika akibat bad commit: Lakukan rollback deployment.