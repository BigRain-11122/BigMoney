"""scripts/science_audit.py — M-layer monthly science audit (T-2026-09-23-02-P1, deliverable 5/7).

Authority: research/BACKTEST_SCIENCE.md s7-M (O-20260923-2215).
Criteria FROZEN BEFORE first run in research/SCIENCE_AUDIT_PREREG.md (s1-s6; s7 = live
results filled AFTER the inaugural run). Changing criteria = new prereg + 7-day veto.

The audit is a CHECK-AND-REPORT layer: findings NEVER block any lane, CEO gets
notification with zero action (O-2205). Exit codes: 0 = audit completed (findings or
not), 1 = auditor itself broken (exception / self-consistency red).

Five checks + C6 (registry design — new checks are appended via their own
prereg section; C6 = REGIME_GUARD monthly integrity check, criteria frozen in
research/SCIENCE_AUDIT_PREREG.md s9 BEFORE its first run, authority
REGIME_GUARD.md s4 + T-2026-09-23-05-P1 deliverable (5)):
  C1  null mu/sigma recompute          (rolling drift vs previous snapshot)
  C2  lockbox violation scan           (trials-ledger batch cutoff metadata)
  C3  registered-trader DSR recheck     (recomputed from stored g25 stats at current head)
  C4  gate attrition ledger summary     (results/gate_attrition.json presence/summary)
  C5  skill_line_v2 recompute           (current standing line + drift + formula gate)
  C6  regime-guard integrity            (threshold fingerprint / state continuity / response consistency)

Usage:
  python scripts/science_audit.py selftest   # offline synthetic, zero network, zero writes
  python scripts/science_audit.py run        # live five-check -> results/science_audit.json
"""
from __future__ import annotations

import glob
import json
import math
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import scripts.science_gates as sg

RESULTS_DIR = sg.RESULTS_DIR
AUDIT_PATH = os.path.join(RESULTS_DIR, "science_audit.json")
GATES_REPORT = os.path.join(RESULTS_DIR, "science_gates_v2.json")
UPDATE_STATUS = os.path.join(RESULTS_DIR, "update_status.json")
TRADER_DIR = os.path.join(_ROOT, "firm", "traders")
G25_DIR = os.path.join(RESULTS_DIR, "g25")

# --- frozen criteria (SCIENCE_AUDIT_PREREG s1-s5; do not touch without new prereg) ---
C1_MU_DRIFT_K = 0.25          # |mu_now - mu_prev| > K * sigma_now
C1_SIGMA_DRIFT_K = 0.20       # relative sigma change > 20%
C1_SIGMA_DRIFT_MIN = 1e-6     # sigma_prev below this = baseline degenerate, skip sigma flag
C2_LEGAL_CUTOFF_KEYS = ("evidence_cutoff", "history_end", "panel_end", "data_cutoff")
C2_LEGACY_WHITELIST = {       # frozen 19 pre-v2 batch files (prereg s2; never extended)
    "p1_screen.json", "p2_calibration.json", "p2_survivors.json", "lowchurn_family.json",
    "combined_exit.json", "lfc_p1.json", "new_signal_p1.json", "g2_nsp1.json",
    "p3_portfolio.json", "sleeve_p3.json", "ce_transfer.json", "shortline_p2_synth.json",
    "shortline_p4_batch1.json", "shortline_p4_batch2.json", "shortline_p4_batch2a.json",
    "shortline_p4_queue.json", "shortline_p4_folk.json", "shortline_g2_folk.json",
    "p5_random_entry.json",
}
C3_DSR_GATE = 0.95
C3_SIGMA_CONSISTENCY_RTOL = 1e-3
C5_LINE_DRIFT_K = 0.05
# --- C6 frozen criteria (SCIENCE_AUDIT_PREREG s9; fp frozen at append time) ---
C6_EXPECTED_FP = "368a8d9d2f65669b4ceddf9db6a3efd4661762a4ae6ea3f1fbcfa81977739601"
C6_STATES = ("GREEN", "YELLOW", "ORANGE", "RED")
C6_PRIORITY = ("VIOLATION", "INCONSISTENT", "DRIFT", "GAP", "STALE")


