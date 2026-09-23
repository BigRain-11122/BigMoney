"""SLEEVE_P3 admission decision -> one-shot verdict (pre-registered).

PRE-REGISTERED before running (research/SLEEVE_P3.md, written first).
Do NOT tune thresholds, switch carriers, or add schemes after seeing
results (p-hacking ban, BACKTEST_PLAN iron rule 3).

Question (round-17 pointer, strategy-line option): do the 6 NSP1
low-correlation sleeves (donchian_20_10 / double_bottom_20 /
price_volume_trend_20, both exit regimes; max|corr|<0.30 vs the 3
registered traders but near-zero standalone Sharpe and deeply negative
x2) improve the P3-validated 3-member portfolio enough to be admitted
as diversification material?

Fixed membership (no search):
  BASE = 3 registered traders (EW3 primary incumbent + IV3 secondary)
  A    = 3 members + all 6 sleeves = 9 (EW9 + IV9)
  B    = 3 members + 3 family representatives (per-signal higher
         recorded full Sharpe from NSP1: donchian_20_10@default,
         double_bottom_20@ce, price_volume_trend_20@ce) = 6 (EW6 + IV6)

Hard gates (batch void if any fails):
  1. patch self-test + 3 trader anchors (registered evidence + x2)
  2. 6 sleeve anchors vs NSP1 recorded cells (sharpe |d|<ANCHOR_TOL,
     x1 trades exact, x2 columns) -- sleeves rerun verbatim via
     new_signal_p1.run_cell, truncated at NSP1's recorded data_end
  3. BASE EW3/IV3 re-derivation must reproduce P3 recorded portfolios

Admission (EW family = pre-registered carrier; IV = secondary evidence
only, never the verdict, P3 precedent), per scheme X in {A-EW9, B-EW6}:
  c1  X.x1 full sharpe  > BASE-EW3 full + 0.05 (real margin, ~2 SE)
  c2  X.x1 oos sharpe   >= BASE-EW3 oos (no regime degradation)
  c3  X validated per P3 template (benefit>0 AND six G1' clauses AND
      worst year > -30%)
  c4  X.x2 survive (full > 0.4004 AND oos > 0)
  admitted <=> c1 AND c2 AND c3 AND c4.
sleeve_admission <=> A-EW9 or B-EW6 admitted (membership fixed
before the run; if both pass both are recorded).

No new signals, no parameter search -> random baselines not re-run
(P3 precedent, recorded constants); null = incumbent BASE + recorded
passive constants. Transparency handicap (all sleeve OOS already seen
in NSP1) is offset by the +0.05 hard margin and the no-degradation
clause, and is declared in the pre-registration.

Products: research/sleeve_p3_results.csv + results/sleeve_p3.json +
research/SLEEVE_P3.md sec.7 (appended after the run).
Trial ledger: cumulative from g2_nsp1.json (N=1043) + this batch
(pre-reg n=30: 18 engine runs + 12 derived portfolio evals) -> 1073.
"""
import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # sibling imports

import pandas as pd

from config import PATHS
from live.paper import (ANCHOR_TOL, OOS_START, build_panels, load_core,
                        self_test_patches, seg_metrics)
from firm.hr import TRADERS_DIR, load_trader
from p3_portfolio import (CRASH_YEAR, anchor_checks, combine, corr_block,
                          g1_clauses, iv_weights, member_run, yearly_returns)
from new_signal_p1 import build_entries, run_cell

SLEEVE_NAMES = ("donchian_20_10", "double_bottom_20", "price_volume_trend_20")
REGIMES = ("default", "ce")
# pre-registered family representatives (higher recorded NSP1 full sharpe)
FAMILY_REPS = [("donchian_20_10", "default"), ("double_bottom_20", "ce"),
               ("price_volume_trend_20", "ce")]
CMP_MARGIN = 0.05                      # pre-registered c1 margin (~2 SE)
TRIALS_PRIOR = "g2_nsp1.json"          # latest cumulative ledger
NSP1_RECORD = "new_signal_p1.json"
P3_RECORD = "p3_portfolio.json"


