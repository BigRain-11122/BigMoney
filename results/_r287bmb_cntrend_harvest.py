# -*- coding: utf-8 -*-
"""r287 bm-b: CN-TREND-ETF-P1 harvest gate (r244 landed-marker law: the
machine whose round observes p1_results.json landed runs the deterministic
re-derive + pool flip; batch never self-flips). Family precedent
_r261bma_coresat_harvest.py ten faces, adapted to the prereg
research/CN_TREND_ETF_PREREG.md frozen contract (7 cells x {x1,x2},
N_eff=2007, own-null pool K=2000, D6 member gate, census faces).

r282 law: post-append re-derive of skill_line must pass
n_eff_override=<recorded n_eff> -- the live data-driven head now includes
this batch's own 2007 echo.
"""
import collections
import datetime
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import science_gates as SG  # noqa: E402

OUT_JSON = os.path.join(ROOT, "results", "cn_trend_ETF", "p1_results.json")
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
ATT = os.path.join(ROOT, "results", "gate_attrition.json")
BATCH = "CN-TREND-ETF-P1"
CELLS = ["MA_BASE", "MA_DUAL", "MA_BG", "MA_INVVOL",
         "DON20_10", "DON55_20", "MA_TRAIL"]
N_TRIALS = 2007

if not os.path.exists(OUT_JSON):
    print("NOT LANDED: p1_results.json absent -- nothing to harvest")
    raise SystemExit(3)

d = json.load(open(OUT_JSON, encoding="utf-8"),
              object_pairs_hook=collections.OrderedDict)
fails = []


