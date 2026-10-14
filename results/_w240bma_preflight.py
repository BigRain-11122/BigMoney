# -*- coding: utf-8 -*-
# r990 bm-a W240 freeze preflight: live fact verification (never transcribed, all import-derived)
import json, os, re, sys, io, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import perpetual_faces as pf_mod

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = {}

# 1. W239 registered row (live import)
W239 = dict(pf_mod.N1_BANDS.get(239) or {})
out["W239_row"] = W239
assert W239.get("engine_owner") == "bm-c", "W239 owner drift"
assert list(W239["a"]) == [542501, 544500] and list(W239["b_exit"]) == [540604, 540803], "W239 band drift"

# 2. W239 finalize product anchors (live read)
w239_out = json.load(open(os.path.join(REPO, "results", "perpetual_faces", "n1_w239_results.json"), encoding="utf-8"))
led = (w239_out.get("science_gates") or {}).get("ledger") or {}
merged_n = w239_out["null_pool_cumulative"]["merged"]["n_values"]
out["W239_final"] = {"total": led.get("total"), "batch": led.get("batch"), "merged_n": merged_n}
assert led.get("total") == 950135 and led.get("batch_trials") == 2200, "ledger drift"
assert merged_n == 523720, "merged n drift"

# 3. W240 prereg: exists, committed, no DRAFT
pre_path = os.path.join(REPO, "research", "PERPETUAL_N1_W240_PREREG.md")
head_txt = open(pre_path, encoding="utf-8").read(2000)
assert "DRAFT-NOT-FROZEN" not in head_txt, "W240 prereg still DRAFT"
r = subprocess.run(["git", "-C", REPO, "log", "--format=%H", "--", "research/PERPETUAL_N1_W240_PREREG.md"],
                   capture_output=True, text=True)
out["prereg_commits"] = [c[:10] for c in r.stdout.strip().splitlines()[:3]]
assert r.stdout.strip(), "prereg not committed"

# 4. n1 file structure anchors (W239 block is last, T-141 marker present exactly once)
n1_t = open(os.path.join(REPO, "scripts", "perpetual_faces_n1.py"), encoding="utf-8").read()
pf_t = open(os.path.join(REPO, "scripts", "perpetual_faces.py"), encoding="utf-8").read()
for needle, n in [("    # --- W239 materializer face", 1), ("    # --- T-141 s2 lane face", 1),
                  ('239: {"batch": "PERPETUAL-N1-W239"', 1), ('"+ W239 materializer face', 1)]:
    c = n1_t.count(needle); assert c == n, f"n1 anchor {needle!r} count {c} != {n}"
for needle, n in [('    239: {"a"', 1), ('238: {"a"', 1)]:
    c = pf_t.count(needle); assert c == n, f"pf anchor {needle!r} count {c} != {n}"
# W239 cfg entry must have engine_owner=bm-c mirror material
assert n1_t.count('"engine_owner": "bm-c"') >= 3
# pf W239 owner line
i = pf_t.find('    239: {"a"')
ls = pf_t.find("\n", i) + 1; le = pf_t.find("\n", ls)
out["pf_239_owner_line"] = pf_t[ls:le]
assert '"engine_owner": "bm-c"}' in pf_t[ls:le], "W239 owner line missing bm-c"
# W239 materializer block span (block start to T-141)
s = n1_t.find("    # --- W239 materializer face"); e = n1_t.find("    # --- T-141 s2 lane face")
blk = n1_t[s:e]
out["w239_block_rows"] = blk.count("assert pf.N1_BANDS[")
# estate + legs structure inside W239 block: 97 rows (90 estate + W232..W238 legs)
m_first = re.search(r"assert pf\.N1_BANDS\[", blk)
m_disj = re.search(r"        # prior-wave disjointness W2\.\.W\d+ \(single state", blk)
assert m_first and m_disj and m_disj.start() > m_first.start(), "parity markers"
row_ls = blk.rfind("\n", 0, m_first.start()) + 1
par_full = blk[row_ls:m_disj.start()]
ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", par_full)
out["w239_parity_rows"] = len(ws)
out["w239_parity_tail"] = ws[-6:]
# ordinals live
owner_rows = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner")]
bma_rows = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-a"]
bmc_rows = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
out["ordinals"] = {"owner": len(owner_rows), "bma": len(bma_rows), "bmc": len(bmc_rows)}
assert len(owner_rows) == 229 and len(bma_rows) == 122 and len(bmc_rows) == 66, "ordinal drift at freeze"

# 5. gate receipts present
for f in ("results/_w240bma_20261014_probe_receipt.json", "results/_w240bma_prereg_derive_receipt.json"):
    assert os.path.exists(os.path.join(REPO, f)), f + " missing"

# 6. seat MSG present (inbox or processed)
seat_found = None
for p in ("fleet/inbox", "fleet/inbox/processed"):
    if os.path.exists(os.path.join(REPO, p, "MSG-20261014-1325-bma-w240-seat.md")):
        seat_found = p + "/MSG-20261014-1325-bma-w240-seat.md"; break
out["seat"] = seat_found
assert seat_found, "W240 seat MSG missing"

# 7. upstream finalize products W17..W239 all present (cumulative deps)
missing = [w for w in range(17, 240)
           if not os.path.exists(os.path.join(REPO, "results", "perpetual_faces", f"n1_w{w}_results.json"))]
out["missing_deps"] = missing
assert not missing, f"missing upstream deps: {missing}"

# 8. fivekey receipt of W239 (five_keys_all_pass)
fk = json.load(open(os.path.join(REPO, "results", "_w239bmc_fivekey_receipt.json"), encoding="utf-8"))
assert fk.get("five_keys_all_pass") is True, "W239 fivekey not ALL PASS"
out["w239_fivekey_all_pass"] = True

print(json.dumps(out, ensure_ascii=False, indent=1))
print("PREFLIGHT OK")
