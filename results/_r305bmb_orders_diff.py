# -*- coding: utf-8 -*-
"""r305 bm-b: S0.5 orders double-scan (R13 law: full set-diff, no ts filter).

File face (fleet/orders/O-*.md) vs heartbeat ack face (orders_ack tokens).
Output: counts + unacked (files needing action) + ghost (acked but file
missing). Zero unacked => mirror of fleet/orders is faithful for this
machine; group decisions.md direct-scan stays unreachable-no-clone (R291
standing note), fleet/orders mirror is the honest substitute lane.
"""
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDERS_DIR = os.path.join(ROOT, "fleet", "orders")
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
OUT = os.path.join(ROOT, "results", "_r305bmb_orders_diff.json")

files = sorted(f for f in os.listdir(ORDERS_DIR)
               if f.startswith("O-") and f.endswith(".md"))
hb = json.load(io.open(HB, encoding="utf-8-sig"))
acked = set((hb.get("orders_ack") or "").split())
fs = set(files)
unacked = sorted(fs - acked)
ghost = sorted(acked - fs)

out = {
    "ts": __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds"),
    "round": "r305",
    "machine": "bm-b",
    "orders_files": len(fs),
    "ack_tokens": len(acked),
    "unacked": unacked,
    "ghost_ack": ghost,
    "verdict": "clean" if not unacked and not ghost else "action_needed",
    "note": ("full set-diff both directions, no timestamp filtering (R13 "
             "O-1820 skip-number lesson); group decisions.md direct-scan "
             "unreachable on bm-b (no group-repo clone, R291 honest note), "
             "fleet/orders mirror is the substitute lane"),
}
with io.open(OUT, "w", encoding="utf-8", newline="") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False))
raise SystemExit(0 if out["verdict"] == "clean" else 1)
