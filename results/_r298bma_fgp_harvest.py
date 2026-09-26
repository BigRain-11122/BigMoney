"""R298 bm-a: FUSION_GRID_P1 harvest (T-85 s2/s3) -- gate_attrition row
(harvest-time append per prereg sec.8 + product attrition_note, r248
entries-list law) + pool done-flip (r244/r291 live-read assert law) +
post_review criteria registration (stable-product anchors only,
D-20260927-04 no-hot-file law; values dry-run verified exactly as the
reviewer sees them BEFORE any write).
Byte faces probed before every write-back (r255 five-face law).
"""
import io
import json
import re
import sys
import os
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from screening.pbo import cscv_pbo

TS = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
P1 = "results/fusion_grid_p1/p1_results.json"
PR = "research/FUSION_GRID_P1_PREREG.md"
ATT = "results/gate_attrition.json"
POOL = "results/runnable_pool.json"
CRIT = "results/post_review_criteria.json"


def faces(path):
    raw = open(path, "rb").read()
    m = re.search(rb"\n(\s+)\"", raw)
    return {"bom": raw[:3] == b"\xef\xbb\xbf", "crlf": raw.count(b"\r\n"),
            "lf": raw.count(b"\n"), "tail_nl": raw.endswith(b"\n"),
            "indent": (m.group(1) if m else b"").decode()}


fa, fp_, fc_ = faces(ATT), faces(POOL), faces(CRIT)
print("attrition faces:", fa)
print("pool faces:", fp_)
print("criteria faces:", fc_)

# ---------- 1) rebuild 45-cell return matrix, recompute CSCV, zero-drift assert ----------
d = json.load(io.open(P1, encoding="utf-8"))
keys = list(d["cells"].keys())
assert len(keys) == 45
mat = pd.DataFrame({k: json.load(io.open("results/fusion_grid_p1/cells/%s.json" % k,
                                         encoding="utf-8"))["returns"]
                    for k in keys})
pbo = cscv_pbo(mat)
assert abs(float(pbo["pbo"]) - float(d["family_pbo"]["pbo"])) < 5e-5, \
    "PBO recompute drift: %s vs %s" % (pbo["pbo"], d["family_pbo"]["pbo"])
print("PBO recompute zero-drift: %.4f" % float(pbo["pbo"]))

# ---------- 2) gate_attrition row append (entries list, r248 law) ----------
att = json.load(io.open(ATT, encoding="utf-8"))
assert not any(e.get("batch") == "FUSION_GRID_P1" for e in att["entries"]), "row exists"
g1 = {k: bool(d["cells"][k]["g1_pass_v2"]) for k in keys}
g2 = {k: bool(d["cells"][k]["eligible_v2"]) for k in keys}
row = {
    "batch": "FUSION_GRID_P1",
    "ts": TS,
    "kind": "measurement",
    "cells_ledger_delta": 2045,
    "ledger_total_after": 202441,
    "gates": {
        "g1_pass": g1,
        "g2_eligible": g2,
        "d6_reject": {},
        "d6_note": "admission line not applicable -- zero new signal functions; "
                   "members = already-judged registered NAV faces (prereg sec.1); "
                   "batch-internal structural corr = N_eff billing face",
        "family_pbo": pbo,
    },
    "note": ("R298 bm-a harvest-time append per prereg sec.8 + product attrition_note "
             "(r248 entries-list law; runner deliberately defers attrition to harvest). "
             "x1 judged face (fusion-layer cost 0 disclosed, members embed own costs); "
             "best cell EW__DEDUP 0.5301 vs own-null skill line 1.7825 (null pool "
             "mu 0.4209 / sigma 0.2754 / K 2000); bootstrap CI lower -0.3299 <= 0; "
             "DSR best 0.0 (sr_star 1.2511 @ n_trials 202441); PBO band observe. "
             "Verdict semantics = grid config-family shows NO increment over random "
             "same-mask portfolios; member-alpha existence claim NOT falsified "
             "(prereg sec.1 pre-embedded). x2 stress face: all 45 cells <= +0.0454 "
             "(best EW__DEDUP, degradation -0.4847). Descriptive (non-binding) all "
             "pass: 45/45 OOS dual positive, 45/45 maxDD line, 0 crash years. "
             "Regime exact face G754/Y714/R141/O22 (1631d, R296 gate zero-drift). "
             "Execution chain: burn crash 05:50 (KeyError sharpe_full, zero judged "
             "products) -> fix 64023a42 R297 -> relaunch 06:10:01 pid 18524 new sha "
             "0cce3192 (fuse cleared by sha change) -> landed 06:10:37 elapsed "
             "28.8s workers 4; fill latency 29.9min vs O-2100 10min = miss honest "
             "(crash-diagnosis round consumed window)"),
}
att["entries"].append(row)
txt = json.dumps(att, ensure_ascii=False, indent=1)
raw = txt.encode("utf-8").replace(b"\n", b"\r\n")   # probed face: CRLF
assert not raw.startswith(b"\xef\xbb\xbf")          # probed: no BOM
assert not raw.endswith(b"\n")                      # probed: no trailing nl
with io.open(ATT, "wb") as fh:
    fh.write(raw)