def _load(path: str):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError, UnicodeDecodeError):
        return None


def _now() -> str:
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------- C1 null pool drift

def check_null_pool(prev: dict | None) -> dict:
    pool = sg.null_sharpes()
    cov = pool["coverage"]
    out = {
        "check": "C1_null_mu_sigma_recompute",
        "n_values": cov["n_values"],
        "mu": None if cov["mu"] is None else round(cov["mu"], 6),
        "sigma": None if cov["sigma"] is None else round(cov["sigma"], 6),
        "coverage_note": cov["known_unparsed"],
        "flags": {},
    }
    if prev and prev.get("mu") is not None and cov["mu"] is not None:
        mu_prev, sig_prev = float(prev["mu"]), float(prev["sigma"] or 0.0)
        d_mu = abs(cov["mu"] - mu_prev)
        out["flags"]["mu_drift_flag"] = bool(cov["sigma"] and d_mu > C1_MU_DRIFT_K * cov["sigma"])
        out["flags"]["sigma_drift_flag"] = bool(
            sig_prev > C1_SIGMA_DRIFT_MIN and cov["sigma"]
            and abs(cov["sigma"] - sig_prev) / sig_prev > C1_SIGMA_DRIFT_K)
        out["flags"]["pool_change"] = bool(cov["n_values"] != prev.get("n_values"))
        out["drift_vs"] = {"mu_prev": round(mu_prev, 6), "sigma_prev": round(sig_prev, 6),
                           "n_prev": prev.get("n_values")}
    else:
        out["flags"]["baseline_first_run"] = True
    out["verdict"] = "DRIFT" if any(v for k, v in out["flags"].items()
                                    if k != "pool_change" and k != "baseline_first_run") else "OK"
    return out


# ---------------------------------------------------------------- C2 lockbox scan

def _ledger_files() -> list[str]:
    hits = []
    for path in sorted(glob.glob(os.path.join(RESULTS_DIR, "*.json"))):
        d = _load(path)
        if isinstance(d, dict) and "trials_ledger" in d:
            hits.append(path)
    return hits


def _data_cutoff() -> str | None:
    d = _load(UPDATE_STATUS)
    if isinstance(d, dict) and d.get("data_cutoff"):
        return str(d["data_cutoff"])
    return None


def check_lockbox() -> dict:
    cutoff_now = _data_cutoff()
    files, findings = [], []
    for path in _ledger_files():
        name = os.path.basename(path)
        d = _load(path) or {}
        legal = {k: d.get(k) for k in C2_LEGAL_CUTOFF_KEYS if d.get(k)}
        entry = {"file": name, "cutoff": next(iter(legal.values()), None), "key": next(iter(legal), None)}
        if legal:
            if cutoff_now and str(entry["cutoff"]) > cutoff_now:
                entry["status"] = "VIOLATION"
                entry["reason"] = f"declared cutoff {entry['cutoff']} > data cutoff {cutoff_now} (impossible data)"
                findings.append(entry)
            else:
                entry["status"] = "OK"
        else:
            if name in C2_LEGACY_WHITELIST:
                entry["status"] = "OK_legacy_grandfathered"
            else:
                entry["status"] = "VIOLATION"
                entry["reason"] = "post-v2 batch missing cutoff metadata (unverifiable lockbox read)"
                findings.append(entry)
        files.append(entry)
    return {
        "check": "C2_lockbox_violation_scan",
        "data_cutoff": cutoff_now,
        "n_ledger_files": len(files),
        "n_whitelisted_legacy": sum(1 for f in files if f["status"] == "OK_legacy_grandfathered"),
        "n_ok_with_cutoff": sum(1 for f in files if f["status"] == "OK"),
        "violations": findings,
        "verdict": "VIOLATIONS" if findings else "OK",
    }


# ---------------------------------------------------------------- C3 trader DSR recheck

def _sigma_from_stats(sr_annualized: float, skew: float, kurtosis: float, t: int) -> float:
    sr = float(sr_annualized) / math.sqrt(sg.PERIODS_PER_YEAR)
    denom = 1.0 - skew * sr + (kurtosis - 1.0) / 4.0 * sr * sr
    return math.sqrt(max(denom, 1e-12) / (t - 1))