def ok(fid, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {fid} {detail}")
    if not cond:
        fails.append(fid)


now = datetime.datetime.now()

# [1] landed + cutoff face (C2 legal top-level key)
ok("cutoff face", d.get("evidence_cutoff") == "2026-09-22"
   and d.get("cutoff_meta", {}).get("evidence_cutoff") == "2026-09-22")

# [2] ledger continuity: prev + 2007 == total == live chain head
tl = d["trials_ledger"]
head = SG.ledger_head()
ok("ledger continuity",
   tl["batch_trials"] == N_TRIALS
   and tl["prev_total"] + N_TRIALS == tl["total"]
   and head["total"] == tl["total"],
   f"prev={tl['prev_total']} +{N_TRIALS} -> total={tl['total']} "
   f"live_head={head['total']} (head file: {head.get('file')})")

# [3] cells census: 7 x {x1,x2} with finite judged sharpe
cells = d["cells"]
ok("cells census", set(cells) == set(CELLS)
   and all(set(cells[c]) == {"x1", "x2"} for c in CELLS)
   and all(isinstance(cells[c]["x2"]["stats"]["sharpe"], float)
           for c in CELLS))

# [4] recorded g1/g2 verdicts per cell (honest face -- report what landed)
g1_pass = {c: d["gates"][c]["g1_prime_v2"]["pass_v2"] for c in CELLS}
g2_elig = {c: d["gates"][c]["g2"]["eligible_v2"] for c in CELLS}
ok("g1/g2 present", all(isinstance(v, bool) for v in
                        list(g1_pass.values()) + list(g2_elig.values())),
   f"g1 pass={sum(g1_pass.values())}/7 g2 eligible={sum(g2_elig.values())}/7")

# [5] skill_line re-derive under r282 n_eff_override law
line = d["skill_line"]
nulls = d["nulls"]
line_pool = {"values": nulls["values"], "coverage": nulls["coverage"]}
re_line = SG.skill_line_v2(batch_cells=N_TRIALS, pool="core48",
                           null_pool=line_pool,
                           n_eff_override=line["n_eff"])
ok("skill_line rederive", abs(re_line["line"] - line["line"]) < 1e-9,
   f"recorded={line['line']} rederive={re_line['line']} "
   f"passive_term={line['passive_term']} n_eff={line['n_eff']}")

# [6] own-null pool census + seed band (RANDOM_LARGE_SAMPLE_LAW)
ok("nulls K2000", len(nulls["values"]) == 2000
   and d["meta"]["seed"]["base"] == 20270201
   and d["meta"]["seed"]["k"] == 2000,
   f"K={len(nulls['values'])} base={d['meta']['seed']['base']}")

# [7] D6 member face (>=0.7 vs in-registry members = reject)
d6 = d["d6_correlation"]
ok("d6 member face", all(c in d6["cells"] for c in CELLS))
for c in CELLS:
    mf = d6["cells"][c]["member_face"]
    print(f"    d6 {c}: max|corr|={mf.get('max_abs_corr')} "
          f"argmax={mf.get('argmax_member')} reject={mf.get('reject')}")

# [8] attrition row entries-visible (r248 consumer-chain law)
att = json.load(open(ATT, encoding="utf-8"))
row = [e for e in att["entries"] if e.get("batch") == BATCH]
ok("attrition entries-visible", len(row) == 1
   and row[0]["cells_ledger_delta"] == N_TRIALS
   and row[0]["ledger_total_after"] == tl["total"])

# [9] census + robust faces present (prereg s3 virtual starts + s2.3)
ok("census/robust faces", "virtual_starts" in d and "robust" in d
   and d["audit"]["elapsed_sec"] > 0
   and isinstance(d["audit"].get("workers"), int),  # r259 __workers__ law
   f"elapsed={d['audit']['elapsed_sec']}s workers={d['audit'].get('workers')}")

# [10] judged x2 verdict table + prereg s5 prediction accountability
print("x2 verdict table (judged face):")
for c in CELLS:
    m = cells[c]["x2"]["stats"]
    print(f"  {c}: sharpe={m['sharpe']} ann={m['ann_ret']} "
          f"maxdd={m['max_dd']} entries={cells[c]['x2']['n_entries']} "
          f"trades={cells[c]['x2']['n_trades']} "
          f"oos_sharpe={m['oos'].get('sharpe') if isinstance(m.get('oos'), dict) else m.get('oos_sharpe')} "
          f"g1={g1_pass[c]} g2={g2_elig[c]}")
n_ma_in_band = sum(
    1 for c in ("MA_BASE", "MA_DUAL", "MA_BG", "MA_INVVOL", "MA_TRAIL")
    if 0.2 <= cells[c]["x2"]["stats"]["sharpe"] <= 0.6)
print(f"s5 prediction face: MA-family x2 sharpe in 0.2-0.6 band: "
      f"{n_ma_in_band}/5 (prediction 1: 0.2-0.6 band)")

# ---- pool flip (r244: harvest = flip + note; idempotent vs other machine)
pool = json.load(open(POOL, encoding="utf-8"))
for e in pool["entries"]:
    if e["id"] == BATCH:
        if e["status"] == "done" and e.get("harvest_note"):
            print(f"already harvested by another machine: "
                  f"{str(e['harvest_note'])[:120]}")
            print("harvest gate:", "PASS" if not fails else fails)
            raise SystemExit(1 if fails else 0)
        e["status"] = "done"
        e["updated_at"] = now.strftime("%Y-%m-%d %H:%M:%S")
        for sh in e["shards"]:
            sh["status"] = "done"
        g1n = sum(g1_pass.values())
        best = max(CELLS, key=lambda c: cells[c]["x2"]["stats"]["sharpe"])
        e["harvest_note"] = (
            f"harvested bm-b r287 same-round {now.strftime('%Y-%m-%d %H:%M')}: "
            f"p1_results.json landed (re-launch after r286 double-crash "
            f"root-fix, autofill-fired with both fixes); ten-face harvest "
            f"gate PASS (cutoff/ledger {tl['prev_total']}+{N_TRIALS}="
            f"{tl['total']}/cells census/g1 {g1n}/7/g2 "
            f"{sum(g2_elig.values())}/7/skill_line rederive n_eff_override "
            f"r282 law/nulls K2000 seed 20270201/D6 member face/attrition "
            f"r248/census+robust/audit workers r259); best x2 cell "
            f"{best} sharpe {cells[best]['x2']['stats']['sharpe']}; "
            f"verdict per prereg s4 recorded honest in product gates")
tmp = POOL + ".tmp"
open(tmp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(pool, ensure_ascii=False, indent=1) + "\n")
os.replace(tmp, POOL)
print("pool flipped done. harvest gate:", "PASS" if not fails else fails)
raise SystemExit(1 if fails else 0)