chk = json.load(io.open(ATT, encoding="utf-8"))
assert any(e.get("batch") == "FUSION_GRID_P1" for e in chk["entries"])
print("attrition: FUSION_GRID_P1 row appended (entries n=%d)" % len(chk["entries"]))

# ---------- 3) pool done-flip (r244 law + r291 live-read assert) ----------
pool = json.load(io.open(POOL, encoding="utf-8-sig"))
entry = [e for e in pool["entries"] if e.get("id") == "FUSION-GRID-P1"]
assert len(entry) == 1, "pool entry not found"
e = entry[0]
sh = e["shards"][0]
assert e["status"] == "ready" and sh["status"] == "ready", \
    "unexpected pool state: entry=%s shard=%s" % (e["status"], sh["status"])
e["status"] = "done"
sh["status"] = "done"
sh["owner"] = "bm-a"
sh["owner_since"] = "2026-09-27 06:10:01"
e["done_at"] = "2026-09-27 06:10:37"
e["result_ref"] = "results/fusion_grid_p1/p1_results.json"
e["harvest_note"] = (
    "R298 bm-a harvest: relaunch 06:10:01 autofill pid 18524 new sha 0cce3192 "
    "(crash-fuse cleared by sha change per O-0947; first burn 05:50 crashed at "
    "first cell KeyError st['sharpe_full'], fix 64023a42 R297) -> landed "
    "06:10:37 elapsed 28.8s workers 4 -> judged NEGATIVE 0/45 G1'v2 (best "
    "EW__DEDUP 0.5301 vs own-null line 1.7825, mu_null 0.4209; CI lower "
    "-0.3299) + 0/45 G2 (DSR 0.0, PBO 0.4857 observe) -> config-family "
    "no-increment verdict, slot closed no-reopen (new evidence = new prereg); "
    "prereg s7/s8 single-finalization + attrition row + post_review row "
    "registered same round; fill latency 29.9min > 10min target miss honest")
