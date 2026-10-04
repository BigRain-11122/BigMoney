"""r665: read probe output detail — per-event fast10 grid + no-fire events."""
import json, io

d = json.load(io.open("results/theme_ring/theme_ignition_face_probe.json", encoding="utf-8"))
for r in d["events"]:
    f = r["fast10"]
    st = f.get("status", "FIRED")
    print(f"{r['id']:16s} anchor={r['ceo_anchor']} face={r['anchor_face'][:28]:28s} "
          f"fast10={f.get('fire_date')} d_td={f.get('delta_td')} pm10={f.get('match_pm10td','-')}")
print("--- summary ---")
print(json.dumps(d["summary_by_face"], ensure_ascii=False, indent=1))