def check_traders(head_total: int) -> dict:
    rows = []
    for path in sorted(glob.glob(os.path.join(TRADER_DIR, "*.json"))):
        tid = os.path.basename(path)[:-5]
        if tid == "_template":
            continue
        v = _load(os.path.join(G25_DIR, tid + ".json"))
        if not v or not (v.get("legs") or {}).get("dsr"):
            rows.append({"trader": tid, "status": "STALE",
                         "reason": "no g25 verdict file — run g25_retro before adjudication"})
            continue
        dsr_leg = v["legs"]["dsr"]
        rec = {
            "trader": tid,
            "verdict_recorded": v.get("verdict"),
            "dsr_recorded": dsr_leg.get("dsr"),
            "n_trials_recorded": dsr_leg.get("n_trials"),
            "ledger_head_now": head_total,
            "ci_low_recorded": (v["legs"].get("ci") or {}).get("ci95_low"),
            "pbo_recorded": (v["legs"].get("pbo") or {}).get("pbo"),
        }
        sigma_stored = float(dsr_leg.get("sigma_sr") or 0.0)
        if sigma_stored <= 0:
            rec.update({"status": "WARN", "reason": "verdict sigma_sr missing/corrupt"})
            rows.append(rec)
            continue
        # sigma consistency from stored skew/kurt/T (prereg s3)
        try:
            sig_re = _sigma_from_stats(dsr_leg["sr_annualized"], dsr_leg["skew"],
                                       dsr_leg["kurtosis"], dsr_leg["T"])
            rec["sigma_consistent"] = bool(abs(sig_re - sigma_stored) / sigma_stored <= C3_SIGMA_CONSISTENCY_RTOL)
        except (KeyError, TypeError, ValueError):
            rec["sigma_consistent"] = False
        now = sg.dsr_from_stats(dsr_leg["sr_annualized"], sigma_stored, head_total)
        rec["dsr_rechecked_now"] = now["dsr"]
        rec["dsr_gate_cross"] = bool(now["dsr"] >= C3_DSR_GATE)
        rec["status"] = "OK" if rec.get("sigma_consistent") else "WARN"
        rows.append(rec)
    stale = [r for r in rows if r["status"] == "STALE"]
    warn = [r for r in rows if r["status"] == "WARN"]
    return {
        "check": "C3_trader_dsr_recheck",
        "n_traders": len(rows),
        "n_stale": len(stale),
        "n_warn": len(warn),
        "n_gate_cross": sum(1 for r in rows if r.get("dsr_gate_cross")),
        "rows": rows,
        "verdict": "STALE" if stale else ("WARN" if warn else "OK"),
    }


# ---------------------------------------------------------------- C4 attrition ledger

def check_attrition() -> dict:
    path = os.path.join(RESULTS_DIR, "gate_attrition.json")
    d = _load(path)
    if d is None:
        return {"check": "C4_gate_attrition_summary", "status": "MISSING",
                "note": "results/gate_attrition.json not yet filed by any batch receipt "
                        "(BACKTEST_SCIENCE s7-T machine-readable attrition); first batch "
                        "post-review with attrition section creates it",
                "verdict": "MISSING"}
    if isinstance(d, dict):
        entries = d.get("batches") or d.get("entries") or []
        return {"check": "C4_gate_attrition_summary", "status": "PRESENT",
                "n_entries": len(entries) if isinstance(entries, list) else None,
                "keys": sorted(d.keys()),
                "verdict": "OK"}
    return {"check": "C4_gate_attrition_summary", "status": "UNPARSABLE", "verdict": "WARN"}


# ---------------------------------------------------------------- C5 skill line recompute

