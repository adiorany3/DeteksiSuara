# Sample Ternak Siaga — seluruhnya sintetis

1. Buka Pemeriksaan ternak di http://localhost:8501.
2. Isi ID SAMPLE-001 dan Kandang Demo.
3. Unggah audio_sintetis_10_menit.wav dan citra_sintetis.png pada input masing-masing.
4. Untuk simulasi saja, aktifkan ketiga checkbox ketersediaan observasi. Isi 12 batuk, pilih Luka mulut dan Air liur berlebih, isi suhu 40,3 °C.
5. Klik Hitung & simpan pemeriksaan. Harapan: 82/100, Prioritas tinggi.

Audio berisi 12 nada pendek selama 10 menit, BUKAN suara batuk. PNG berupa kartu bertanda SIMULASI, BUKAN citra lesi. Nilai skenario tidak diturunkan dari berkas; jangan gunakan sebagai data pelatihan atau validasi klinis. Checkbox sumber terkonfirmasi hanya diaktifkan dalam simulasi alur ini, bukan pengakuan bahwa nada merupakan batuk.

observasi_demo.csv menyediakan lima skenario beserta hasil harapan. CSV belum dapat diimpor ke aplikasi; salin nilai secara manual. Nilai kosong berarti sinyal tidak tersedia: jangan aktifkan checkbox sinyal tersebut. jumlah_gejala adalah jumlah pilihan gejala; untuk satu gejala pilih Luka mulut. Nol berarti sudah ditinjau dan tidak ada gejala, bukan belum ditinjau.

SAMPLE-005 memperlihatkan override: skor 15 tetap Prioritas tinggi karena ada gejala klinis. Sampel tidak merepresentasikan diagnosis.

Buat ulang dan periksa sample:

```bash
/Users/macbookpro/Desktop/Prototype/.venv/bin/python /Users/macbookpro/Desktop/Prototype/samples/generate.py
```

## Sample lapangan versi baru

Di halaman Pemeriksaan ternak, pilih skenario lalu klik **Muat sample ke formulir**. Nilai diisi otomatis; klik Hitung & simpan untuk melihat hasil. Data simulasi ditandai pada laporan. Jangan mengubah label menjadi observasi nyata.

Enam skenario mencakup demam dengan lesi, batuk tanpa lesi, observasi rendah, suara komunal ambigu, lesi kuku tanpa demam, serta demam dengan pemeriksaan belum lengkap. Konteks, kualitas data, dan tindak lanjut disertakan. Semua kasus fiktif; bukan catatan pasien dan bukan hasil validasi dokter hewan.

Paket ZIP terbaru berisi scenarios.json, skenario_lapangan.csv, audio_latar_sintetis.wav, ilustrasi_observasi.png, dan panduan ini. CSV untuk inspeksi manual; pemuat formulir memakai skenario JSON bawaan, bukan impor CSV.

Audio terbaru: 30 detik noise buatan dengan enam impuls, bukan rekaman batuk sapi. Jangan mengekstrapolasi hitungan audio ini menjadi batuk per 10 menit. Gambar terbaru merupakan diagram area inspeksi, bukan foto penyakit. Berkas versi awal yang dijelaskan di atas tetap tersedia di folder, tidak termasuk ZIP terbaru.

Bangun dan uji paket terbaru:

```bash
/Users/macbookpro/Desktop/Prototype/.venv/bin/python /Users/macbookpro/Desktop/Prototype/samples/realistic.py
```

Untuk sample klinis autentik, diperlukan rekaman/foto lapangan dengan izin penggunaan, identitas ternak tersamarkan, anotasi petugas, durasi rekaman dan metode suhu yang jelas. Tidak ada media autentik yang direkayasa atau diklaim dalam paket ini.

