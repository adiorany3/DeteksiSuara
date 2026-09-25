import csv
import io
import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from risk import assess

st.set_page_config(page_title="Ternak Siaga • Peringatan Dini", page_icon="🐄", layout="wide")
st.markdown("""<style>
.stApp {background:#f4f7f6;color:#173d38}
.block-container {padding-top:2.2rem;max-width:1440px;padding-bottom:4rem}
[data-testid="stSidebar"] {background:#e6efeb;border-right:1px solid #ccdcd5}
h1,h2,h3 {color:#173d38;letter-spacing:-.025em}
h1 {font-size:2.6rem!important;max-width:900px}
div[data-testid="stMetric"] {background:#fff;padding:22px;border:1px solid #d9e4df;
border-top:3px solid #258675;border-radius:14px;box-shadow:0 4px 16px #163d3806}
[data-testid="stMetricLabel"] {color:#47645b}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius:14px}
.stButton>button[kind="primary"] {background:#176a59;border-color:#176a59;min-height:44px}
button:focus-visible,a:focus-visible {outline:3px solid #bb7400!important;outline-offset:3px}
.hero {background:#173d38;color:#f5faf7;border-radius:18px;padding:26px 30px;margin:18px 0 24px}
.hero small {color:#bee0d3;letter-spacing:.13em;font-weight:600}
.hero p {margin:8px 0 0;max-width:780px;line-height:1.7}
@media(max-width:700px) {h1 {font-size:2rem!important}.hero {padding:20px}.block-container {padding-top:1.2rem}}
</style>""", unsafe_allow_html=True)

DEMO = [
    {"id": "SBW-001", "pen": "Kandang A", "coughs": 12, "signs": 2, "temperature": 40.3},
    {"id": "SBW-002", "pen": "Kandang A", "coughs": 6, "signs": 0, "temperature": 39.6},
    {"id": "SBW-003", "pen": "Kandang B", "coughs": 0, "signs": 0, "temperature": 38.6},
    {"id": "SBW-004", "pen": "Kandang B", "coughs": None, "signs": 0, "temperature": 38.8},
    {"id": "SBW-005", "pen": "Kandang C", "coughs": 2, "signs": 0, "temperature": 38.9},
    {"id": "SBW-006", "pen": "Kandang C", "coughs": 1, "signs": 1, "temperature": 39.2},
]
SAMPLE_DIR = Path(__file__).resolve().parent / "samples"
SCENARIOS = json.loads((SAMPLE_DIR / "scenarios.json").read_text(encoding="utf-8"))


def load_scenario():
    case = SCENARIOS[st.session_state.scenario_index]
    st.session_state.update(animal=case["id"], pen=case["pen"],
                            cough_known=case["coughs"] is not None, coughs=case["coughs"] or 0,
                            signs_known=case["signs"] is not None, signs=case["signs"] or [],
                            temp_known=case["temperature"] is not None, temperature=case["temperature"] or 38.5,
                            simulated=True)
    st.session_state.pop("last_result", None)


if "records" not in st.session_state:
    st.session_state.records = [dict(row, source="Simulasi", time="Demo — bukan pembacaan langsung") for row in DEMO]

with st.sidebar:
    st.title("Ternak Siaga")
    st.caption("SISTEM PERINGATAN DINI")
    st.divider()
    page = st.radio("Navigasi", ["Ringkasan", "Pemeriksaan ternak", "Metode & referensi"])
    st.divider()
    st.markdown("**Kabupaten Sumbawa**\n\nPrototype • ternak sapi")
    st.caption("Tidak terhubung mikrofon, kamera, atau sensor. Data tersimpan hanya selama sesi browser.")
    sample_zip = Path(__file__).resolve().parent / "samples" / "sample_ternak_siaga.zip"
    if sample_zip.is_file():
        st.download_button("Unduh sample demo (ZIP)", sample_zip.read_bytes(), sample_zip.name, "application/zip")
        st.caption("Enam skenario lapangan, CSV, audio sintetis, ilustrasi inspeksi, panduan. Bukan bukti klinis.")

st.caption("KESEHATAN TERNAK / PEMANTAUAN MULTIMODAL")
st.title({"Ringkasan": "Kenali sinyal lebih awal.", "Pemeriksaan ternak": "Pemeriksaan tiga sinyal", "Metode & referensi": "Transparansi sebelum prediksi"}[page])
st.write("Suara batuk, citra klinis, dan suhu tubuh — satu pandangan untuk menentukan prioritas pemeriksaan.")
st.warning("Prototype penelitian. Skor risiko bukan diagnosis PMK/BRDC, bukan probabilitas penyakit, dan tidak menggantikan dokter hewan.")