def check_skill_line(prev: dict | None) -> dict:
    line = sg.skill_line_v2(batch_cells=0)
    out = {
        "check": "C5_skill_line_v2_recompute",
        "line": line["line"],
        "n_eff": line["n_eff"],
        "passive_term": line["passive_term"],
        "null_term": line["null_term"],
        "ledger_head": line["ledger_head"],
        "recorded_lines_jurisdiction": sg.recorded_lines()["jurisdiction"],
        "formula_selfconsistent": bool(abs(line["line"] - max(line["passive_term"], line["null_term"])) < 1e-9),
    }
    if prev and prev.get("line") is not None:
        out["line_prev"] = prev["line"]
        out["flags"] = {"line_drift_flag": bool(abs(line["line"] - float(prev["line"])) > C5_LINE_DRIFT_K)}
    else:
        out["flags"] = {"baseline_first_run": True}
    ok_formula = out["formula_selfconsistent"]
    out["verdict"] = "OK" if ok_formula else "SELFCONSISTENCY_RED"
    return out


# ---------------------------------------------------------------- C6 regime-guard integrity

def _bench_calendar():
    """Independent trading-day calendar from data/daily/510300.csv
    (read-only, zero network; date column by header name)."""
    path = os.path.join(_ROOT, "data", "daily", "510300.csv")
    if not os.path.exists(path):
        return None
    try:
        import csv
        with open(path, encoding="utf-8", newline="") as fh:
            out = []
            for row in csv.DictReader(fh):
                d = str(row.get("date", "")).split(" ")[0].split("T")[0]
                if d:
                    out.append(d)
            return out or None
    except (OSError, ValueError):
        return None


