import json, os, subprocess, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rec_path = os.path.join(REPO, "results", "_w235bmc_20261013_probe_receipt.json")
rec = json.load(open(rec_path, encoding="utf-8"))
print("verdict:", rec.get("verdict"))
print("bands:", json.dumps(rec.get("bands"), ensure_ascii=False))
print("legs keys:", sorted((rec.get("legs") or {}).keys()))
for k, v in (rec.get("legs") or {}).items():
    print("leg", k, "=", json.dumps(v, ensure_ascii=False)[:400])
print()
for k in sorted(rec.keys()):
    if k not in ("legs", "bands"):
        v = rec[k]
        if isinstance(v, (str, int, float, bool)):
            print(k, "=", str(v)[:200])
        elif isinstance(v, dict):
            print(k, "=", json.dumps(v, ensure_ascii=False)[:400])
sys.path.insert(0, os.path.join(REPO, "scripts"))
import perpetual_faces as pf_mod
rows = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner")]
bma_rows = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-a"]
bmc_rows = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
print()
print("owner rows:", len(rows), "| bma:", len(bma_rows), "| bmc:", len(bmc_rows))
print("last wave key:", max(pf_mod.N1_BANDS.keys()))
print("W234:", json.dumps(pf_mod.N1_BANDS.get(234), ensure_ascii=False))
# seat msg location
for p in ("fleet/inbox", "fleet/inbox/processed"):
    f = os.path.join(REPO, p, "MSG-20261013-2149-bmc.md")
    print("seat msg at", p, ":", os.path.exists(f))
# prereg + receipt shas via pickaxe
def g(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.strip()
print("w235 prereg add sha:", g("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W235_PREREG.md").splitlines()[:1])
print("w235 receipt add sha:", g("log", "--diff-filter=A", "--format=%H", "--", "results/_w235bmc_20261013_probe_receipt.json").splitlines()[:1])
print("w234 freeze sha:", g("log", "--format=%H", "-S", '234: {"a"', "--", "scripts/perpetual_faces.py").splitlines()[:1])
# W234 finalize anchors
w234_out = json.load(open(os.path.join(REPO, "results", "perpetual_faces", "n1_w234_results.json"), encoding="utf-8"))
led = (w234_out.get("science_gates") or {}).get("ledger") or {}
merged = None
try:
    merged = w234_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
print("W234 ledger total:", led.get("total"), "| merged n:", merged)
