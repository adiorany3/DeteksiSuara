"""Transparent demo rules; not a trained or clinically validated model."""
import math


def assess(coughs, signs, temperature):
    if coughs is not None and (type(coughs) is not int or not 0 <= coughs <= 1000):
        raise ValueError("Batuk harus bilangan bulat 0–1000 per 10 menit.")
    if signs is not None and (type(signs) is not int or not 0 <= signs <= 3):
        raise ValueError("Jumlah gejala harus 0–3.")
    if temperature is not None and (
        isinstance(temperature, bool) or not isinstance(temperature, (int, float))
        or not math.isfinite(temperature) or not 30 <= temperature <= 45
    ):
        raise ValueError("Suhu harus angka 30–45 °C; verifikasi pengukuran ekstrem.")
    # ponytail: demo untuk sapi, bukan probabilitas; ganti aturan setelah validasi dokter hewan.
    parts = {
        "Batuk": None if coughs is None else min(coughs / 10, 1) * 30,
        "Citra/gejala": None if signs is None else signs / 3 * 45,
        "Suhu": None if temperature is None else min(max((temperature - 39) / 1.5, 0), 1) * 25,
    }
    complete = all(value is not None for value in parts.values())
    score = round(sum(value for value in parts.values() if value is not None)) if complete else None
    red_flag = (signs is not None and signs > 0) or (temperature is not None and temperature >= 40.5)
    if red_flag or (score is not None and score >= 60):
        label = "Prioritas tinggi"
    elif not complete:
        label = "Data belum lengkap"
    elif score >= 25:
        label = "Perlu dipantau"
    else:
        label = "Sinyal rendah"
    return {"score": score, "label": label, "parts": parts, "complete": complete}


if __name__ == "__main__":
    assert assess(0, 0, 38.5)["score"] == 0
    assert assess(10, 3, 40.5)["score"] == 100
    assert assess(0, 1, 38.5)["label"] == "Prioritas tinggi"
    assert assess(None, 0, 38.5)["score"] is None
    assert assess(None, 1, None)["label"] == "Prioritas tinggi"
    assert assess(10, 0, 39)["label"] == "Perlu dipantau"
    for args in [(-1, 0, 39), (0, 4, 39), (0, 0, float("nan")), (0, 0, 46)]:
        try:
            assess(*args)
        except ValueError:
            pass
        else:
            raise AssertionError(args)
    print("Risk checks passed")