def check_regime_guard(fp_expected: str | None = None) -> dict:
    """SCIENCE_AUDIT_PREREG s9 (criteria FROZEN before first C6 run).
    (a) threshold fingerprint vs prereg; (b) state-series continuity vs
    independent bench calendar; (c) response consistency in shadow era.
    fp_expected param = selftest-only injection; production callers pass
    nothing and get the s9-frozen constant."""
    out = {"check": "C6_regime_guard_integrity", "flags": {}, "findings": []}
    findings = out["findings"]
    expected = fp_expected if fp_expected is not None else C6_EXPECTED_FP

    # (a) threshold fingerprint
    fp = None
    try:
        import scripts.market_regime as mr
        fp = mr.threshold_fingerprint()
    except Exception as exc:            # auditor never dies on lane module
        findings.append({"kind": "MODULE_ERROR", "detail": str(exc)[:200]})
    out["thresholds_fp"] = fp
    out["fp_matches_prereg"] = (fp == expected) if fp is not None else None
    if fp is not None and fp != expected:
        findings.append({"kind": "DRIFT",
                         "detail": "threshold fingerprint != prereg-frozen "
                                   "value (s9) -- law values changed without "
                                   "a new prereg"})

    # (b) state-series continuity
    st = _load(os.path.join(RESULTS_DIR, "regime_state.json"))
    if st is None:
        out["verdict"] = "MISSING"
        out["note"] = "regime_state.json absent -- probe never ran on this node"
        return out
    hist = st.get("history") or []
    out["n_history"] = len(hist)
    cal = _bench_calendar()
    cal_pos = {d: i for i, d in enumerate(cal)} if cal else None
    prev = None
    for e in hist:
        asof, s = str(e.get("asof", "")), e.get("state")
        if s not in C6_STATES:
            findings.append({"kind": "INCONSISTENT",
                             "detail": f"invalid state {s!r} @ {asof}"})
        if prev is not None:
            if asof <= prev["asof"]:
                findings.append({"kind": "INCONSISTENT",
                                 "detail": f"asof not strictly increasing "
                                           f"{prev['asof']} -> {asof}"})
            elif (cal_pos is not None and prev["asof"] in cal_pos
                  and asof in cal_pos
                  and cal_pos[asof] != cal_pos[prev["asof"]] + 1):
                findings.append({"kind": "GAP",
                                 "detail": f"calendar gap {prev['asof']} -> "
                                           f"{asof} (machine-off probe day = "
                                           f"honest finding, not hidden)"})
            if s != prev["state"]:
                if not any(t.get("asof") == asof and t.get("from") == prev["state"]
                           and t.get("to") == s
                           for t in (st.get("transitions") or [])):
                    findings.append({"kind": "INCONSISTENT",
                                     "detail": f"state change "
                                               f"{prev['state']}->{s} @ {asof} "
                                               f"without matching transition"})
                if int(e.get("days_in_state", 0) or 0) != 1:
                    findings.append({"kind": "INCONSISTENT",
                                     "detail": f"days_in_state != 1 on change "
                                               f"day @ {asof}"})
            elif int(e.get("days_in_state", 0) or 0) != \
                    int(prev.get("days_in_state", 0) or 0) + 1:
                findings.append({"kind": "INCONSISTENT",
                                 "detail": f"days_in_state not prev+1 on "
                                           f"same-state day @ {asof}"})
        prev = e
    if cal and hist and str(hist[-1].get("asof")) != cal[-1]:
        findings.append({"kind": "STALE",
                         "detail": f"history tail {hist[-1].get('asof')} != "
                                   f"bench last bar {cal[-1]} (probe not run "
                                   f"after the latest bar)"})
    sfp = st.get("thresholds_fp")
    out["state_file_fp"] = sfp
    if sfp is not None and sfp != expected:
        findings.append({"kind": "DRIFT",
                         "detail": "state-file carried fp != prereg (state "
                                   "written by drifted code, or prereg "
                                   "superseded without s9 revision)"})

    # (c) response consistency (shadow era; enforce response leg = separate
    #     signed item, reported as not_wired when mode ever flips)
    mode = st.get("mode")
    out["state_mode"] = mode
    if mode == "enforce":
        out["flags"]["enforce_response_check"] = \
            "not_wired (separate signed item per s9)"
    if mode not in ("shadow", "enforce"):
        findings.append({"kind": "INCONSISTENT",
                         "detail": f"state mode {mode!r} unknown"})
    state_by_asof = {str(e.get("asof")): e.get("state") for e in hist}
    n_paper = n_block = 0
    for p in sorted(glob.glob(os.path.join(RESULTS_DIR, "paper",
                                           "*_paper.json"))):
        n_paper += 1
        d = _load(p)
        blk = d.get("regime_guard") if isinstance(d, dict) else None
        if not isinstance(blk, dict):
            continue    # block absent = honest rollout note, not a finding
        n_block += 1
        if blk.get("mode") != "shadow":
            findings.append({"kind": "VIOLATION",
                             "detail": f"{os.path.basename(p)}: regime_guard "
                                       f"mode {blk.get('mode')!r} != shadow "
                                       f"(unauthorized interference)"})
        basof = str(blk.get("asof"))
        if basof in state_by_asof and blk.get("state") != state_by_asof[basof]:
            findings.append({"kind": "VIOLATION",
                             "detail": f"{os.path.basename(p)}: block state "
                                       f"{blk.get('state')} != history "
                                       f"{state_by_asof[basof]} @ {basof}"})
    out["paper_files"] = n_paper
    out["paper_with_block"] = n_block
    out["flags"]["paper_block_absent_everywhere"] = bool(n_paper and n_block == 0)

    out["verdict"] = "OK" if not findings else next(
        (k for k in C6_PRIORITY
         if any(f["kind"] == k for f in findings)), "FINDINGS")
    return out


def _exit_code(c5_verdict: str, auditor_error: bool = False) -> int:
    """Prereg s6: 0 = audit completed (findings or not); 1 = auditor broken
    (self-consistency red or internal fault — uncaught exceptions exit 1 anyway)."""
    return 1 if (auditor_error or c5_verdict == "SELFCONSISTENCY_RED") else 0


# ---------------------------------------------------------------- run / rolling ledger

def _prev_snapshot() -> tuple[dict | None, dict | None, str | None]:
    """(null_prev, line_prev, source) — last audit entry, else science_gates report."""
    audit = _load(AUDIT_PATH)
    if audit and isinstance(audit.get("history"), list) and audit["history"]:
        last = audit["history"][-1]
        return last.get("null_pool"), last.get("skill_line"), "science_audit.json:history[-1]"
    rep = _load(GATES_REPORT)
    if rep:
        return (rep.get("null_pool_coverage"),
                rep.get("skill_line_v2_current"),
                "science_gates_v2.json")
    return None, None, None


