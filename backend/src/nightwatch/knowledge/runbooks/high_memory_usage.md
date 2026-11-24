# SOP: High Memory Usage / Memory Leak Incident

## Scope
Peringatan ini dipicu ketika penggunaan RAM kontainer (`sample-app` / `api-server`) melebihi threshold 90%.

## Indikasi & Gejala
- Alert `HighMemoryUsage` berstatus FIRING.
- Metrik `sample_app_memory_usage_percent` konsisten naik tanpa penurunan setelah siklus garbage collection.
- Potensi error di log: `OutOfMemoryError`, `heap space exhausted`, atau `BufferPoolFull`.

## Langkah Investigasi
1. Periksa metrik Prometheus: Cek kemiringan grafik memori (rate of increase).
2. Periksa Loki: Cari log dengan pola `OutOfMemory`, `memory leak`, atau error unhandled exceptions.
3. Periksa riwayat deploy: Cek apakah ada deployment baru dalam kurun waktu 2 jam terakhir sebelum alert firing.

## Rencana Mitigasi Resmi
1. **Mitigasi Segera (P1/P2)**:
   - Jika memori mencapai >92% dan terus naik, usulkan **restart service** (`docker restart <container>`) untuk mereclaim memori dan mencegah crash (OOM Kill).
2. **Mitigasi Jika Ada Deploy Baru**:
   - Jika insiden berkorelasi kuat dengan deployment/commit terbaru yang menambahkan buffer atau dependensi, lakukan **rollback** ke rilis sebelumnya.
3. **Penyelidikan Jangka Panjang**:
   - Profiling heap dump aplikasi untuk menemukan leaky object reference.
   - Pasang circuit breaker atau bounded queue pada buffer request.