def load_constants() -> dict:
    with open(os.path.join(PATHS.results_dir, "p2_calibration.json"),
              encoding="utf-8") as fh:
        calib = json.load(fh)
    g = calib["g1_prime_gate"]
    with open(os.path.join(PATHS.results_dir, TRIALS_PRIOR),
              encoding="utf-8") as fh:
        prior = json.load(fh)
    with open(os.path.join(PATHS.results_dir, NSP1_RECORD),
              encoding="utf-8") as fh:
        nsp1 = json.load(fh)
    with open(os.path.join(PATHS.results_dir, P3_RECORD),
              encoding="utf-8") as fh:
        p3 = json.load(fh)
    return {
        "i_bar": g["i_full_sharpe_gt"], "vi_bar": g["vi_full_sharpe_gt"],
        "dd_min": g["iii_dd_min"], "trades_min": g["iv_trades_min"],
        "prior_ledger": prior["trials_ledger"],
        "prior_n": sum(x["n"] for x in prior["trials_ledger"]),
        "sleeve_cutoff": nsp1["universe"]["data_end"],   # 2026-09-22
        "nsp1_cells": {f"{c['name']}@{c['exit_regime']}": c
                       for c in nsp1["cells"] if c["status"] == "ok"},
        "p3_ports": p3["portfolios"],
    }


def sleeve_anchor(got: dict, rec: dict, got_x2: dict) -> dict:
    ok1 = (abs(got["full"]["sharpe"] - rec["full"]["sharpe"]) < ANCHOR_TOL
           and abs(got["oos"]["sharpe"] - rec["oos"]["sharpe"]) < ANCHOR_TOL
           and got["n_trades"] == rec["n_trades"])
    ok2 = (abs(got_x2["full"]["sharpe"] - rec["x2_full_sharpe"]) < ANCHOR_TOL
           and abs(got_x2["oos"]["sharpe"] - rec["x2_oos_sharpe"])
           < ANCHOR_TOL)
    return {"anchor_ok": bool(ok1), "x2_ok": bool(ok2),
            "got_full": got["full"]["sharpe"], "got_oos": got["oos"]["sharpe"],
            "got_trades": got["n_trades"],
            "rec_full": rec["full"]["sharpe"], "rec_oos": rec["oos"]["sharpe"],
            "rec_trades": rec["n_trades"],
            "got_x2_full": got_x2["full"]["sharpe"],
            "got_x2_oos": got_x2["oos"]["sharpe"],
            "rec_x2_full": rec["x2_full_sharpe"],
            "rec_x2_oos": rec["x2_oos_sharpe"]}


def eval_scheme(name: str, kind: str, tids: list, sleeves: dict, K: dict):
    """Combine one membership set under EW or IV; x1 + x2 evals."""
    eqs1 = {tid: sleeves[tid]["x1"]["eq"] for tid in tids}
    eqs2 = {tid: sleeves[tid]["x2"]["eq"] for tid in tids}
    rets = pd.concat({tid: eqs1[tid] / eqs1[tid].iloc[0] for tid in tids},
                     axis=1, join="inner").dropna().pct_change().dropna()
    if kind == "EW":
        w = {tid: round(1.0 / len(tids), 6) for tid in tids}
    else:
        w = iv_weights(rets)
    out = {"scheme": name, "kind": kind, "members": tids, "weights": w}
    for mult, key in ((1, "x1"), (2, "x2")):
        eqs = eqs1 if mult == 1 else eqs2
        eq = combine(eqs, w)
        full = seg_metrics(eq)
        oos = seg_metrics(eq, OOS_START)
        n_tr = sum(sleeves[tid][key]["n_trades"] for tid in tids)
        yr = yearly_returns(eq)
        out[key] = {"full": full, "oos": oos, "n_trades": n_tr,
                    "yearly": yr, "worst_year": min(yr.values())}
    p1 = out["x1"]
    member_s = {tid: sleeves[tid]["x1"]["full"]["sharpe"] for tid in tids}
    w_mean = sum(w[tid] * member_s[tid] for tid in tids)
    p1["clauses"] = g1_clauses(p1, p1["n_trades"], K)
    p1["member_sharpes"] = member_s
    p1["weighted_mean_member_sharpe"] = round(w_mean, 4)
    p1["benefit"] = round(p1["full"]["sharpe"] - w_mean, 4)
    p1["dr"] = round(p1["full"]["sharpe"] / w_mean, 4) if w_mean else None
    p2 = out["x2"]
    p1["x2_survive"] = bool(p2["full"]["sharpe"] > K["vi_bar"]
                            and p2["oos"]["sharpe"] > 0)
    p1["validated"] = bool(p1["benefit"] > 0 and all(p1["clauses"].values())
                           and p1["worst_year"] > CRASH_YEAR)
    return out