def table_rows(records):
    rows = []
    for row in records:
        result = assess(row["coughs"], row["signs"], row["temperature"])
        rows.append({"ID ternak": row["id"], "Kandang": row["pen"], "Status": result["label"],
                     "Skor /100": result["score"], "Batuk /10 menit": row["coughs"],
                     "Gejala /3": row["signs"], "Suhu °C": row["temperature"],
                     "Sumber": row["source"], "Waktu": row["time"]})
    return rows


if page == "Ringkasan":
    rows = table_rows(st.session_state.records)
    cols = st.columns(4)
    for col, label, value in zip(cols, ["Ternak terpantau", "Prioritas tinggi", "Perlu dipantau", "Data belum lengkap"],
                                 [len(rows), sum(r["Status"] == "Prioritas tinggi" for r in rows),
                                  sum(r["Status"] == "Perlu dipantau" for r in rows),
                                  sum(r["Skor /100"] is None for r in rows)]):
        col.metric(label, value)
    st.markdown('<section class="hero"><small>PANTAU · TINJAU · TINDAK LANJUT</small><p>Mulai dari ternak berprioritas tinggi. Periksa kualitas setiap sinyal sebelum mengambil keputusan bersama petugas kesehatan hewan.</p></section>', unsafe_allow_html=True)
    overview, details = st.columns([1, 2])
    with overview, st.container(border=True):
        st.markdown("**Kelengkapan observasi**")
        complete = sum(r["Skor /100"] is not None for r in rows)
        st.progress(complete / len(rows), text=f"{complete} dari {len(rows)} ternak memiliki tiga sinyal")
        st.caption("Data hilang bukan sinyal negatif. Prioritas klinis dapat muncul sebelum skor lengkap.")
    with details, st.container(border=True):
        st.markdown("**Antrian tindak lanjut**")
        urgent = [r for r in rows if r["Status"] == "Prioritas tinggi"]
        if urgent:
            st.write(" · ".join(r["ID ternak"] for r in urgent))
            st.caption("Perlu penilaian petugas. Urutan bukan estimasi tingkat keparahan penyakit.")
        else:
            st.write("Belum ada prioritas tinggi berdasarkan observasi tersimpan.")
    st.subheader("Daftar prioritas ternak")
    left, right = st.columns([2, 1])
    query = left.text_input("Cari ID ternak", placeholder="Contoh: SBW-001")
    pen = right.selectbox("Kandang", ["Semua"] + sorted({r["Kandang"] for r in rows}))
    priority = {"Prioritas tinggi": 0, "Data belum lengkap": 1, "Perlu dipantau": 2, "Sinyal rendah": 3}
    filtered = sorted([r for r in rows if query.lower() in r["ID ternak"].lower() and
                       (pen == "Semua" or r["Kandang"] == pen)], key=lambda r: priority[r["Status"]])
    st.dataframe(filtered, hide_index=True, width="stretch", column_config={
        "Skor /100": st.column_config.ProgressColumn("Indeks risiko", min_value=0, max_value=100, format="%d"),
        "Suhu °C": st.column_config.NumberColumn("Suhu °C", format="%.1f"),
    })
    st.caption("Skor kosong = sinyal belum lengkap. Sinyal rendah tidak menyingkirkan penyakit. Semua data awal adalah simulasi.")
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0]))
    writer.writeheader()
    # Prevent spreadsheet formulas from user-entered identifiers.
    writer.writerows({k: "'" + v if isinstance(v, str) and v.lstrip().startswith(("=", "+", "-", "@")) else v
                     for k, v in row.items()} for row in filtered)
    st.download_button("Unduh laporan CSV", output.getvalue().encode("utf-8-sig"), "ternak-siaga.csv", "text/csv")
    st.subheader("Tiga sinyal, satu tindak lanjut")
    for col, title, text in zip(st.columns(3), ["01 / Suara batuk", "02 / Citra klinis", "03 / Suhu tubuh"],
                               ["Jumlah batuk terverifikasi per 10 menit. Suara kandang tidak otomatis teratribusi ke satu ternak.",
                                "Tinjau luka mulut, air liur berlebih, dan lesi kuku. Unggahan tidak diklasifikasikan otomatis.",
                                "Input suhu tubuh oleh petugas. Suhu permukaan tidak boleh disamakan langsung dengan suhu inti."]):
        with col, st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(text)

