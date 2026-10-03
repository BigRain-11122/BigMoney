"""r634 bm-b: crash fuse + trio k-monotonicity zero-blocker evidence."""
import json

cf = json.load(open(r"results/crash_fuse.json", encoding="utf-8"))
print("FUSE_KEYS:", {k: cf[k] for k in list(cf)[:8]})

for fam in ("fund_value_p1", "fund_quality_p1", "fund_divlowvol_p1"):
    p = rf"results/{fam}/nulls.jsonl"
    ks = []
    for line in open(p, encoding="utf-8"):
        ks.append(json.loads(line).get("k"))
    dup = len(ks) - len(set(ks))
    mono = all(b > a for a, b in zip(ks, ks[1:]))
    print(fam, "n=", len(ks), "dup_k=", dup, "monotonic=", mono, "max_k=", max(ks))
