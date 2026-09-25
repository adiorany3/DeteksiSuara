# Ternak Siaga

Prototype Streamlit peringatan dini untuk sapi. Antarmuka Indonesia, tiga sinyal, daftar prioritas per ekor, ekspor CSV. Bukan diagnosis atau perangkat medis tervalidasi.

## Jalankan

```bash
cd /Users/macbookpro/Desktop/Prototype
python3 -m venv /Users/macbookpro/Desktop/Prototype/.venv
/Users/macbookpro/Desktop/Prototype/.venv/bin/python -m pip install -r /Users/macbookpro/Desktop/Prototype/requirements.txt
/Users/macbookpro/Desktop/Prototype/.venv/bin/python -m streamlit run /Users/macbookpro/Desktop/Prototype/app.py --server.address 127.0.0.1
```

Buka http://localhost:8501. Uji aturan:

```bash
/Users/macbookpro/Desktop/Prototype/.venv/bin/python /Users/macbookpro/Desktop/Prototype/risk.py
```

## Batas prototype

- Enam ternak awal adalah simulasi, bukan sensor langsung.
- Audio/citra hanya bukti yang ditinjau manual; tidak ada model CNN, detektor batuk, atau integrasi perangkat. Hitungan batuk harus teratribusi ke ternak dan berdurasi 10 menit.
- Indeks 0–100 memakai aturan demonstrasi, bukan probabilitas. Semua sinyal diperlukan untuk skor. Gejala klinis atau suhu tinggi memicu prioritas meskipun data belum lengkap.
- Data hanya dalam sesi; ID sama mengganti observasi terakhir. Berkas tidak disimpan ke disk. Ekspor CSV sebelum menutup sesi. Tidak ada autentikasi; gunakan lokal dengan data demo, bukan layanan publik atau arsip kesehatan.
- Angka studi berasal dari brief dan belum diverifikasi. Klaim CNN 100% bukan klaim aplikasi. Ketidaksesuaian metadata DOI ditandai pada halaman metode.
- Sebelum penggunaan klinis: validasi dokter hewan, data sapi independen per kandang, kalibrasi suhu, evaluasi alarm palsu, dan tata kelola data diperlukan.
