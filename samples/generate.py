"""Generate synthetic upload fixtures; never clinical evidence. Run directly."""
import csv
import math
from pathlib import Path
import struct
import sys
import wave
import zipfile

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from risk import assess

cases = [
    ("SAMPLE-001", 12, 2, 40.3, 82, "Prioritas tinggi"),
    ("SAMPLE-002", 6, 0, 39.6, 28, "Perlu dipantau"),
    ("SAMPLE-003", 0, 0, 38.6, 0, "Sinyal rendah"),
    ("SAMPLE-004", None, 0, 38.8, None, "Data belum lengkap"),
    ("SAMPLE-005", 0, 1, 38.5, 15, "Prioritas tinggi"),
]
with (ROOT / "observasi_demo.csv").open("w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    writer.writerow(["id", "kandang", "batuk_per_10_menit", "jumlah_gejala", "suhu_c", "skor_harapan", "status_harapan", "sumber"])
    for animal, coughs, signs, temp, score, label in cases:
        result = assess(coughs, signs, temp)
        assert (result["score"], result["label"]) == (score, label)
        writer.writerow([animal, "Kandang Demo", coughs, signs, temp, score, label, "SIMULASI"])

# ponytail: tone fixture only; replace with consented, annotated cattle audio for model validation.
rate = 8000
with wave.open(str(ROOT / "audio_sintetis_10_menit.wav"), "wb") as audio:
    audio.setparams((1, 2, rate, 0, "NONE", "not compressed"))
    silence = bytes(rate * 2)
    pulse = b"".join(struct.pack("<h", int(2200 * math.sin(2 * math.pi * 440 * i / rate)))
                     if i < rate // 5 else b"\x00\x00" for i in range(rate))
    for second in range(600):
        audio.writeframesraw(pulse if second % 50 == 0 else silence)
with wave.open(str(ROOT / "audio_sintetis_10_menit.wav")) as audio:
    assert audio.getnframes() / audio.getframerate() == 600

image = Image.new("RGB", (1000, 600), "#f0f6f3")
draw = ImageDraw.Draw(image)
draw.text((50, 45), "SIMULASI - BUKAN FOTO KLINIS", fill="#173f3b", font_size=38)
draw.rectangle((50, 130, 950, 460), outline="#167367", width=4)
draw.text((80, 170), "Fixture PNG untuk uji unggah dan pratinjau.", fill="#173f3b", font_size=28)
draw.text((80, 240), "Tidak menggambarkan lesi atau penyakit.", fill="#173f3b", font_size=28)
draw.text((80, 310), "Gejala diisi manual dari skenario CSV.", fill="#173f3b", font_size=28)
image.save(ROOT / "citra_sintetis.png")
with Image.open(ROOT / "citra_sintetis.png") as check:
    check.verify()

with zipfile.ZipFile(ROOT / "sample_ternak_siaga.zip", "w", zipfile.ZIP_DEFLATED) as archive:
    for name in ["observasi_demo.csv", "audio_sintetis_10_menit.wav", "citra_sintetis.png", "README.md"]:
        archive.write(ROOT / name, arcname=name)
print("Sample CSV, WAV, PNG, ZIP generated; assertions passed.")
