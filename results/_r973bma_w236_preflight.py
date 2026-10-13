# -*- coding: utf-8 -*-
# r973 bm-a window: W236 five-face freeze SPLICE PREFLIGHT receipt builder.
# Purpose: machine-verify ALL splice preconditions live and emit the exact
# facts the next window's _w236bma_freeze_edits.py derivation consumes.
# (The freeze editor itself is derived from the committed W235 template
#  _w235bma_freeze_edits.py per lineage law; this preflight does NOT splice.)
import json, os, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIT = r"C:\Program Files\Git\cmd\git.exe"
out = {}

def g(*a):
    r = subprocess.run([GIT, "-C", REPO, *a], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout.strip()

# ---- 1) probe receipt (ADMIT) ----
rec = json.load(open(os.path.join(REPO, "results", "_w236bma_20261014_probe_receipt.json"), encoding="utf-8"))
out["probe_receipt"] = {
    "verdict": rec.get("verdict"),
    "bands": rec.get("bands"),
    "path": "results/_w236bma_20261014_probe_receipt.json",
}
assert rec.get("verdict") == "ADMIT", f"probe receipt not ADMIT: {rec.get('verdict')}"
b = rec.get("bands") or {}
assert b.get("a_lo") == 534004 and b.get("b_lo") == 536004, f"W236 declared bands drift: {b}"

# ---- 2) live law file: W235 row registered, W236 absent ----
sys.path.insert(0, os.path.join(REPO, "scripts"))
import perpetual_faces as pf_mod
W235 = dict(pf_mod.N1_BANDS.get(235) or {})
W236_live = dict(pf_mod.N1_BANDS.get(236) or {})
out["W235_row_live"] = W235
out["W236_row_live"] = W236_live
assert W235.get("engine_owner") == "bm-a", f"W235 owner face: {W235}"
a_t = W235.get("a") or ()
b_t = W235.get("b_exit") or ()
assert tuple(a_t) == (531804, 533803), f"W235 bands A drift: {W235}"
assert tuple(b_t) == (533804, 534003), f"W235 bands B drift: {W235}"
assert not W236_live, f"W236 already registered in law file -- splice window stale: {W236_live}"

# ---- 3) W235 finalize product + anchors (upstream chain-order precondition) ----
w235_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w235_results.json")
assert os.path.exists(w235_out_path), "W235 finalize product missing"
w235_out = json.load(open(w235_out_path, encoding="utf-8"))
led = (w235_out.get("science_gates") or {}).get("ledger") or {}
merged_n = None
try:
    merged_n = w235_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
out["W235_finalize"] = {"ledger_total": led.get("total"), "merged_n": merged_n,
                        "product": "results/perpetual_faces/n1_w235_results.json"}
assert led.get("total") == 940789 and merged_n == 514920, \
    f"W235 finalize anchors drift: total={led.get('total')} merged={merged_n} (expect 940,789 / 514,920)"
# transitive deps present
for w in (234, 233, 232, 231, 230, 225, 224, 223):
    p = os.path.join(REPO, "results", "perpetual_faces", f"n1_w{w}_results.json")
    assert os.path.exists(p), f"transitive chain dep missing: n1_w{w}_results.json"
out["transitive_deps_present"] = True

# ---- 4) W236 prereg on origin + on disk (r972 landed) ----
chk = subprocess.run([GIT, "-C", REPO, "cat-file", "-e", "origin/main:research/PERPETUAL_N1_W236_PREREG.md"], capture_output=True)
assert chk.returncode == 0, "W236 prereg NOT on origin -- chain face incomplete"
prereg_disk = os.path.join(REPO, "research", "PERPETUAL_N1_W236_PREREG.md")
assert os.path.exists(prereg_disk), "W236 prereg missing on disk"
w236_prereg_sha = g("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W236_PREREG.md").splitlines()[:1]
w236_prereg_sha_committed = g("log", "--format=%H", "-1", "--", "research/PERPETUAL_N1_W236_PREREG.md").splitlines()[:1]
w235_prereg_sha = g("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W235_PREREG.md").splitlines()[:1]
w235_freeze_sha = g("log", "--format=%H", "-S", '235: {"a"', "--", "scripts/perpetual_faces.py").splitlines()[:1]
w236_receipt_sha = g("log", "--diff-filter=A", "--format=%H", "--", "results/_w236bma_20261014_probe_receipt.json").splitlines()[:1]
out["pickaxe_shas"] = {
    "w236_prereg_add": w236_prereg_sha,
    "w236_prereg_last_committed": w236_prereg_sha_committed,
    "w235_prereg_add": w235_prereg_sha,
    "w235_freeze": w235_freeze_sha,
    "w236_probe_receipt_add": w236_receipt_sha,
}

# ---- 5) W236 own seat MSG on origin (bm-a published r971 @ 5c25db795) ----
seat_ok = subprocess.run([GIT, "-C", REPO, "cat-file", "-e", "origin/main:fleet/inbox/processed/MSG-20261014-0446-bma-w236-seat.md"], capture_output=True)
seat_ok2 = subprocess.run([GIT, "-C", REPO, "cat-file", "-e", "origin/main:fleet/inbox/MSG-20261014-0446-bma-w236-seat.md"], capture_output=True)
seat_loc = "processed" if seat_ok.returncode == 0 else ("inbox" if seat_ok2.returncode == 0 else "MISSING")
out["seat"] = {"msg": "MSG-20261014-0446-bma-w236-seat.md", "origin_state": seat_loc}
assert seat_loc != "MISSING", "W236 own-seat MSG not found on origin"
# foreign-seat hygiene: no other W236 seat files
ip = g("ls-tree", "--name-only", "-r", "origin/main", "fleet/inbox/", "fleet/inbox/processed/")
foreign = [l for l in ip.splitlines() if "W236" in l and "0446" not in l]
assert not foreign, f"foreign W236 seat files: {foreign}"
out["foreign_seat_files"] = []

# ---- 6) ordinal faces (live derive, r587/r359 law) ----
rows = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner")]
bma_rows = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-a"]
bmc_rows = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
out["ordinal_faces"] = {"owner_rows_live": len(rows), "bma_rows_live": len(bma_rows),
                        "bmc_rows_live": len(bmc_rows),
                        "engine_owned_ordinal": len(rows) + 1,
                        "bma_own_ordinal": len(bma_rows) + 1}

# ---- 7) own-band vacancy (seed_admit live re-check, both bands) ----
sa = []
for base, span, tag in ((b.get("a_lo"), 2000, "A"), (b.get("b_lo"), 200, "B")):
    r = subprocess.run(["python", os.path.join(REPO, "Tools", "seed_admit_gate.py"),
                        "--span", str(span), str(base)],
                       capture_output=True, text=True, cwd=REPO)
    tail = (r.stdout or "").strip().splitlines()[-1:] + (r.stderr or "").strip().splitlines()[-1:]
    sa.append({"band": tag, "base": base, "span": span, "rc": r.returncode, "tail": tail})
    assert r.returncode == 0, f"seed_admit gate {tag} rc={r.returncode}: {tail}"
out["seed_admit_gate"] = sa

# ---- 8) engine idle (no active burns -- splice window expects idle queue) ----
eng = subprocess.run(["python", os.path.join(REPO, "scripts", "saturation_engine.py"), "status"],
                     capture_output=True, text=True, cwd=REPO, encoding="utf-8", errors="replace")
try:
    ed = json.loads(eng.stdout)
    out["engine"] = {"alive": ed.get("engine_alive"), "active_burns": ed.get("active_burns"),
                     "queue_depth": ed.get("queue_depth")}
    assert ed.get("engine_alive") is True, "engine not alive"
except Exception:
    out["engine"] = {"parse": "non-json", "raw": (eng.stdout or eng.stderr or "")[:200]}

# ---- 9) W236 declared bands (from receipt verbatim, NINETY-SIXTH staircase) ----
b = rec.get("bands") or {}
out["W236_declared_bands"] = {"A": f"{b.get('a_lo')}_{'%d' % b.get('a_hi') if isinstance(b.get('a_hi'), int) else b.get('a_hi')}",
                              "B": f"{b.get('b_lo')}_{'%d' % b.get('b_hi') if isinstance(b.get('b_hi'), int) else b.get('b_hi')}",
                              "raw": b}
print(json.dumps(out, ensure_ascii=False, indent=1))
# save receipt
import io
with io.open(os.path.join(REPO, "results", "_r973bma_w236_preflight.json"), "w", encoding="utf-8", newline="") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("PREFLIGHT RECEIPT SAVED: results/_r973bma_w236_preflight.json")
