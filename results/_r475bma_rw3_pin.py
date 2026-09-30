# r475 bm-a: RW-3 param pinning (recon memo sequence: explicit params in
# trader JSONs BEFORE engine default flip).
# - 6 registered members: pin the UPGRADED caliber (full + strict) --
#   probe evidence: byte-identical on all 24 anchor fields (0/6 moved).
# - 15 PROSPECT members: pin their declared-at-freeze caliber (legacy +
#   non-strict) so frozen P-5 evidence stays reproducible after the flip.
# Backup copies -> results/_r475bma_rw3_pin_backup/ for this round only.
import json
import os
import shutil

MEMBERS = ["COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
           "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01"]
UP = {"trade_pnl_mode": "full", "strict_open_fills": True}
PIN_LEGACY = {"trade_pnl_mode": "legacy", "strict_open_fills": False}
BK = "results/_r475bma_rw3_pin_backup"
os.makedirs(BK, exist_ok=True)

changed = {"upgraded": [], "pinned_legacy": [], "skipped": []}
for fn in sorted(os.listdir("firm/traders")):
    if not fn.endswith(".json") or fn == "_template.json":
        continue
    tid = fn[:-5]
    path = os.path.join("firm/traders", fn)
    with open(path, encoding="utf-8") as f:
        t = json.load(f)
    if tid in MEMBERS:
        target, tag = UP, "upgraded"
    elif t.get("level") == "PROSPECT":
        target, tag = PIN_LEGACY, "pinned_legacy"
    else:
        changed["skipped"].append(tid)
        continue
    if all(t["params"].get(k) == v for k, v in target.items()):
        changed["skipped"].append(tid)
        continue
    shutil.copy2(path, os.path.join(BK, fn))
    t["params"].update(target)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(t, f, indent=2, ensure_ascii=False)
    changed[tag].append(tid)

print(json.dumps(changed, indent=1))
assert len(changed["upgraded"]) == 6, "6 registered members must be upgraded"
print("OK: 6 upgraded +", len(changed["pinned_legacy"]), "prospect pinned legacy")
