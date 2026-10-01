"""r524 bm-b: W28 12/12 completeness + ownership verification (r310 gate, pre-finalize)."""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "results", "p2cal_ext", "n1_w28")

def git(*args):
    return subprocess.check_output(["git", "-C", ROOT] + list(args), text=True, encoding="utf-8")

# local 12 shards
local = sorted(f for f in os.listdir(D) if f.startswith("shard-") and f.endswith(".json"))
print("local shards:", len(local))

# origin ls-tree 12 shards (r310 completeness: pool done != product delivered)
origin = [l.split()[-1] for l in git("ls-tree", "origin/main", "results/p2cal_ext/n1_w28/").splitlines() if "shard-" in l]
origin = sorted(l for l in origin if l.split("/")[-1].startswith("shard-"))
print("origin shards:", len(origin))
assert len(local) == 12 and len(origin) == 12, "completeness FAIL"

# ownership + payload sanity (r323/r513 law: audit.machine before any action)
totals = []
for f in local:
    with open(os.path.join(D, f), "r", encoding="utf-8") as fh:
        d = json.load(fh)  # json.loads gate
    m = d.get("audit", {}).get("machine")
    n = d.get("n_values", d.get("n", "?"))
    assert m == "bm-b", f"{f} ownership FAIL: {m}"
    totals.append(n)
print("ownership: 12/12 audit.machine=bm-b")
print("n_values:", totals, "sum:", sum(t for t in totals if isinstance(t, int)))

# band integrity vs law (W28 = A 99_004..101_003 / B 40_451..40_650, r523 frozen)
import sys as _s
_s.path.insert(0, os.path.join(ROOT, "scripts"))
import perpetual_faces as pf
w28 = pf.N1_BANDS[28]
print("law bands W28:", w28)
a_seeds = set()
for f in local:
    with open(os.path.join(D, f), "r", encoding="utf-8") as fh:
        d = json.load(fh)
    # collect seed presence if recorded
    for cell in d.get("cells", []) if isinstance(d.get("cells"), list) else []:
        s = cell.get("a_seed", cell.get("seed"))
        if s is not None:
            a_seeds.add(s)
if a_seeds:
    lo, hi = w28["a"][0], w28["a"][1]
    out_of_band = [s for s in a_seeds if not (lo <= s <= hi)]
    print(f"a-seed face: {len(a_seeds)} distinct, out-of-band: {len(out_of_band)}")
    assert not out_of_band, f"OUT-OF-BAND seeds: {out_of_band[:5]}..."
else:
    print("a-seed face: not recorded per-cell (shard-level) -- band check skipped")

print("W28-VERIFY: ALL PASS (12/12 local+origin, bm-b owned, payloads parse)")