def run() -> int:
    head = sg.ledger_head()
    null_prev, line_prev, prev_src = _prev_snapshot()
    c1 = check_null_pool(null_prev)
    c2 = check_lockbox()
    c3 = check_traders(head["total"])
    c4 = check_attrition()
    c5 = check_skill_line(line_prev)
    c6 = check_regime_guard()

    payload = {
        "module": "scripts/science_audit.py",
        "authority": "research/BACKTEST_SCIENCE.md s7-M + research/SCIENCE_AUDIT_PREREG.md (s1-s6 frozen before first run; s9 = C6 frozen before its first run)",
        "generated": _now(),
        "ledger_head": head,
        "previous_snapshot_source": prev_src,
        "checks": [c1, c2, c3, c4, c5, c6],
        "summary": {
            "c1_null": c1["verdict"], "c2_lockbox": c2["verdict"], "c3_traders": c3["verdict"],
            "c4_attrition": c4["verdict"], "c5_line": c5["verdict"],
            "c6_regime": c6["verdict"],
            "n_findings": len(c2["violations"]) + c3["n_stale"] + c3["n_warn"]
                           + (1 if c4["verdict"] == "MISSING" else 0)
                           + sum(1 for v in c5["flags"].values() if v)
                           + len(c6["findings"]),
        },
        "discipline": "findings never block any lane; CEO notification zero-action (O-2205)",
    }

    # rolling evolution ledger: append to history, never rewrite prior entries
    audit = _load(AUDIT_PATH) or {"history": []}
    if not isinstance(audit.get("history"), list):
        audit = {"history": []}
    audit["history"].append({
        "generated": payload["generated"],
        "ledger_head": head,
        "null_pool": {k: c1[k] for k in ("n_values", "mu", "sigma")},
        "skill_line": {"line": c5["line"], "n_eff": c5["n_eff"]},
        "checks": payload["checks"],
        "summary": payload["summary"],
    })
    audit["current"] = payload
    tmp = AUDIT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(audit, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, AUDIT_PATH)

    print(json.dumps({"ledger_head": head["total"], "summary": payload["summary"],
                      "prev_src": prev_src}, ensure_ascii=False))
    for c in payload["checks"]:
        print(f"  [{c['verdict']:<8}] {c['check']}")
        for v in c.get("violations", []):
            print(f"      VIOLATION {v['file']}: {v['reason']}")
        for r in c.get("rows", []):
            if r["status"] != "OK":
                print(f"      {r['status']} {r.get('trader','')}: {r.get('reason','')}")
        for f in c.get("findings", []):
            print(f"      {f['kind']}: {f['detail']}")
    return _exit_code(c5["verdict"])


# ---------------------------------------------------------------- selftest (offline, synthetic)

