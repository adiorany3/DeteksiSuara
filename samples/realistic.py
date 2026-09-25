"""Synthetic field scenarios and media; no clinical claims. Run to rebuild and check."""
import csv
import json
import math
from pathlib import Path
import random
import struct
import sys
import wave
import zipfile
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from risk import assess

cases = json.loads((ROOT / "scenarios.json").read_text())
with (ROOT / "skenario_lapangan.csv").open("w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    writer.writerow(["id", "kandang", "batuk_10_menit", "gejala", "suhu_c", "skor", "status", "konteks", "kualitas", "tindak_lanjut", "sumber"])
    for case in cases:
        result = assess(case["coughs"], None if case["signs"] is None else len(case["signs"]), case["temperature"])
        assert (result["score"], result["label"]) == (case["expected"], case["status"]), case
        writer.writerow([case["id"], case["pen"], case["coughs"], None if case["signs"] is None else "; ".join(case["signs"]),
                         case["temperature"], case["expected"], case["status"], case["context"], case["quality"], case["action"], "SIMULASI"])

# ponytail: procedural noise, not animal audio; replace only with licensed, annotated field recordings.
rng = random.Random(42)
rate = 16000
frames = bytearray()
events = [4.2, 4.65, 12.1, 20.4, 21.0, 26.3]
for i in range(rate * 30):
    t = i / rate
    value = 0.018 * rng.uniform(-1, 1) + 0.012 * math.sin(2 * math.pi * 70 * t)
    for start in events:
        dt = t - start
        if 0 <= dt < 0.32:
            envelope = math.sin(math.pi * dt / 0.32) * math.exp(-7 * dt)
            value += envelope * (0.42 * rng.uniform(-1, 1) + 0.13 * math.sin(2 * math.pi * 180 * t))
    frames.extend(struct.pack("<h", int(max(-1, min(value, 1)) * 32767)))
with wave.open(str(ROOT / "audio_latar_sintetis.wav"), "wb") as audio:
    audio.setparams((1, 2, rate, 0, "NONE", "not compressed"))
    audio.writeframes(frames)
with wave.open(str(ROOT / "audio_latar_sintetis.wav")) as audio:
    assert audio.getnframes() == rate * 30

image = Image.new("RGB", (1100, 650), "#edf3ef")
d = ImageDraw.Draw(image)
d.text((36, 28), "SIMULASI / PANDUAN AREA INSPEKSI", fill="#173d38", font_size=32)
d.text((36, 78), "Ilustrasi skematis - bukan foto lesi atau diagnosis", fill="#47645b", font_size=23)
for x, title in [(35, "01  MULUT"), (395, "02  AIR LIUR"), (755, "03  KUKU")]:
    d.rounded_rectangle((x, 135, x + 315, 535), radius=20, fill="white", outline="#b6cfc1", width=2)
    d.text((x + 20, 158), title, fill="#173d38", font_size=24)
d.ellipse((90, 245, 295, 380), fill="#bf9281", outline="#61483f", width=3)
d.arc((105, 290, 280, 360), 0, 180, fill="#61483f", width=5)
d.line((190, 340, 190, 405), fill="#bc663c", width=3)
d.text((62, 428), "Periksa permukaan", fill="#173d38", font_size=22)
d.text((62, 462), "dan luka teramati", fill="#173d38", font_size=22)
d.ellipse((450, 245, 655, 365), fill="#bf9281", outline="#61483f", width=3)
for x in [510, 548, 585]:
    d.line((x, 348, x-8, 397), fill="#429ca8", width=5)
d.text((420, 428), "Amati air liur", fill="#173d38", font_size=22)
d.text((420, 462), "dan perilaku makan", fill="#173d38", font_size=22)
d.rectangle((850, 232, 970, 325), fill="#bf9281")
d.polygon([(850, 315), (825, 385), (905, 385), (910, 325)], fill="#514c49")
d.polygon([(920, 325), (925, 385), (995, 385), (970, 315)], fill="#514c49")
d.text((780, 428), "Tinjau kuku", fill="#173d38", font_size=22)
d.text((780, 462), "dan cara berjalan", fill="#173d38", font_size=22)
d.text((36, 577), "Gejala harus dinilai petugas. Ilustrasi ini bukan data model AI.", fill="#173d38", font_size=24)
image.save(ROOT / "ilustrasi_observasi.png")
with Image.open(ROOT / "ilustrasi_observasi.png") as check:
    check.verify()
with zipfile.ZipFile(ROOT / "sample_ternak_siaga.zip", "w", zipfile.ZIP_DEFLATED) as archive:
    for name in ["scenarios.json", "skenario_lapangan.csv", "audio_latar_sintetis.wav", "ilustrasi_observasi.png", "README.md"]:
        archive.write(ROOT / name, name)
print("Six scenarios, WAV, illustration and ZIP verified")
