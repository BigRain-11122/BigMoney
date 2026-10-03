"""r633 bm-a: fund-trio finalize REHEARSAL (import-only, zero runner-code touch).

Mirrors each runner's cmd_finalize call order with REAL current data to
surface path bugs BEFORE bm-b NULLS K=2000 lands (finalize window <=10-09
open). Output = rehearsal reports, NOT verdicts: nulls are partial
(<2000) so every nulls-dependent readout is invalid by construction and
flagged as such. Verdict-scale legs exercised for MECHANICS only:
g1_prime_v2/g2_registration_v2/M1/DSR/PBO/G-SEG/passive/block-bootstrap/
sign-flip/law-A exit census/cutoff_meta/append_ledger signature.

Usage: python results/_r633bma_finalize_rehearsal.py [--fam fund_quality_p1]
"""
import importlib.util
import inspect
import json
import os
import sys
import time
import traceback

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

FAMS = [
    ("fund_quality_p1", "scripts/fund_quality_p1.py"),
    ("fund_value_p1", "scripts/fund_value_p1.py"),
    ("fund_divlowvol_p1", "scripts/fund_divlowvol_p1.py"),
]


def load_mod(key, path):
    name = "reh_" + key
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def slim(x, depth=0):
    """Keep report payloads light: drop long lists/arrays, keep structure."""
    if isinstance(x, dict):
        return {str(k): slim(v, depth + 1) for k, v in x.items()
                if k != "_cont"}
    if isinstance(x, (list, tuple)):
        if len(x) > 12:
            return {"__len__": len(x), "head": [slim(v, depth + 1) for v in x[:3]]}
        return [slim(v, depth + 1) for v in x]
    if isinstance(x, (np.floating, np.integer)):
        return float(x)
    if isinstance(x, (np.ndarray, pd.Series)):
        return {"__ndarray__": True, "len": int(len(x))}
    return x


