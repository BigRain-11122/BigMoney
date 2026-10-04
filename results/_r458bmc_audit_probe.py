"""r458 bm-c S3 evidence probe (regenerable, read-only): compute_audit flags."""
import json

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
for face in ("results/compute_audit.bm-c.json", "results/watermark.jsonl"):
    pass
with open(ROOT + r"\results\compute_audit.bm-c.json", encoding="utf-8") as f:
    d = json.load(f)
flags = d.get("flags", d.get("violations", "NO-FLAGS-KEY"))
print("audit_flags =", json.dumps(flags, ensure_ascii=False)[:600])
print("load_state =", d.get("load_state"))
print("stale_flag_hits =", d.get("stale_flag_hits", "n/a"))