def main():
    t0 = time.time()
    if not self_test_patches():
        print("patch self-test FAILED -- abort (fake-evidence guard)")
        return 2
    print("patch self-tests: PASS")

    K = load_constants()
    print(f"constants: i>{K['i_bar']} vi>{K['vi_bar']} "
          f"prior_N={K['prior_n']} sleeve_cutoff={K['sleeve_cutoff']}")

    prices_full = load_core()
    members = [p.stem for p in sorted(TRADERS_DIR.glob("*.json"))
               if not p.name.startswith("_")]
    traders = {tid: load_trader(tid) for tid in members}
    print(f"members: {members}")

    # ---------- member runs (anchor-cum-sleeve, P3 code path) ----------
    sleeves = {}
    anchors = {}
    for tid in members:
        r1 = member_run(traders[tid], prices_full, None)
        r2 = member_run(traders[tid], prices_full, cost_mult=2)
        a = anchor_checks(traders[tid], r1, r2)
        anchors[tid] = a
        sleeves[tid] = {"x1": r1, "x2": r2}
        print(f"  {tid:<16} x1 full_s={r1['full']['sharpe']:>7.4f} "
              f"| x2 full_s={r2['full']['sharpe']:>7.4f} "
              f"anchor={'OK' if a['anchor_ok'] else 'BROKEN'} "
              f"x2={'OK' if a['x2_ok'] else 'BROKEN'}")
    if not all(a["anchor_ok"] and a["x2_ok"] for a in anchors.values()):
        print("MEMBER ANCHOR BROKEN -- batch void")
        return write_outputs(K, members, sleeves, anchors, None, None,
                             None, None, None, t0, void=True)

    # ---------- sleeve runs (NSP1 code path, truncated at record end) --
    ps = pd.Timestamp(K["sleeve_cutoff"])
    prices_trunc = {s: df[df.index <= ps] for s, df in prices_full.items()}
    P = build_panels(prices_trunc)
    idx = P["close"].index
    entries = {e[0]: e for e in build_entries(P)}
    sleeve_ids = [f"{n}@{r}" for n in SLEEVE_NAMES for r in REGIMES]
    sleeve_anchors = {}
    for sid in sleeve_ids:
        name, regime = sid.split("@")
        ce = regime == "ce"
        _, _, params, entry, exit_, _ = entries[name]
        r1 = run_cell(prices_trunc, idx, entry, exit_, params, ce)
        r2 = run_cell(prices_trunc, idx, entry, exit_, params, ce, cost_mult=2)
        rec = K["nsp1_cells"][sid]
        a = sleeve_anchor(r1, rec, r2)
        sleeve_anchors[sid] = a
        sleeves[sid] = {"x1": r1, "x2": r2}
        print(f"  {sid:<28} x1 full_s={r1['full']['sharpe']:>7.4f} "
              f"(rec {rec['full']['sharpe']}) "
              f"| x2 full_s={r2['full']['sharpe']:>7.4f} "
              f"(rec {rec['x2_full_sharpe']}) "
              f"anchor={'OK' if a['anchor_ok'] else 'BROKEN'} "
              f"x2={'OK' if a['x2_ok'] else 'BROKEN'}")
    if not all(a["anchor_ok"] and a["x2_ok"] for a in sleeve_anchors.values()):
        print("SLEEVE ANCHOR BROKEN -- batch void")
        return write_outputs(K, members, sleeves, anchors, sleeve_anchors,
                            None, None, None, None, t0, void=True)

    # ---------- schemes ----------
    reps = [f"{n}@{r}" for n, r in FAMILY_REPS]
    sets = {"BASE": members, "A": members + sleeve_ids, "B": members + reps}
    schemes = []
    for set_name, tids in sets.items():
        for kind in ("EW", "IV"):
            s = eval_scheme(f"{set_name}-{kind}{len(tids)}", kind, tids,
                            sleeves, K)
            schemes.append(s)
            p1, p2 = s["x1"], s["x2"]
            print(f"  {s['scheme']:<10} x1 full_s={p1['full']['sharpe']:>7.4f} "
                  f"oos_s={p1['oos']['sharpe']:>7.4f} "
                  f"benefit={p1['benefit']:>7.4f} DR={p1['dr']} "
                  f"worst={p1['worst_year']} "
                  f"| x2 full_s={p2['full']['sharpe']:>7.4f} "
                  f"validated={p1['validated']}")

    # ---------- BASE reproduction hard gate ----------
    base_repro = {}
    for sch, rec_key, fields in (("BASE-EW3", "EW_x1", ("full", "oos")),
                                 ("BASE-EW3", "EW_x2", ("full", "oos")),
                                 ("BASE-IV3", "IV_x1", ("full", "oos")),
                                 ("BASE-IV3", "IV_x2", ("full", "oos"))):
        s = next(x for x in schemes if x["scheme"] == sch)
        key = "x1" if rec_key.endswith("x1") else "x2"
        rec = K["p3_ports"][rec_key]
        for f in fields:
            got = s[key][f]["sharpe"]
            want = rec[f]["sharpe"]
            ok = abs(got - want) < ANCHOR_TOL
            base_repro[f"{sch}:{key}:{f}"] = {"got": got, "want": want,
                                              "ok": bool(ok)}
            if not ok:
                print(f"BASE repro BROKEN: {sch} {key} {f} "
                      f"got={got} want={want}")
    base_ok = all(v["ok"] for v in base_repro.values())
    print(f"BASE reproduction vs P3 record: "
          f"{'OK' if base_ok else 'BROKEN'} ({len(base_repro)} fields)")
    if not base_ok:
        return write_outputs(K, members, sleeves, anchors, sleeve_anchors,
                             schemes, base_repro, None, None, t0, void=True)

    # ---------- correlations (9 curves, informational) ----------
    tids9 = members + sleeve_ids
    norm1 = pd.concat({tid: sleeves[tid]["x1"]["eq"] /
                       sleeves[tid]["x1"]["eq"].iloc[0] for tid in tids9},
                      axis=1, join="inner").dropna()
    rets9 = norm1.pct_change().dropna()
    oos_mask = rets9.index >= pd.Timestamp(OOS_START)
    corr = {"full": corr_block(rets9), "is": corr_block(rets9, ~oos_mask),
            "oos": corr_block(rets9, oos_mask)}
    print(f"corr 9-curve: full avg={corr['full']['avg_pairwise']} "
          f"(band {corr['full']['band']}), oos avg="
          f"{corr['oos']['avg_pairwise']}")

    # ---------- admission clauses (EW carrier only) ----------
    base_ew = next(s for s in schemes if s["scheme"] == "BASE-EW3")
    b_full = base_ew["x1"]["full"]["sharpe"]
    b_oos = base_ew["x1"]["oos"]["sharpe"]
    admission = {}
    for sch_name in ("A-EW9", "B-EW6"):
        s = next(x for x in schemes if x["scheme"] == sch_name)
        p1 = s["x1"]
        c1 = bool(p1["full"]["sharpe"] > b_full + CMP_MARGIN)
        c2 = bool(p1["oos"]["sharpe"] >= b_oos)
        c3 = bool(p1["validated"])
        c4 = bool(p1["x2_survive"])
        admission[sch_name] = {
            "c1_beat_base_by_margin": c1, "c2_oos_no_degrade": c2,
            "c3_validated_p3_template": c3, "c4_x2_survive": c4,
            "got_full": p1["full"]["sharpe"], "need_full": b_full + CMP_MARGIN,
            "got_oos": p1["oos"]["sharpe"], "need_oos": b_oos,
            "admitted": bool(c1 and c2 and c3 and c4)}
        print(f"  {sch_name}: c1={c1} c2={c2} c3={c3} c4={c4} "
              f"-> admitted={admission[sch_name]['admitted']} "
              f"(need full>{b_full + CMP_MARGIN:.4f}, got "
              f"{p1['full']['sharpe']:.4f}; need oos>={b_oos:.4f}, got "
              f"{p1['oos']['sharpe']:.4f})")
    sleeve_admission = bool(any(v["admitted"] for v in admission.values()))
    print(f"\n===== SLEEVE admission: {sleeve_admission} =====")

    return write_outputs(K, members, sleeves, anchors, sleeve_anchors,
                         schemes, base_repro, corr, admission, t0,
                         void=False)