def rehearse(key, path):
    t_start = time.time()
    m = load_mod(key, path)
    legs = {}

    def leg(name, fn):
        t0 = time.time()
        try:
            v = fn()
            legs[name] = {"ok": True, "elapsed_sec": round(time.time() - t0, 1),
                          "value": v}
            return v
        except Exception as e:
            legs[name] = {"ok": False, "elapsed_sec": round(time.time() - t0, 1),
                          "error": f"{type(e).__name__}: {e}",
                          "tb_tail": traceback.format_exc().splitlines()[-3:]}
            return None

    # -- 1. input parse (schema face) --------------------------------------
    def _inputs():
        probe = json.load(open(m.PROBE_JSON, encoding="utf-8"))
        d6 = json.load(open(m.D6_JSON, encoding="utf-8"))
        cont = {}
        for c in m.CELLS:
            for f in m.FACES:
                p = os.path.join(m.OUT_DIR, f"cont_{c}_{f}.json")
                cont[(c, f)] = json.load(open(p, encoding="utf-8"))
        n_sens = sum(1 for ln in open(m._shard_files(kind="sens"),
                                      encoding="utf-8") if ln.strip())
        n_nulls = sum(1 for ln in open(m._shard_files(kind="nulls"),
                                       encoding="utf-8") if ln.strip())
        shard_rows = {}
        for c in m.CELLS:
            for f in m.FACES:
                shard_rows[f"{c}|{f}"] = sum(
                    1 for ln in open(m._shard_files(cell=c, face=f),
                                     encoding="utf-8") if ln.strip())
        return {"probe_keys": sorted(probe.keys())[:10],
                "d6_keys": sorted(d6.keys()),
                "cont_keys": {f"{c}|{f}": sorted(cont[(c, f)].keys())
                              for c in m.CELLS for f in m.FACES},
                "n_sens": n_sens, "n_nulls": n_nulls,
                "cell_shard_rows": shard_rows,
                "_cont": cont}
    inp = leg("inputs_parse", _inputs)
    cont = (inp or {}).get("_cont") or {}
    n_nulls = (inp or {}).get("n_nulls", -1)

    # -- 2. worker init + firing months (panel load face) ------------------
    leg("worker_init", lambda: bool(m._init_worker()) or True)
    leg("firing_months", lambda: bool(m._firing_months()) or True)

    # -- 3. passive face (mirror cmd_finalize) ------------------------------
    def _passive():
        lo = m._G["_t0_pos"]
        hi = len(m._G["idx"]) - 1
        rel = m._passive_window(lo, hi)
        pc = rel.pct_change().dropna()
        sh = float((pc.mean() / pc.std(ddof=1)) * np.sqrt(252))
        return {"n_members_t0": int(rel.count()) if hasattr(rel, "count") else None,
                "sharpe_full": round(sh, 6),
                "ret_full": round(float(rel.iloc[-1] - 1), 6),
                "span": [str(m._G["idx"][lo].date()),
                         str(m._G["idx"][hi].date())]}
    passive = leg("passive_face", _passive)

    # -- 4. headline legs: bootstrap / sign-flip ----------------------------
    h = cont.get((m.HEADLINE, "x1"))
    h_rets = pd.Series(h["returns"]) if h and "returns" in h else None
    if h_rets is not None:
        leg("block_bootstrap", lambda: m._block_bootstrap_sharpe(h_rets))
        leg("sign_flip", lambda: m._sign_flip_perm(h_rets))
    else:
        legs["headline_returns"] = {"ok": False, "elapsed_sec": 0.0,
                                    "error": "headline x1 cont returns missing"}

    # -- 5. nulls partial stats (REHEARSAL face, never a verdict input) -----
    def _nulls():
        rows = [json.loads(ln) for ln in open(m._shard_files(kind="nulls"),
                                              encoding="utf-8") if ln.strip()]
        vals = [r["sharpe"] for r in rows]
        return {"k": len(vals), "want": m.K_NULLS,
                "mu": round(float(np.mean(vals)), 4),
                "sigma": round(float(np.std(vals, ddof=1)), 4)}
    nstats = leg("nulls_partial_stats", _nulls)

    # -- 6. gate mechanics (partial nulls; readouts invalid by design) ------
    if h and h_rets is not None and passive and nstats and n_nulls < m.K_NULLS:
        def _gates():
            pool = {"coverage": {"mu": nstats["mu"], "sigma": nstats["sigma"],
                                 "n_values": nstats["k"]},
                    "source": f"REHEARSAL partial {nstats['k']}/{m.K_NULLS}"}
            g1 = m.g1_prime_v2(sharpe_full=h["sharpe_full"], returns=h_rets,
                               batch_cells=m.BATCH_CELLS, pool="core48",
                               n_trades=h["n_trades"],
                               n_entries=h["n_entries"],
                               null_pool=pool,
                               passive_override=passive["sharpe_full"])
            x2 = cont[(m.HEADLINE, "x2")]
            tstat = m.t_from_sharpe(h["sharpe_full"], len(h_rets))
            m1 = m.m1_t_value_gate(tstat, claim_class="new_strategy")
            dsr = m.deflated_sharpe_ratio(h_rets, n_trials=m.BATCH_CELLS)
            mat = pd.DataFrame(
                {f"{c}|{f}": pd.Series(cont[(c, f)]["returns"])
                 for c in m.CELLS for f in m.FACES}).dropna()
            from screening.pbo import cscv_pbo, pbo_verdict
            rec = cscv_pbo(mat)
            pbo = float(rec["pbo"])
            band = pbo_verdict(pbo)
            g2 = m.g2_registration_v2(g1.get("pass"), dsr.get("dsr", dsr), pbo)
            return {"g1_prime_mechanics": g1,
                    "x2_survival": {"sharpe_full": x2["sharpe_full"],
                                    "pass": bool(x2["sharpe_full"] > 0)},
                    "m1": m1, "dsr": dsr,
                    "pbo": {"pbo": round(pbo, 4), "band": band,
                            "cscv_n": int(rec.get("n", len(mat)))},
                    "g2_mechanics": g2}
        leg("gate_mechanics_partial_nulls", _gates)
    else:
        legs["gate_mechanics_partial_nulls"] = {
            "ok": False, "elapsed_sec": 0.0,
            "error": "prerequisites missing: "
                     + json.dumps({"headline": bool(h),
                                   "h_rets": h_rets is not None,
                                   "passive": bool(passive),
                                   "nstats": bool(nstats),
                                   "nulls_lt_want": n_nulls < m.K_NULLS})}

    # -- 7. G-SEG coverage (real face, nulls-independent) ------------------
    def _gseg():
        rows = m._read_cells(m.HEADLINE, "x1") or []
        full = [r for r in rows if not r.get("partial_12m")]
        cnt = {}
        for r in full:
            cnt[r.get("regime", "na")] = cnt.get(r.get("regime", "na"), 0) + 1
        return {"n_full_starts": len(full), "coverage": cnt,
                "pass": all(cnt.get(reg, 0) >= 50
                            for reg in ("bear", "bull", "chop"))}
    leg("g_seg", _gseg)

    # -- 8. per-start 12m dist + rolling worst + crash years ---------------
    if h_rets is not None:
        def _dist():
            rows = m._read_cells(m.HEADLINE, "x1") or []
            full = [r for r in rows if not r.get("partial_12m")]
            r12 = sorted(r["ret_12m"] for r in full)
            if not r12:
                return {"n": 0}
            def pct(q):
                return round(float(np.percentile(r12, q)), 4)
            hret = h_rets
            rw = {}
            for yrs, bars in (("3y", 756), ("5y", 1260), ("10y", 2520)):
                if len(hret) >= bars:
                    roll = (1 + hret).rolling(bars).apply(np.prod, raw=True) - 1
                    rw[yrs] = round(float(roll.min()), 4)
                else:
                    rw[yrs] = None
            lo = m._G["_t0_pos"]
            hidx = m._G["idx"][lo + 1:lo + 1 + len(hret)]
            if len(hidx) == len(hret):
                cy = (1 + hret).groupby(hidx.year).apply(
                    lambda x: float(x.prod() - 1))
            else:
                cy = pd.Series(dtype=float)
            crash = {int(y): round(v, 4) for y, v in cy.items() if v <= -0.35}
            return {"n": len(r12), "best": pct(100), "worst": pct(0),
                    "p25": pct(25), "median": pct(50), "p75": pct(75),
                    "positive_share": round(
                        sum(1 for v in r12 if v > 0) / len(r12), 4),
                    "rolling_worst": rw,
                    "crash_years_lte_-35pct": crash}
        leg("starts_12m_dist_and_rolling", _dist)

    # -- 9. sensitivity aggregation (real, complete face) ------------------
    def _sens():
        rows = [json.loads(ln) for ln in open(m._shard_files(kind="sens"),
                                              encoding="utf-8") if ln.strip()]
        sh = [r["sharpe"] for r in rows]
        return {"k": len(sh),
                "sharpe_p05": round(float(np.percentile(sh, 5)), 4),
                "sharpe_p50": round(float(np.percentile(sh, 50)), 4),
                "sharpe_p95": round(float(np.percentile(sh, 95)), 4),
                "maxdd_worst": round(float(min(r["max_dd"] for r in rows)), 4)}
    leg("sensitivity_aggregation", _sens)

    # -- 10. law-A exit census (heavy leg; timed) ---------------------------
    leg("exit_census", lambda: m._census_core(m._cell_spans(m.HEADLINE), "x1"))

    # -- 11. ledger signature + cutoff meta (no writes) --------------------
    def _ledger():
        import science_gates
        fn = science_gates.append_ledger
        params = set(inspect.signature(fn).parameters)
        need = {"batch_name", "batch_trials", "file_name", "evidence_cutoff"}
        return {"signature": str(inspect.signature(fn)),
                "params_superset_ok": need.issubset(params)}
    leg("append_ledger_signature", _ledger)
    leg("cutoff_meta", lambda: m.cutoff_meta("2026-09-22"))

    # -- assemble ------------------------------------------------------------
    ok = all(l.get("ok") for l in legs.values())
    report = {
        "rehearsal": True,
        "NOT_A_VERDICT": True,
        "why": (f"nulls partial ({n_nulls}/{m.K_NULLS}) -> every "
                "nulls-dependent readout (skill line, g1/g2 pass flags) "
                "is INVALID by construction; this report proves the "
                "finalize code path/mechanics only"),
        "batch": m.BATCH_NAME,
        "ticket": getattr(m, "TICKET", None),
        "machine": "bm-a",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "legs": {k: {"ok": v["ok"], "elapsed_sec": v["elapsed_sec"],
                     "value": slim(v.get("value")),
                     **({"error": v["error"], "tb_tail": v.get("tb_tail")}
                        if not v["ok"] else {})}
                 for k, v in legs.items()},
        "all_legs_ok": ok,
        "elapsed_total_sec": round(time.time() - t_start, 1),
    }
    return report