elif page == "Pemeriksaan ternak":
    st.info("Audio/citra hanya bukti. Observasi diisi petugas; belum ada model AI atau koneksi sensor.")
    with st.expander("Sample lapangan — pilih dan muat skenario", expanded=True):
        index = st.selectbox("Skenario sintetis", range(len(SCENARIOS)),
                             format_func=lambda i: SCENARIOS[i]["title"], key="scenario_index")
        case = SCENARIOS[index]
        st.write(case["context"])
        st.caption("Kualitas data: " + case["quality"])
        st.write("Tindak lanjut: " + case["action"])
        st.button("Muat sample ke formulir", on_click=load_scenario)
        st.caption("Nilai fiktif menyerupai situasi lapangan, bukan data pasien atau ambang klinis tervalidasi.")
        media1, media2 = st.columns(2)
        with media1:
            if (SAMPLE_DIR / "audio_latar_sintetis.wav").is_file():
                st.audio(str(SAMPLE_DIR / "audio_latar_sintetis.wav"))
                st.caption("30 detik suara buatan: latar bising + impuls mirip batuk. Bukan rekaman sapi, bukan sumber hitungan 10 menit.")
        with media2:
            if (SAMPLE_DIR / "ilustrasi_observasi.png").is_file():
                st.image(str(SAMPLE_DIR / "ilustrasi_observasi.png"), caption="Ilustrasi area inspeksi; bukan foto klinis.", width="stretch")
    st.session_state.setdefault("simulated", True)
    st.checkbox("Data simulasi (jangan dicatat sebagai observasi nyata)", key="simulated")
    a, b = st.columns(2)
    animal = a.text_input("ID ternak", max_chars=40, placeholder="SBW-007", key="animal")
    pen = b.text_input("Nama kandang", max_chars=60, placeholder="Kandang A", key="pen")
    c1, c2, c3 = st.columns(3)
    with c1, st.container(border=True):
        st.subheader("01 / Batuk")
        audio = st.file_uploader("Rekaman 10 menit (opsional)", type=["wav", "mp3", "ogg"])
        if audio:
            if audio.size > 20 * 1024 * 1024:
                st.error("Batas audio 20 MB.")
            else:
                st.audio(audio)
        cough_known = st.checkbox("Batuk dihitung, sumber ternak terkonfirmasi", key="cough_known")
        coughs = st.number_input("Batuk per 10 menit", 0, 1000, disabled=not cough_known, key="coughs")
        st.caption("Hitungan mikrofon kandang bukan hitungan per ekor tanpa identifikasi sumber.")
    with c2, st.container(border=True):
        st.subheader("02 / Citra klinis")
        image = st.file_uploader("Foto klinis (opsional)", type=["jpg", "jpeg", "png"])
        if image:
            if image.size > 5 * 1024 * 1024:
                st.error("Batas citra 5 MB.")
            else:
                try:
                    st.image(image, caption="Bukti visual — tinjauan manual", width="stretch")
                except Exception:
                    st.error("Citra tidak terbaca. Unggah PNG/JPEG valid.")
        signs_known = st.checkbox("Gejala sudah ditinjau petugas", key="signs_known")
        signs = st.multiselect("Gejala terlihat", ["Luka mulut", "Air liur berlebih", "Lesi kuku"], disabled=not signs_known, key="signs")
    with c3, st.container(border=True):
        st.subheader("03 / Suhu tubuh")
        temp_known = st.checkbox("Pengukuran suhu tubuh tersedia", key="temp_known")
        temperature = st.number_input("Suhu tubuh (°C)", 30.0, 45.0, 38.5, 0.1, disabled=not temp_known, key="temperature")
        st.caption("Gunakan prosedur tervalidasi. Ukur ulang nilai ekstrem; bukan suhu lingkungan atau suhu permukaan.")
    if st.button("Hitung & simpan pemeriksaan", type="primary"):
        if not animal.strip() or not pen.strip() or not animal.strip().isprintable() or not pen.strip().isprintable():
            st.error("Isi ID ternak dan kandang valid.")
        elif not any([cough_known, signs_known, temp_known]):
            st.error("Isi minimal satu sinyal. Skor gabungan membutuhkan ketiganya.")
        else:
            record = {"id": animal.strip(), "pen": pen.strip(), "coughs": int(coughs) if cough_known else None,
                      "signs": len(signs) if signs_known else None, "temperature": temperature if temp_known else None,
                      "source": "Simulasi" if st.session_state.simulated else "Observasi manual", "time": datetime.now().astimezone().isoformat(timespec="seconds")}
            st.session_state.records = [r for r in st.session_state.records if r["id"] != record["id"]] + [record]
            st.session_state.last_result = record
    st.caption("Simpan memperbarui observasi terakhir ID sama. Riwayat dan berkas bukti tidak disimpan; unduh CSV sebelum menutup sesi.")
    if "last_result" in st.session_state:
        row = st.session_state.last_result
        result = assess(row["coughs"], row["signs"], row["temperature"])
        st.divider()
        st.subheader(f"Hasil tersimpan: {row['id']}")
        st.caption(f"{row['time']} — bukan perubahan formulir yang belum disimpan.")
        st.metric(result["label"], "Belum lengkap" if result["score"] is None else f"{result['score']}/100")
        st.write("Kontribusi aturan demo: " + " · ".join(f"{k}: {'belum tersedia' if v is None else f'{v:.1f} poin'}" for k, v in result["parts"].items()))
        if result["label"] == "Prioritas tinggi":
            st.error("Hubungi dokter hewan/petugas kesehatan hewan untuk penilaian segera. Batasi perpindahan dan kontak ternak sesuai arahan petugas. Jangan menunggu skor meningkat.")
        elif result["label"] == "Data belum lengkap":
            st.warning("Lengkapi sinyal. Data tidak lengkap bukan hasil negatif.")
        else:
            st.info("Lanjutkan observasi. Hubungi dokter hewan bila muncul gejala, sulit bernapas, atau kondisi memburuk, berapa pun skornya.")