def write_outputs(K, members, sleeves, anchors, sleeve_anchors, schemes,
                  base_repro, corr, admission, t0, void=False):
    n_engine = 0 if sleeves is None else 2 * len(sleeves)
    n_evals = 0 if schemes is None else 2 * len(schemes)
    ledger = list(K["prior_ledger"]) + [{
        "batch": "SLEEVE-P3-admission", "n": n_engine + n_evals,
        "note": f"{n_engine} engine runs (3 members x2 anchor-cum-sleeve + "
                f"6 sleeves x2 NSP1-record anchor) + {n_evals} portfolio "
                f"evaluations (derived, non-engine); pre-registered n=30 "
                f"(research/SLEEVE_P3.md sec.4)"}]

    # ---------- CSV ----------
    rows = []
    for tid, a in anchors.items():
        for mult, key in ((1, "x1"), (2, "x2")):
            r = sleeves[tid][key]
            rows.append({"kind": "member", "id": tid, "scheme": "",
                         "cost_mult": mult, "weights": "",
                         "full_sharpe": r["full"]["sharpe"],
                         "full_ann": r["full"]["annual_return"],
                         "full_dd": r["full"]["max_drawdown"],
                         "n_trades": r["n_trades"],
                         "oos_sharpe": r["oos"]["sharpe"],
                         "oos_ann": r["oos"]["annual_return"],
                         "benefit": "", "dr": "", "worst_year": "",
                         "validated": "", "x2_survive": "",
                         "c1": "", "c2": "", "c4": "", "admitted": "",
                         "anchor_ok": a["anchor_ok"] if mult == 1
                         else a["x2_ok"]})
    if sleeve_anchors:
        for sid, a in sleeve_anchors.items():
            for mult, key in ((1, "x1"), (2, "x2")):
                r = sleeves[sid][key]
                rows.append({"kind": "sleeve", "id": sid, "scheme": "",
                             "cost_mult": mult, "weights": "",
                             "full_sharpe": r["full"]["sharpe"],
                             "full_ann": r["full"]["annual_return"],
                             "full_dd": r["full"]["max_drawdown"],
                             "n_trades": r["n_trades"],
                             "oos_sharpe": r["oos"]["sharpe"],
                             "oos_ann": r["oos"]["annual_return"],
                             "benefit": "", "dr": "", "worst_year": "",
                             "validated": "", "x2_survive": "",
                             "c1": "", "c2": "", "c4": "", "admitted": "",
                             "anchor_ok": a["anchor_ok"] if mult == 1
                             else a["x2_ok"]})
    if schemes:
        for s in schemes:
            for mult, key in ((1, "x1"), (2, "x2")):
                p = s[key]
                rows.append({"kind": "portfolio", "id": s["scheme"],
                             "scheme": s["scheme"], "cost_mult": mult,
                             "weights": json.dumps(s["weights"]),
                             "full_sharpe": p["full"]["sharpe"],
                             "full_ann": p["full"]["annual_return"],
                             "full_dd": p["full"]["max_drawdown"],
                             "n_trades": p["n_trades"],
                             "oos_sharpe": p["oos"]["sharpe"],
                             "oos_ann": p["oos"]["annual_return"],
                             "benefit": p.get("benefit", ""),
                             "dr": p.get("dr", ""),
                             "worst_year": p["worst_year"],
                             "validated": p.get("validated", ""),
                             "x2_survive": p.get("x2_survive", ""),
                             "c1": "", "c2": "", "c4": "",
                             "admitted": admission.get(s["scheme"], {})
                             .get("admitted", "") if mult == 1 else "",
                             "anchor_ok": ""})
    csv_path = os.path.join(PATHS.root, "research", "sleeve_p3_results.csv")
    cols = ["kind", "id", "scheme", "cost_mult", "weights", "full_sharpe",
            "full_ann", "full_dd", "n_trades", "oos_sharpe", "oos_ann",
            "benefit", "dr", "worst_year", "validated", "x2_survive",
            "c1", "c2", "c4", "admitted", "anchor_ok"]
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            w.writerow([r.get(c, "") for c in cols])
    print(f"saved: {csv_path} ({len(rows)} rows)")

    # ---------- JSON ----------
    sleeve_admission = None
    if admission is not None:
        sleeve_admission = bool(any(v["admitted"]
                                    for v in admission.values()))
    out = {
        "batch": "SLEEVE-P3-admission",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc": "research/SLEEVE_P3.md (written before run)",
        "universe": {"pool": "core48-bare-codes",
                     "member_cutoff": "registered evidence_cutoff",
                     "sleeve_cutoff": K["sleeve_cutoff"],
                     "oos_start": OOS_START},
        "void": void,
        "constants": {
            "g1_prime_i_bar": K["i_bar"], "g1_prime_vi_bar": K["vi_bar"],
            "cmp_margin": CMP_MARGIN, "crash_year": CRASH_YEAR,
            "family_reps": [f"{n}@{r}" for n, r in FAMILY_REPS],
            "note": "recorded constants rule (J19); random baselines not "
                    "re-run (P3 precedent: composition batch, zero new "
                    "search); null = incumbent BASE + recorded passive"},
        "family_reps_rule": "per-signal higher recorded NSP1 full sharpe, "
                            "fixed before this batch ran",
        "anchors": {"members": anchors,
                    "sleeves_vs_nsp1": sleeve_anchors,
                    "base_vs_p3": base_repro},
        "correlation_9curve": corr,
        "schemes": {s["scheme"]: {
            "kind": s["kind"], "members": s["members"],
            "weights": s["weights"],
            "x1": {k: v for k, v in s["x1"].items()},
            "x2": {k: (v if not isinstance(v, dict) else
                       {kk: vv for kk, vv in v.items() if kk != "yearly"})
                   for k, v in s["x2"].items()},
        } for s in (schemes or [])},
        "admission_clauses": admission,
        "verdict": {
            "template": "SLEEVE admission one-shot (EW carrier; IV = "
                        "secondary evidence only)",
            "void": void,
            "sleeve_admission": sleeve_admission,
            "admitted_schemes": None if admission is None else
            [k for k, v in admission.items() if v["admitted"]],
            "fail_branch": None if (void or (sleeve_admission
                                              is not None and
                                              sleeve_admission)) else
            "no scheme admitted: sleeves archived as material with real "
            "variance-reduction but insufficient alpha vs the incumbent; "
            "NO scheme/weight/member retries (p-hacking ban); core48 "
            "in-pool diversification material exhausted -- next material "
            "must come from outside the pool (cash-leg engine feature = "
            "user-side decision; pool expansion naming audit = J9 data "
            "source, outside this node's mandate), both via new "
            "pre-registration",
        },
        "trials_ledger": ledger,
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": n_engine, "n_portfolio_evals": n_evals,
                  "workers": 1, "cpu_parallel": "serial (single-process)"},
    }
    # yearly dicts are large-ish; keep them (audit value) but shorten keys
    json_path = os.path.join(PATHS.results_dir, "sleeve_p3.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
    print(f"saved: {json_path}")

    if void:
        summary = "VOID (anchor broken)"
    else:
        summary = f"sleeve_admission={sleeve_admission}"
    print(f"\n===== SLEEVE_P3 verdict: {summary} =====")
    print(f"engine runs={n_engine} evals={n_evals} "
          f"elapsed={time.time()-t0:.0f}s "
          f"ledger N={sum(x['n'] for x in ledger)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
