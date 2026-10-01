# W52 prereg anchor extraction: latest LANDED N1 finalize = W49 (bm-b r558,
# K=103,520, ledger head 470,148). W48 re-derive pending (bm-a declared),
# W50/W51 registered + burned 12/12, finalizes chain-pending (r307).
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
for w in (49, 47):
    p = f"results/perpetual_faces/n1_w{w}_results.json"
    d = json.load(open(p, encoding="utf-8"))
    print(f"===W{w} top-level keys===")
    print(sorted(d.keys()))
    for k in ("merged", "wave_only", "w_only", "summary", "skill_line",
              "k_lift", "klift", "audit", "ledger", "trials_ledger"):
        if k in d:
            v = d[k]
            s = json.dumps(v, ensure_ascii=False)
            print(f"[{k}] {s[:1200]}")
