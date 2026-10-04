"""r458 bm-c S3 quick probe (regenerable, read-only): watermark_red two keys."""
import json

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
with open(ROOT + r"\results\watermark_red.json", encoding="utf-8") as f:
    d = json.load(f)
print("red =", d.get("red"))
np = d.get("next_pick")
print("next_pick =", json.dumps(np, ensure_ascii=False)[:300])