def selftest() -> int:
    import shutil
    import tempfile
    checks = []

    def ok(name, cond):
        checks.append((name, bool(cond)))
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")

    global RESULTS_DIR, UPDATE_STATUS, AUDIT_PATH
    real_results, real_update, real_audit = RESULTS_DIR, UPDATE_STATUS, AUDIT_PATH
    tmp = tempfile.mkdtemp(prefix="sci_audit_st_")
    try:
        # --- C1 drift flag math (same expressions as check_null_pool)
        ok("C1 math: no drift below thresholds",
           not (abs(0.012 - 0.01) > C1_MU_DRIFT_K * 0.201)
           and not (abs(0.201 - 0.20) / 0.20 > C1_SIGMA_DRIFT_K))
        ok("C1 math: mu drift beyond 0.25*sigma flagged",
           abs(0.30 - 0.01) > C1_MU_DRIFT_K * 0.201)
        ok("C1 math: sigma drift beyond 20% flagged",
           abs(0.30 - 0.20) / 0.20 > C1_SIGMA_DRIFT_K)
        ok("C1 baseline: no prev snapshot -> baseline_first_run, verdict OK",
           check_null_pool(None)["verdict"] == "OK"
           and check_null_pool(None)["flags"].get("baseline_first_run") is True)

        # --- C2 lockbox scan on synthetic results dir (real function, temp universe)
        def mk(name, **fields):
            with open(os.path.join(tmp, name), "w", encoding="utf-8") as fh:
                json.dump(fields, fh)

        RESULTS_DIR, UPDATE_STATUS = tmp, os.path.join(tmp, "update_status.json")
        mk("update_status.json", data_cutoff="2026-09-23")
        mk("p1_screen.json", trials_ledger={"total": 10})              # whitelisted legacy, no key
        mk("postv2_ok.json", trials_ledger={"total": 5}, evidence_cutoff="2026-09-22")
        mk("postv2_bad.json", trials_ledger={"total": 5})               # post-v2, no key -> VIOLATION
        mk("postv2_impossible.json", trials_ledger={"total": 5}, evidence_cutoff="2026-12-31")
        mk("not_a_batch.json", other=1)                                # no trials_ledger -> out of universe
        c2 = check_lockbox()
        vmap = {v["file"]: v for v in c2["violations"]}
        ok("C2 universe = 4 ledger files (non-batch excluded)", c2["n_ledger_files"] == 4)
        ok("C2 legacy whitelisted without key -> grandfathered (no violation)",
           "p1_screen.json" not in vmap and c2["n_whitelisted_legacy"] == 1)
        ok("C2 post-v2 with legal cutoff key -> OK (no violation)", "postv2_ok.json" not in vmap)
        ok("C2 post-v2 missing cutoff metadata -> VIOLATION",
           "postv2_bad.json" in vmap and "missing cutoff metadata" in vmap["postv2_bad.json"]["reason"])
        ok("C2 cutoff beyond data cutoff -> VIOLATION (impossible data)",
           "postv2_impossible.json" in vmap and "impossible data" in vmap["postv2_impossible.json"]["reason"])
        ok("C2 verdict VIOLATIONS when any finding", c2["verdict"] == "VIOLATIONS")

        # --- C4 attrition presence check on temp dir
        c4_missing = check_attrition()
        ok("C4 missing ledger -> honest MISSING finding",
           c4_missing["verdict"] == "MISSING" and "not yet filed" in c4_missing["note"])
        mk("gate_attrition.json", batches=[{"batch": "x"}])
        c4_present = check_attrition()
        ok("C4 present ledger -> summarized OK",
           c4_present["verdict"] == "OK" and c4_present["n_entries"] == 1)

        # --- C3 recheck math: recompute-from-stored-stats == raw DSR within tolerance,
        #     monotone in N (ledger growth never raises DSR), sigma consistency path
        rets = sg._synth_returns(1512, 2.5, seed=77)
        raw = sg.deflated_sharpe_ratio(rets, n_trials=2727)
        re = sg.dsr_from_stats(raw["sr_annualized"], raw["sigma_sr"], 2727)
        ok("C3 math: recheck DSR reproduces raw within 0.005", abs(re["dsr"] - raw["dsr"]) <= 0.005)
        re_big = sg.dsr_from_stats(raw["sr_annualized"], raw["sigma_sr"], 50000)
        ok("C3 math: DSR at grown ledger head never rises", re_big["dsr"] <= re["dsr"])
        sig_re = _sigma_from_stats(raw["sr_annualized"], raw["skew"], raw["kurtosis"], raw["T"])
        ok("C3 math: sigma recompute from stats consistent (rtol 1e-3)",
           abs(sig_re - raw["sigma_sr"]) / raw["sigma_sr"] <= C3_SIGMA_CONSISTENCY_RTOL)
        ok("C3 gate: strong synthetic edge crosses 0.95 at 2727", re["dsr"] >= C3_DSR_GATE)

        # --- C5 drift/consistency math (same expressions as check_skill_line)
        ok("C5 math: line drift flag beyond 0.05",
           abs(1.05 - 0.93) > C5_LINE_DRIFT_K and not (abs(0.94 - 0.93) > C5_LINE_DRIFT_K))
        ok("C5 math: formula self-consistency expression",
           abs(0.933 - max(0.4792, 0.933)) < 1e-9)

        # --- C6 regime-guard integrity (synthetic state on temp dir; bench
        #     calendar read real + read-only)
        cal = _bench_calendar()
        d1, d2, d3 = cal[-3], cal[-2], cal[-1]

        def st_write(hist, transitions=None, mode="shadow"):
            with open(os.path.join(tmp, "regime_state.json"), "w",
                      encoding="utf-8") as fh:
                json.dump({"mode": mode, "history": hist,
                           "transitions": transitions or []}, fh)

        st_write([{"asof": d1, "state": "GREEN", "days_in_state": 1},
                  {"asof": d2, "state": "GREEN", "days_in_state": 2},
                  {"asof": d3, "state": "GREEN", "days_in_state": 3}])
        c6 = check_regime_guard()
        ok("C6 OK path: contiguous days + fp match -> OK, zero paper files",
           c6["verdict"] == "OK" and c6["fp_matches_prereg"] is True
           and c6["paper_files"] == 0)
        c6 = check_regime_guard(fp_expected="0" * 64)
        ok("C6 fp mismatch vs injected expected -> DRIFT", c6["verdict"] == "DRIFT")
        st_write([{"asof": d1, "state": "GREEN", "days_in_state": 1},
                  {"asof": d3, "state": "GREEN", "days_in_state": 2}])
        c6 = check_regime_guard()
        ok("C6 calendar gap -> GAP", c6["verdict"] == "GAP")
        st_write([{"asof": d1, "state": "GREEN", "days_in_state": 1},
                  {"asof": d2, "state": "ORANGE", "days_in_state": 1},
                  {"asof": d3, "state": "ORANGE", "days_in_state": 2}],
                 transitions=[{"asof": d2, "from": "GREEN", "to": "YELLOW"}])
        c6 = check_regime_guard()
        ok("C6 state change without matching transition -> INCONSISTENT",
           c6["verdict"] == "INCONSISTENT")
        os.makedirs(os.path.join(tmp, "paper"), exist_ok=True)
        st_write([{"asof": d3, "state": "ORANGE", "days_in_state": 1}])
        with open(os.path.join(tmp, "paper", "X_paper.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"regime_guard": {"mode": "enforce",
                                        "state": "ORANGE", "asof": d3}}, fh)
        c6 = check_regime_guard()
        ok("C6 paper block mode != shadow -> VIOLATION",
           c6["verdict"] == "VIOLATION" and c6["paper_with_block"] == 1)
        with open(os.path.join(tmp, "paper", "X_paper.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"regime_guard": {"mode": "shadow",
                                        "state": "ORANGE", "asof": d3}}, fh)
        c6 = check_regime_guard()
        ok("C6 matching shadow block -> clean OK (no violation, no stale)",
           c6["verdict"] == "OK" and c6["paper_with_block"] == 1)
        st_write([{"asof": d1, "state": "GREEN", "days_in_state": 1}])
        os.remove(os.path.join(tmp, "paper", "X_paper.json"))
        c6 = check_regime_guard()
        ok("C6 history tail != bench last bar -> STALE", c6["verdict"] == "STALE")
        os.remove(os.path.join(tmp, "regime_state.json"))
        c6 = check_regime_guard()
        ok("C6 absent state file -> MISSING", c6["verdict"] == "MISSING")

        # --- run() exit rule: only C5 hard-red exits 1; findings exit 0
        ok("run exit rule: only SELFCONSISTENCY_RED (or auditor fault) exits 1; findings exit 0",
           _exit_code("SELFCONSISTENCY_RED") == 1 and _exit_code("VIOLATIONS") == 0
           and _exit_code("MISSING") == 0 and _exit_code("OK", auditor_error=True) == 1)
    finally:
        RESULTS_DIR, UPDATE_STATUS, AUDIT_PATH = real_results, real_update, real_audit
        shutil.rmtree(tmp, ignore_errors=True)

    n_fail = sum(1 for _, c in checks if not c)
    print(f"\nscience_audit selftest: {len(checks)-n_fail}/{len(checks)} PASS, {n_fail} FAIL")
    return 1 if n_fail else 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    raise SystemExit(selftest() if cmd == "selftest" else run() if cmd == "run" else 0)