def main():
    only = ""
    if len(sys.argv) >= 3 and sys.argv[1] == "--fam":
        only = sys.argv[2]
    summary = {}
    for key, path in FAMS:
        if only and key != only:
            continue
        print(f"[rehearsal] {key} ...", flush=True)
        rep = rehearse(key, path)
        op = os.path.join(ROOT, "results",
                          f"_r633bma_finalize_rehearsal_{key}.json")
        with open(op, "w", encoding="utf-8") as f:
            json.dump(rep, f, ensure_ascii=False, indent=1)
        summary[key] = {"all_legs_ok": rep["all_legs_ok"],
                        "elapsed_total_sec": rep["elapsed_total_sec"],
                        "failed_legs": [k for k, v in rep["legs"].items()
                                        if not v["ok"]]}
        print(f"  all_legs_ok={rep['all_legs_ok']} "
              f"elapsed={rep['elapsed_total_sec']}s "
              f"failed={[k for k, v in rep['legs'].items() if not v['ok']]}",
              flush=True)
    sp = os.path.join(ROOT, "results", "_r633bma_finalize_rehearsal_summary.json")
    with open(sp, "w", encoding="utf-8") as f:
        json.dump({"machine": "bm-a",
                   "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
                   "rehearsal": True, "NOT_A_VERDICT": True,
                   "families": summary}, f, ensure_ascii=False, indent=1)
    bad = [k for k, v in summary.items() if not v["all_legs_ok"]]
    print("REHEARSAL " + ("ALL-GREEN" if not bad else "RED: " + ",".join(bad)))
    return 0 if not bad else 4


if __name__ == "__main__":
    raise SystemExit(main())