pool["updated_at"] = TS
with io.open(POOL, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(pool, fh, ensure_ascii=False, indent=1)
chk2 = json.load(io.open(POOL, encoding="utf-8-sig"))
ce = [x for x in chk2["entries"] if x.get("id") == "FUSION-GRID-P1"][0]
assert ce["status"] == "done" and ce["shards"][0]["status"] == "done"
print("pool: FUSION-GRID-P1 flipped done (live-read asserted before write)")

# ---------- 4) post_review criteria registration (dry-run verify first) ----------
def jf(path, dotted, want):
    x = json.load(io.open(path, encoding="utf-8"))
    for part in dotted.split("."):
        x = x[part]
    return str(x) == str(want), "%s=%s (want %s)" % (dotted, x, want)


def fe(path):
    return os.path.exists(path), "exists" if os.path.exists(path) else "ABSENT"


def fc(path, sub):
    return (sub in io.open(path, encoding="utf-8").read()), \
           ("contains" if sub in io.open(path, encoding="utf-8").read() else "MISSING: " + sub[:50])


CHECKS = [
    ("fe", ("scripts/fusion_grid_p1.py",)),
    ("fe", (P1,)),
    ("fe", ("results/fusion_grid_p1/nulls_summary.json",)),
    ("fe", ("results/fusion_grid_p1/regime_series.json",)),
    ("fe", (PR,)),
    ("jf", (P1, "batch", "FUSION_GRID_P1")),
    ("jf", (P1, "evidence_cutoff", "2026-09-22")),
    ("jf", (P1, "trials_ledger.prev_total", "200396")),
    ("jf", (P1, "trials_ledger.batch_trials", "2045")),
    ("jf", (P1, "trials_ledger.total", "202441")),
    ("jf", (P1, "skill_line.line", "1.7825")),
    ("jf", (P1, "skill_line.mu_null", "0.4209")),
    ("jf", (P1, "skill_line.sigma_null", "0.2754")),
    ("jf", (P1, "nulls.K", "2000")),
    ("jf", (P1, "nulls.coverage.n_values", "2000")),
    ("jf", (P1, "family_pbo.pbo", "0.4857")),
    ("jf", (P1, "cells.EW__DEDUP.sharpe_full", "0.5301")),
    ("jf", (P1, "cells.EW__DEDUP.g1_pass_v2", "False")),
    ("jf", (P1, "cells.EW__DEDUP.eligible_v2", "False")),
    ("jf", (P1, "cells.EW__ALL32.sharpe_full", "0.5237")),
    ("jf", (P1, "cells.EW__ALL32.g1_pass_v2", "False")),
    ("jf", (P1, "cells.INV_MDD__ALL32.sharpe_full", "0.4753")),
    ("jf", (P1, "cells.REGIME_COND__TOP2.sharpe_full", "0.0419")),
    ("jf", (P1, "audit.elapsed_sec", "28.8")),
    ("jf", (P1, "audit.workers", "4")),
    ("jf", (P1, "baselines_descriptive.ew48_passive.sharpe", "0.3792")),
    ("fc", (PR, "0/45 G1' 判负照报")),
    ("fc", (PR, "判负关槽")),
    ("fc", (ATT, "FUSION_GRID_P1")),
]
bad = []
for kind, args in CHECKS:
    fn = {"fe": fe, "jf": jf, "fc": fc}[kind]
    ok, detail = fn(*args)
    if not ok:
        bad.append((kind, args, detail))
if bad:
    for b in bad:
        print("DRY-RUN FAIL:", b)
    raise SystemExit("dry-run verification failed: %d checks" % len(bad))
print("dry-run: all %d checks verified as reviewer sees them" % len(CHECKS))

checks = []
for kind, args in CHECKS:
    if kind == "fe":
        checks.append({"kind": "file_exists", "args": list(args)})
    elif kind == "jf":
        checks.append({"kind": "json_field", "args": [args[0], args[1], str(args[2])]})
    elif kind == "fc":
        checks.append({"kind": "file_contains", "args": list(args)})

new_row = {
    "id": "T-85-FUSION-GRID-P1",
    "claim": (
        "T-85 s2/s3 FUSION_GRID_P1 (fusion-layer grid over 32 registered "
        "member NAVs, O-20260926-2320 24h-quench supply batch) full arc: "
        "prereg frozen commit 7cf87f13 R295 BEFORE runner build 95f4e95d "
        "R296 BEFORE any run (R99 law; seed fusion_grid_p1=20275200 "
        "registered at freeze, R250 one-step) -> first burn 05:50:01 pid "
        "20952 crashed at first cell job (KeyError st['sharpe_full'], "
        "zero judged products, engineering bug) -> fix 64023a42 R297 "
        "(sharpe_full key per frozen sec.4 full-window face + B7b "
        "consumed-key contract selftest leg, 23/23) -> relaunch 06:10:01 "
        "autofill pid 18524 new sha 0cce3192 (crash-fuse cleared by sha "
        "change per O-0947 fix-first law) -> landed 06:10:37 elapsed "
        "28.8s workers 4; fill latency 29.9min vs O-2100 10min target "
        "MISS honest (crash-diagnosis round consumed the window) -> "
        "JUDGED NEGATIVE per frozen sec.4: 0/45 G1'v2 (skill line "
        "1.7825 = null-term dominated, own-null pool mu 0.4209 / sigma "
        "0.2754 / K 2000; best cell EW__DEDUP 0.5301, bootstrap CI "
        "[-0.3299, 1.392] lower <= 0; all 45 line_ok=False) + 0/45 G2 "
        "(DSR best 0.0 vs sr_star 1.2511 @ n_trials 202441; family PBO "
        "0.4857 observe band > 0.25 gate) -> verdict semantics = grid "
        "config-family shows NO increment over random same-mask "
        "portfolios (random-config baseline itself ~0.42 Sharpe), "
        "member-alpha existence NOT falsified (sec.1 pre-embedded); "
        "descriptive face all-pass 45/45 (OOS dual positive, maxDD "
        "line, zero crash years) disclosed as non-binding; x2 stress "
        "face all 45 <= +0.0454 honest; regime exact face "
        "G754/Y714/R141/O22 zero-drift vs R296 gate (probe F4 approx "
        "face superseded per prereg sec.2 runner-exact clause); dedup "
        "disclosure 6/990 pairs >= 0.999 (cross-family same-subset "
        "mechanical twins, survivor face empty so no collapse); "
        "ledger 200396 + 2045 = 202441 single-count; s7/s8 "
        "single-finalization with 5-prediction reconciliation (P1 MISS "
        "diversification arithmetic; P2 HIT; P3 magnitude MISS premise "
        "face = approx regime shares falsified by exact v3 face "
        "ORANGE+RED 10% not 61%; P4 HIT; P5 no contradiction) -> "
        "fusion grid slot closed, no-reopen law, new evidence = new "
        "prereg; zero STRATEGY_LIBRARY entries, zero FUSION-* paper "
        "account proposals (sec.4 survivor face naturally empty)"),
    "claim_source": (
        "research/FUSION_GRID_P1_PREREG.md (frozen 7cf87f13, s7/s8 "
        "backfilled R298 single-finalization) + results/fusion_grid_p1/"
        "p1_results.json product + results/gate_attrition.json entries "
        "row FUSION_GRID_P1 + pool done-flip R298 (autofill relaunch "
        "trail 06:10:01) + ticket T-2026-09-26-85-P1 progress_r298"),
    "status": "closed",
    "checks": checks,
}
c = json.load(io.open(CRIT, encoding="utf-8"))
assert not any(x["id"] == new_row["id"] for x in c["items"]), "duplicate id"
c["items"].append(new_row)
with io.open(CRIT, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(c, fh, ensure_ascii=False, indent=1)
chk3 = json.load(io.open(CRIT, encoding="utf-8"))
assert chk3["items"][-1]["id"] == "T-85-FUSION-GRID-P1"
print("registered T-85-FUSION-GRID-P1 (items=%d, checks=%d)"
      % (len(chk3["items"]), len(checks)))
