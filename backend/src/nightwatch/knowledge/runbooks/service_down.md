# SOP: Target Service Down / OOM Killed

## Scope
Peringatan ini dipicu ketika target scrape Prometheus `sample-app:8000` tidak merespon (`up == 0`).

## Indikasi & Gejala
- Alert `ServiceDown` berstatus FIRING.
- Healthcheck endpoint `/health` mengembalikan error koneksi atau timeout.
- Kontainer berhenti berjalan (`Exit code 137` untuk OOM kill, atau `Exit code 1`).

## Langkah Investigasi
1. Cek status kontainer Docker: Jalankan `docker ps -a` untuk melihat status exit code.
2. Cek syslog / system dmesg: Cari indikasi `Out of memory: Kill process` oleh kernel Linux.
3. Periksa log terakhir sebelum kontainer mati di Loki.

## Rencana Mitigasi Resmi
1. Nyalakan kembali service (`docker start <container>`).
2. Jika terbukti OOM killed: Tambahkan alokasi memory limit kontainer di `docker-compose.yml` atau perbaiki memory leak di kode aplikasi.