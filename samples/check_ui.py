"""Run with project .venv Python; Streamlit built-in testing, no extra framework."""
import json
from pathlib import Path
import sys
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from risk import assess

app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
assert not app.exception, app.exception
app.sidebar.radio[0].set_value("Pemeriksaan ternak").run()
for index, case in enumerate(json.loads((ROOT / "samples/scenarios.json").read_text())):
    app.selectbox(key="scenario_index").set_value(index).run()
    next(b for b in app.button if b.label == "Muat sample ke formulir").click().run()
    assert not app.exception, app.exception
    assert app.text_input(key="animal").value == case["id"]
    next(b for b in app.button if b.label == "Hitung & simpan pemeriksaan").click().run()
    assert not app.exception, app.exception
    record = app.session_state["last_result"]
    assert record["source"] == "Simulasi"
    result = assess(record["coughs"], record["signs"], record["temperature"])
    assert (result["score"], result["label"]) == (case["expected"], case["status"])
for page in ["Ringkasan", "Metode & referensi"]:
    app.sidebar.radio[0].set_value(page).run()
    assert not app.exception, app.exception
print("Six load/save scenarios and all pages passed")