else:
    st.subheader("Cara membaca skor")
    st.markdown("""
- **Batuk (0–30):** `min(jumlah batuk / 10, 1) × 30`, hitungan terkonfirmasi per 10 menit.
- **Gejala (0–45):** jumlah jenis gejala dibagi 3, dikali 45.
- **Suhu (0–25):** `min(max((suhu − 39) / 1,5, 0), 1) × 25`.
- Ketiga sinyal lengkap: jumlah dibulatkan menjadi indeks 0–100. Tidak lengkap: skor tidak diterbitkan.
- Skor ≥60: prioritas tinggi; 25–59: perlu dipantau; <25: sinyal rendah.
- **Override:** satu gejala klinis atau suhu ≥40,5 °C tetap prioritas tinggi, termasuk saat skor rendah atau data tidak lengkap.

Bobot dan ambang adalah **asumsi demonstrasi untuk sapi**, bukan ambang klinis tervalidasi.
Sinyal berkorelasi; penjumlahan bukan bukti akurasi meningkat. Batuk tidak spesifik PMK.
Suhu rendah ekstrem atau tanda bahaya lain memerlukan evaluasi meskipun indeks rendah.
""")
    st.subheader("Bukti awal, bukan janji akurasi")
    st.markdown("""
| Informasi dari brief | Batas interpretasi |
|---|---|
| Sumbawa: 12.814 ekor pada puncak PMK 2022 | Angka pengguna; sumber primer belum diverifikasi. |
| Diagnosis manual sekitar 48 jam per ekor | Klaim brief; bukan durasi standar semua pemeriksaan. |
| CNN 100%; SMO 90%; IBk 87%; Trees.J48 86%; Naive Bayes 79% | Hasil dilaporkan, bukan performa prototype. Dataset kecil/terkontrol berpotensi bias; perlu telaah pembagian data dan validasi eksternal. |
| AgriEngineering 2025: 16 mikrofon, dua kandang babi, enam hari, 1.110 batuk | Jumlah tangkapan bukan sensitivitas/spesifisitas; belum membuktikan kinerja pada sapi atau diagnosis PMK. |
""")
    st.write("Rujukan pengguna: Bulletin of Information Technology, Vol. 6 No. 4, Desember 2025, hlm. 337–344, Universitas Teknologi Sumbawa.")
    st.write("DOI yang diberikan: https://doi.org/10.47065/bit.v5i2.2245")
    st.warning("Metadata DOI memuat v5i2, berbeda dengan volume/nomor yang disebutkan. Kesesuaian artikel belum diverifikasi. Rujukan ‘AI (BRDC) 2026, 5 (2025)’ dan ‘JUSTINDO PMK (2026)’ belum cukup lengkap untuk diidentifikasi.")
    st.subheader("Sebelum dipakai di lapangan")
    st.write("Butuh dataset sapi berlabel dokter hewan, pemisahan data berdasarkan ternak/kandang, validasi eksternal, kalibrasi sensor, identifikasi sumber batuk, evaluasi sensitivitas, spesifisitas dan alarm palsu. Klaim batuk mendahului gejala harus diuji per penyakit. Tidak ada CNN atau detektor audio dalam prototype ini.")
