"""Aggregate real system state into dashboard data files.

Writes:
    results/dashboard_status.js   -> window.DASH_DATA = {...}  (for file:// HTML)
    results/dashboard_status.json -> same payload, plain JSON for other consumers

Run:
    python -m monitor.build_status

The 10-minute loop refreshes this every tick; bigmoney.html reads it on open.
All numbers come from real files only — no mock data.
"""
import csv
import glob
import json
import os
import sys
import statistics
import datetime as dt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS, SCREEN
from engine.exit_rules import ExitConfig

COMPOSITE_PLAN = "0.3×(-vol_60) + 0.3×(-intraday_range) + 0.2×mom_12_1 + 0.2×price_position"


def _read_json(path):
    try:
        # utf-8-sig: transparently accepts BOM'd files (state-bm-a.json is
        # written by bm-a's PowerShell tooling with a BOM) and plain UTF-8.
        with open(path, encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception:
        return None


def _smoke_health() -> dict:
    """Parse last line of logs/smoke.log: '<iso> pass=19 fail=0'."""
    p = os.path.join(PATHS.logs_dir, "smoke.log")
    if not os.path.exists(p):
        return {"pass": 0, "fail": -1, "at": None, "ok": False}
    last = ""
    with open(p, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                last = line.strip()
    try:
        head, tail = last.split(" ", 1)
        kv = dict(x.split("=") for x in tail.split())
        return {"pass": int(kv.get("pass", 0)), "fail": int(kv.get("fail", 1)),
                "at": head, "ok": int(kv.get("fail", 1)) == 0}
    except Exception:
        return {"pass": 0, "fail": -1, "at": last, "ok": False}


def _network() -> dict:
    st = _read_json(os.path.join(PATHS.logs_dir, "network_status.json")) or {}
    # Nothing writes this file on cadence (network_detector only writes when
    # run standalone; smoke only reads) -- without a refresh here the panel
    # face sits at UNKNOWN forever on fresh clones. Reuse the detector's own
    # detect/write_status when absent or >30min stale; local OS query only.
    try:
        age_min = None
        ts = st.get("detected_at")
        if ts:
            try:
                age_min = (dt.datetime.now(dt.timezone.utc)
                           - dt.datetime.fromisoformat(ts)).total_seconds() / 60
            except Exception:
                age_min = None
        if age_min is None or age_min > 30:
            import network_detector
            st = network_detector.write_status(network_detector.detect()) or st
    except Exception:
        pass
    return {"net_type": st.get("net_type", "UNKNOWN"),
            "hotspot": bool(st.get("hotspot", False)),
            "allow_heavy_sync": bool(st.get("allow_heavy_sync", False)),
            "detected_at": st.get("detected_at")}


def _data_freshness() -> dict:
    daily = PATHS.daily_dir
    latest, n = None, 0
    for f in os.listdir(daily):
        if not (f.endswith(".csv") and f[:-4].isdigit()):
            continue
        n += 1
        try:
            with open(os.path.join(daily, f), encoding="utf-8") as fh:
                lines = [ln for ln in fh.read().splitlines() if ln.strip()]
            d = dt.date.fromisoformat(lines[-1].split(",")[0])
            if latest is None or d > latest:
                latest = d
        except Exception:
            continue
    stale = (dt.date.today() - latest).days if latest else 999
    return {"n_core": n, "latest_bar": str(latest), "stale_days": stale,
            "fresh": stale <= 15}


def _update_state() -> dict:
    """Daily-update chain health from results/update_status.json (J18b).

    update_daily.py rewrites the file every loop tick; a missing file or an
    old timestamp means the data lifeline is not running on this machine.
    """
    st = _read_json(os.path.join(PATHS.results_dir, "update_status.json")) or {}
    out = {"present": bool(st), "last_run": st.get("updated"), "age_min": None,
           "symbols": st.get("symbols"), "total_new_rows": st.get("total_new_rows"),
           "failures": len(st.get("failures") or []),
           "overlap_mismatches": len(st.get("overlap_mismatches") or []),
           "data_cutoff": st.get("data_cutoff"),
           "status": "none", "text": "更新链待产出"}
    if not st:
        return out
    try:
        t = dt.datetime.fromisoformat(str(st.get("now") or st.get("updated")))
        out["age_min"] = int((dt.datetime.now() - t).total_seconds() // 60)
    except Exception:
        pass
    if out["failures"] > 0:
        out["status"], out["text"] = "bad", f"更新链 {out['failures']} 失败"
    elif out["overlap_mismatches"] > 0:
        out["status"], out["text"] = "warn", "更新链 overlap 错配"
    elif out["age_min"] is not None and out["age_min"] > 60:
        out["status"], out["text"] = "warn", f"更新链 {out['age_min']}分未跑"
    else:
        out["status"], out["text"] = "ok", "更新链活 · 0 失败"
    return out


def _heat_state() -> dict:
    """Heat/attention chain health (P-C family, O-1850) from results/heat_*_status.json.

    L1 = update_heat.py daily guba-popularity snapshot collector;
    L2 = backfill_heat_history.py per-stock rank-history backfill.
    L2 rejects are honest short-history refusals (frozen floor policy,
    PC_COLLECTOR sec4.1) and do not raise a flag by design.
    """
    l1 = _read_json(os.path.join(PATHS.results_dir, "heat_update_status.json")) or {}
    l2 = _read_json(os.path.join(PATHS.results_dir, "heat_backfill_status.json")) or {}
    era = l2.get("dataset_era") or {}
    n_l2 = l2.get("n_done_run")
    out = {
        "present": bool(l1 or l2),
        "l1_verdict": l1.get("verdict"),
        "l1_snapshots": l1.get("snapshots"),
        "l1_updated": l1.get("updated"),
        "l2_updated": l2.get("updated"),
        "l2_done": n_l2, "l2_target": l2.get("n_target"),
        "l2_rejects": len(l2.get("failures") or []),
        "era_min": era.get("date_min"), "era_max": era.get("date_max"),
        "status": "none", "text": "热度链待产出",
    }
    if not out["present"]:
        return out
    v = str(out["l1_verdict"] or "")
    if v.startswith("fetch_fail") or v.startswith("validation_fail"):
        out["status"], out["text"] = "bad", "热度采集失败"
    elif v == "fetching":
        out["status"], out["text"] = "warn", "热度采集中"
    else:
        l2_txt = "—" if n_l2 is None else f"{n_l2}/{out['l2_target'] or 0}件"
        out["status"], out["text"] = "ok", f"热度链活 · L1 {out['l1_snapshots'] or 0}份 · L2 {l2_txt}"
    return out


def _futures_state() -> dict:
    """C-layer futures daily chain (bm-a R48 update_futures.py) from
    results/futures_update_status.json. In the S6 auto-loop since R51 bm-a
    (daily-cutoff zero-network no-op guard); staleness is disclosed as warn
    (age>24h), not red."""
    st = _read_json(os.path.join(PATHS.results_dir, "futures_update_status.json")) or {}
    pv = st.get("per_variety") or []
    out = {"present": bool(st), "varieties": len(pv),
           "planned": len(st.get("varieties_planned") or []),
           "last_attempt": st.get("last_attempt") or st.get("ts"),
           "age_min": None, "cutoff": None, "errors": 0, "rows_total": 0,
           "status": "none", "text": "期货链待产出"}
    if not out["present"]:
        return out
    for v in pv:
        if v.get("error"):
            out["errors"] += 1
        out["rows_total"] += v.get("rows_local") or 0
        last = str(v.get("last") or "")
        if last and (out["cutoff"] is None or last > out["cutoff"]):
            out["cutoff"] = last
    try:
        t = dt.datetime.fromisoformat(str(out["last_attempt"]))
        out["age_min"] = int((dt.datetime.now() - t).total_seconds() // 60)
    except Exception:
        pass
    if out["errors"]:
        out["status"], out["text"] = "bad", f"期货链 {out['errors']} 品种失败"
    elif out["varieties"] < out["planned"]:
        out["status"], out["text"] = "warn", f"期货链 {out['varieties']}/{out['planned']} 品种"
    elif out["age_min"] is not None and out["age_min"] > 24 * 60:
        out["status"], out["text"] = "warn", f"期货链 {out['age_min'] // 60}h 未跑"
    else:
        out["status"], out["text"] = "ok", f"期货链 {out['varieties']} 品种在库"
    return out


def _moneyflow_state() -> dict:
    """Stock main-moneyflow forward panel (bm-a R63 update_moneyflow.py,
    MF_COLLECTOR spec) from results/moneyflow_update_status.json.
    Connection-level source block = parked with 30min-gate self-heal
    (honest warn, P-B r40 precedent); mismatches = bad."""
    st = _read_json(os.path.join(PATHS.results_dir,
                                 "moneyflow_update_status.json")) or {}
    pn = st.get("panel") or {}
    lr = st.get("last_refresh") or {}
    out = {"present": bool(st), "mode": st.get("mode"),
           "complete": bool(pn.get("complete")), "cutoff": pn.get("cutoff"),
           "n_symbols": pn.get("n_symbols") or 0,
           "universe_n": pn.get("universe_n"),
           "appended": lr.get("appended") or 0,
           "failures": lr.get("failures") or 0,
           "conn_stopped": bool(lr.get("conn_stopped")),
           "mismatches": lr.get("n_mismatches") or 0,
           "last_attempt": st.get("ts"), "age_min": None,
           "status": "none", "text": "资金流面板待产出"}
    if not out["present"]:
        return out
    try:
        t = dt.datetime.fromisoformat(str(out["last_attempt"]))
        out["age_min"] = int((dt.datetime.now() - t).total_seconds() // 60)
    except Exception:
        pass
    have = f"{out['n_symbols']}/{out['universe_n']}"
    if out["mismatches"]:
        out["status"] = "bad"
        out["text"] = f"资金流源改史 {out['mismatches']} 行旗标"
    elif out["complete"]:
        out["status"] = "ok"
        out["text"] = f"资金流面板 {have} 只 · cutoff {out['cutoff'] or '—'}"
    elif out["conn_stopped"]:
        out["status"] = "warn"
        out["text"] = f"资金流源阻断停发 · 30min 自愈 · 已采 {have}"
    else:
        out["status"] = "warn"
        out["text"] = f"资金流首拉/刷新在途 · 已采 {have}"
    return out


def _regime_state() -> dict:
    """Market regime guard shadow state (REGIME_GUARD v1.0, T-05) from
    results/regime_state.json. Missing file = honest not-yet-probed."""
    st = _read_json(os.path.join(PATHS.results_dir, "regime_state.json")) or {}
    state = st.get("state")
    bad = state in ("ORANGE", "RED")
    out = {
        "present": bool(st), "asof": st.get("asof"), "mode": st.get("mode"),
        "state": state, "state_cn": st.get("state_cn"),
        "raw_level": st.get("raw_level"),
        "days_in_state": st.get("days_in_state"),
        "triggers": st.get("triggers") or [],
        "last_transition": (st.get("transitions") or [{}])[-1] or None,
    }
    out["status"] = "bad" if bad else ("ok" if st else "missing")
    return out


def _portfolio_state() -> dict:
    """Portfolio & Capital dept dashboard (org_chart v3, O-2311) from
    results/portfolio_ew6.json (T-06, EW6 report-only pass 1).
    Report-only by charter: reads are regime-discounted, no promotion
    or allocation signal is derived here."""
    j = _read_json(os.path.join(PATHS.results_dir, "portfolio_ew6.json")) or {}
    x1 = (j.get("portfolios") or {}).get("x1") or {}
    x2 = (j.get("portfolios") or {}).get("x2") or {}
    ev = j.get("verdict") or {}
    ov = (j.get("regime") or {}).get("overlay") or {}
    out = {
        "present": bool(x1),
        "generated": j.get("generated"),
        "members": len((j.get("universe") or {}).get("members") or []),
        "ew_sharpe": (x1.get("full") or {}).get("sharpe"),
        "ew_annual": (x1.get("full") or {}).get("annual_return"),
        "ew_dd": (x1.get("full") or {}).get("max_drawdown"),
        "n_trades": x1.get("n_trades"),
        "worst_year": ev.get("ew_worst_year", x1.get("worst_year")),
        "weighted_mean": x1.get("weighted_mean_member_sharpe"),
        "benefit": ev.get("ew_benefit"),
        "dr": ev.get("ew_dr"),
        "ew_validated": ev.get("ew_validated"),
        "x2_sharpe": (x2.get("full") or {}).get("sharpe"),
        "x2_survive": ev.get("ew_x2_survive"),
        "overlay_sharpe": (ov.get("full") or {}).get("sharpe"),
        "overlay_worst_year": ov.get("worst_year"),
        "bear_days": ov.get("bear_days_used"),
        "applicability": ev.get("applicability"),
        "status": "ok" if x1 else "none",
        "text": "EW6 报告制" if x1 else "组合批待产出",
    }
    # IV6 report-only pass 2 (bm-a R35, charter s1.1 IV path): display-only block;
    # EW stays the validated carrier (no post-run switching), IV adoption = charter s5 T1.
    ivj = _read_json(os.path.join(PATHS.results_dir, "portfolio_iv6.json")) or {}
    ivx1 = (ivj.get("portfolios_iv") or {}).get("x1") or {}
    ivx2 = (ivj.get("portfolios_iv") or {}).get("x2") or {}
    ivv = ivj.get("verdict") or {}
    ivh = ivv.get("head_to_head") or (ivj.get("head_to_head") or {})
    ivg = ivj.get("v2_gate_iv6") or {}
    out["iv"] = {
        "present": bool(ivx1),
        "generated": ivj.get("generated"),
        "sharpe": (ivx1.get("full") or {}).get("sharpe"),
        "annual": (ivx1.get("full") or {}).get("annual_return"),
        "dd": (ivx1.get("full") or {}).get("max_drawdown"),
        "worst_year": ivx1.get("worst_year"),
        "n_trades": ivx1.get("n_trades"),
        "benefit": ivx1.get("benefit", ivv.get("iv_benefit")),
        "dr": ivx1.get("dr", ivv.get("iv_dr")),
        "x2_sharpe": (ivx2.get("full") or {}).get("sharpe"),
        "x2_survive": ivv.get("iv_x2_survive"),
        "validated": ivv.get("iv_validated"),
        "v2_pass": ivv.get("v2_pass"),
        "skill_line_v2": ivg.get("skill_line", {}).get("line") if isinstance(ivg.get("skill_line"), dict) else ivg.get("skill_line"),
        "ci95_low": (ivg.get("bootstrap_ci") or {}).get("ci95_low"),
        "delta_sharpe": ivh.get("delta_full_sharpe"),
        "delta_dd": ivh.get("delta_max_dd"),
        "corr_ew": ivh.get("corr_iv6_ew6"),
        "weights": ivx1.get("weights") or {},
        "status": "ok" if ivx1 else "none",
    }
    return out


def _corr_watch_state() -> dict:
    """Correlation watch + IV-weight refresh monitor (portfolio dept
    charter s1.2, R36) from results/corr_watch.json. Report-only watch
    (W1 full-window D6 line / W2 IS2 convergence / W3 trend / W4
    disclosure / W5 x2 margin); zero-N_eff monitoring class per JSON
    audit block — no promotion or allocation signal derived here."""
    j = _read_json(os.path.join(PATHS.results_dir, "corr_watch.json")) or {}
    w = j.get("watch") or {}
    w2 = w.get("W2_is2_convergence") or {}
    w5 = w.get("W5_x2_margins") or {}
    margins = [m.get("margin") for m in w5.values()
               if isinstance(m, dict) and isinstance(m.get("margin"), (int, float))]
    traj = w.get("rolling_traj") or {}
    ivw = (j.get("iv_weight_refresh") or {}).get("weights") or {}
    fl = j.get("forward_leg") or {}
    flag = j.get("verdict")
    out = {
        "present": bool(w),
        "generated": j.get("generated"),
        "verdict": flag,
        "w1_flag": (w.get("W1_full_d6_line") or {}).get("flag"),
        "w2_flag": w2.get("flag"),
        "w2_hits": len(w2.get("hits") or {}),
        "max_is2_pair": w.get("max_is2_pair"),
        "corr_iv6_ew6": (w.get("W4_corr_iv6_ew6") or {}).get("got"),
        "x2_margin_min": min(margins) if margins else None,
        "rolling_avg_last": traj.get("avg_last"),
        "iv_weight_max": max(ivw.values()) if ivw else None,
        "twin_ok": (j.get("twin") or {}).get("ok"),
        "forward_status": fl.get("status"),
        "forward_bars": fl.get("min_bars"),
        "status": "ok" if w else "none",
        "text": (f"{flag} · W2 IS2 越线 {len(w2.get('hits') or {})} 对"
                 if w else "监控待产出"),
    }
    return out


def _watermark_state() -> dict:
    """CPU watermark closed-loop display (T-25 / O-20260924-1626 R3):
    py curve tail from watermark.jsonl + RED flag from watermark_red.json
    (watchdog C7 leg) + recent RED count from watchdog.log tail."""
    out: dict = {"present": False, "py_tail": [], "last_sample": None,
                 "red": False, "lane": "—", "zombies_killed": [],
                 "red_flags_recent": 0}
    py_tail: list = []
    try:
        with open(os.path.join(PATHS.results_dir, "watermark.jsonl"),
                  "r", encoding="utf-8") as f:
            lines = f.readlines()[-5:]
        for ln in lines:
            s = json.loads(ln)
            py_tail.append(round(float(s.get("py_cpu_pct", 0.0)), 1))
            out["last_sample"] = s.get("ts")
    except Exception:
        py_tail = []
    if py_tail:
        out["present"] = True
        out["py_tail"] = py_tail
    rf = _read_json(os.path.join(PATHS.results_dir, "watermark_red.json"))
    if rf:
        out["red"] = bool(rf.get("red"))
        out["lane"] = rf.get("lane") or "—"
        out["zombies_killed"] = rf.get("zombies_killed") or []
        out["next_pick"] = rf.get("next_pick")   # T-25 seg-a advisory surface
    n_red = 0
    try:
        with open(os.path.join(PATHS.logs_dir, "watchdog.log"),
                  "r", encoding="utf-8", errors="replace") as f:
            tail = f.readlines()[-400:]
        n_red = sum(1 for ln in tail if "C7 WATERMARK RED" in ln)
    except Exception:
        n_red = 0
    out["red_flags_recent"] = n_red
    return out


def _autofill_state() -> dict:
    """C8 auto-fill display (T-36 / O-20260924-2100 §2): runnable-pool
    ready count + last autofill tick verdict + fill latency vs the
    ready->running <=10min hard target (from results/autofill_state.json)."""
    pool = _read_json(os.path.join(PATHS.results_dir, "runnable_pool.json")) or {}
    entries = pool.get("entries") or []
    ready = [e for e in entries if e.get("status") == "ready"]
    waiting = [e for e in entries if e.get("status") == "waiting"]
    st = _read_json(os.path.join(PATHS.results_dir, "autofill_state.json")) or {}
    tick = st.get("last_tick") or {}
    launches = st.get("launches") or []
    lat = [l.get("fill_latency_min") for l in launches
           if l.get("fill_latency_min") is not None]
    return {
        "present": bool(pool),
        "pool_ready": len(ready),
        "pool_waiting": len(waiting),
        "ready_ids": [e.get("id") for e in ready],
        "last_tick": tick.get("ts"),
        "verdict": tick.get("verdict"),
        "py_cpu_pct": tick.get("py_cpu_pct"),
        "launches_total": len(launches),
        "fill_latency_last": lat[-1] if lat else None,
        "fill_target_met": all(
            l.get("target_met", True) for l in launches[-10:]),
    }


def _saturation_state() -> dict:
    """Fleet CPU saturation panel (T-55 / O-20260925-1137): pool ready count
    + starvation flag state + this machine's py watermark series.

    Per-machine py series lives in each machine's LOCAL watermark.jsonl
    (gitignored by design, T-25) -- the dashboard built on each machine
    shows that machine's own series honestly; pool/flag faces come from
    git-synced shared mirrors (runnable_pool.json / compute_audit.json).
    """
    out = {"present": False, "py_tail": [], "py_last_sample": None,
           "pool_ready": None, "pool_waiting": None, "ready_ids": [],
           "load_state": None, "starvation_flag": False,
           "starvation_candidate": False, "audit_ts": None,
           "starvation_flags_recent": 0}
    py_tail: list = []
    try:
        with open(os.path.join(PATHS.results_dir, "watermark.jsonl"),
                  "r", encoding="utf-8") as f:
            lines = f.readlines()[-12:]
        for ln in lines:
            s = json.loads(ln)
            py_tail.append(round(float(s.get("py_cpu_pct", 0.0)), 1))
            out["py_last_sample"] = s.get("ts")
    except Exception:
        py_tail = []
    out["py_tail"] = py_tail
    pool = _read_json(os.path.join(PATHS.results_dir, "runnable_pool.json")) or {}
    entries = pool.get("entries") or []
    ready = [e for e in entries if e.get("status") == "ready"]
    waiting = [e for e in entries if e.get("status") == "waiting"]
    out["pool_ready"] = len(ready)
    out["pool_waiting"] = len(waiting)
    out["ready_ids"] = [e.get("id") for e in ready]
    au = _read_json(os.path.join(PATHS.results_dir, "compute_audit.json"))
    if au:
        la = au.get("latest") or {}
        out["load_state"] = la.get("load_state")
        out["starvation_flag"] = "pool_starvation" in (la.get("flags") or [])
        out["starvation_candidate"] = bool(la.get("pool_starvation_candidate"))
        out["audit_ts"] = la.get("ts")
        out["starvation_flags_recent"] = sum(
            1 for s in (au.get("history") or [])[-100:]
            if "pool_starvation" in (s.get("flags") or []))
    out["present"] = bool(py_tail) or bool(entries) or bool(au)
    return out


def _token_state() -> dict:
    """Local-first token metering (O-2325, T-04 F6) from
    results/token_usage.json. Byte/3.5 rough proxy, honestly labelled."""
    st = _read_json(os.path.join(PATHS.results_dir, "token_usage.json")) or {}
    ctx = st.get("per_round_context") or {}
    delta = st.get("delta_vs_prev") or {}
    out = {
        "present": bool(st), "generated": st.get("generated"),
        "mandate_est": ctx.get("mandate_read_tokens_est"),
        "codely_context_est": ctx.get("codely_read_tokens_est"),
        "state_est": st.get("total_state_tokens_est"),
        "report_est": st.get("total_report_tokens_est"),
        "delta_state": delta.get("state_tokens_growth"),
        "delta_report": delta.get("report_tokens_growth"),
        "delta_prev": delta.get("prev_generated"),
    }
    return out


def _factor_top(n: int = 10) -> list:
    ic = _read_json(os.path.join(PATHS.results_dir, "factor_ic.json")) or {}
    rows = [{"factor": k[:-4], "horizon": k[-2:],
             "ic_mean": v["ic_mean"], "ic_ir": v["ic_ir"],
             "ic_pos_pct": v["ic_pos_pct"]}
            for k, v in ic.items() if k.endswith("_h20")]
    rows.sort(key=lambda r: abs(r["ic_mean"]), reverse=True)
    return rows[:n]


def _factor_line() -> dict:
    """Research-line factor batches + factor-ledger head (dual-series, R60).

    Factor ledger series lives in results/shortline/*.json (r32 precedent,
    engine N untouched); head via science_gates.ledger_head over that dir.
    All counts data-driven (O-2250 counting single-source rule).
    """
    sl = os.path.join(PATHS.results_dir, "shortline")
    out = {"present": False, "total": None, "head_file": None, "batches": []}
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), "scripts"))
        from science_gates import ledger_head
        head = ledger_head(sl)
        if head["total"]:
            out["total"] = int(head["total"])
            out["head_file"] = head["file"]
    except Exception:
        pass

    def _sl(name):
        return _read_json(os.path.join(sl, name))

    def _add(bid, text, short):
        out["batches"].append({"id": bid, "text": text, "short": short})

    pa = _sl("pa_lhb_ic.json")
    if pa:
        rows = [r for r in (pa.get("rows") or []) if r.get("pass") is not None]
        n_pass = sum(1 for r in rows if r.get("pass"))
        _add("P-A LHB", f"{n_pass}/{len(rows)} 过门", f"{n_pass}/{len(rows)}")
    p1c = _sl("p1c_stock_ic.json")
    if p1c:
        c = p1c.get("counts") or {}
        m = p1c.get("meta") or {}
        wq = "WQ 腿完成" if m.get("wq_complete") else "WQ 腿在飞"
        wq_s = "WQ完成" if m.get("wq_complete") else "WQ飞"
        legs = m.get("legs") or {}
        if "wq" in legs:
            # Post-WQ finalize counts are COMBINED across legs (finalize
            # aggregates all checkpoints); split per-leg pool by factor-name
            # prefix -- same inference finalize itself uses -- so the GTJA
            # label stays factual after the WQ leg lands.
            pool = p1c.get("pool_h10") or []
            gp = sum(1 for f in pool if str(f).startswith("alpha191_"))
            wp = len(pool) - gp
            g_ok = (legs.get("gtja") or {}).get("ok")
            w_ok = (legs.get("wq") or {}).get("ok")
            # single-CJK-char state suffix keeps the dashboard digest under
            # the r13-measured ~75-char ellipsis clip line after WQ lands
            wq_end = "完" if m.get("wq_complete") else "飞"
            _add("P-1c 股票池",
                 f"GTJA {gp}/{g_ok} · WQ {wp}/{w_ok} · {wq}",
                 f"GTJA {gp}/{g_ok} WQ {wp}/{w_ok}{wq_end}")
        else:
            _add("P-1c 股票池",
                 f"GTJA {c.get('pool_h10')}/{c.get('ok')} · {wq}",
                 f"GTJA {c.get('pool_h10')}/{c.get('ok')} {wq_s}")
    p1d = _sl("p1d_ext_slots_ic.json")
    if p1d:
        c = p1d.get("counts") or {}
        _add("P-1d 扩展槽", f"{c.get('pass')}/{c.get('computed')} 过门",
             f"{c.get('pass')}/{c.get('computed')}")
    gq = _sl("p1d_gdhs_quarterly.json")
    if gq:
        vs = gq.get("verdict_summary") or {}
        _add("P-1d gdhs quarterly",
             f"{vs.get('pass')}/{vs.get('of')} quarterly-frequency",
             f"{vs.get('pass')}/{vs.get('of')}")
    pc = _sl("pc_l2_ic.json")
    if pc:
        rows = [r for r in (pc.get("rows") or []) if r.get("pass") is not None]
        n_pass = sum(1 for r in rows if r.get("pass"))
        _add("热度 L2", f"{n_pass}/{len(rows)} 过门", f"{n_pass}/{len(rows)}")
    xl = _sl("xlib_synth.json")
    if xl:
        pr = xl.get("primary") or {}
        if pr:
            k4 = pr.get("k")
            _add("XLIB 跨库合成",
                 (f"K{k4} 过门" if pr.get("pass")
                  else f"K{k4} V2 剃刀差收线"),
                 f"K{k4}{'过' if pr.get('pass') else '判负'}")
    out["present"] = bool(out["batches"]) or out["total"] is not None
    # Compact digest for width-budgeted dashboard rows (full text stays in
    # the events log); built data-driven from the batch shorts above.
    if out["present"]:
        short = {"P-A LHB": "LHB", "P-1c 股票池": "", "P-1d 扩展槽": "槽",
                 "热度 L2": "L2", "XLIB 跨库合成": "XLIB",
                 "P-1d gdhs quarterly": "gdhs"}
        seg = []
        for b in out["batches"]:
            label = (short.get(b["id"], b["id"]) + " "
                     + (b.get("short") or b["text"])).strip()
            seg.append(label)
        dig = " · ".join(seg)
        out["digest"] = f"N={out['total'] or '—'} · {dig}" if out["total"] else dig
    return out


def _backtest_summary() -> dict:
    sharpe, ar, mdd = [], [], []
    n_ok = passed = 0
    for f in glob.glob(os.path.join(PATHS.results_dir, "*.json")):
        base = os.path.basename(f)
        if base.startswith(("factor_ic", "dashboard_status")):
            continue
        d = _read_json(f)
        if not isinstance(d, dict) or d.get("status") != "ok":
            continue  # probe/scratch products may be list-typed; backtest faces are dict-only
        n_ok += 1
        m = d["metrics"]
        sharpe.append(m["sharpe"])
        ar.append(m["annual_return"])
        mdd.append(abs(m["max_drawdown"]))
        if (m.get("num_trades", 0) >= SCREEN.min_trades
                and abs(m.get("max_drawdown", 0)) <= SCREEN.max_drawdown_limit
                and m.get("sharpe", 0) >= SCREEN.min_sharpe
                and m.get("annual_return", 0) > 0):
            passed += 1
    return {
        "n_combos": n_ok,
        "sharpe_med": round(statistics.median(sharpe), 3) if sharpe else None,
        "sharpe_max": round(max(sharpe), 3) if sharpe else None,
        "ar_med": round(statistics.median(ar), 4) if ar else None,
        "ar_max": round(max(ar), 4) if ar else None,
        "mdd_med": round(statistics.median(mdd), 3) if mdd else None,
        "n_pass": passed,
    }


def _ranking_rows(n: int = 5) -> list:
    p = os.path.join(PATHS.results_dir, "ranking.csv")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows[:n]


def _gate_chain(bt: dict) -> dict:
    """Honest gate-chain narrative from real result files (no hard-coded numbers).

    432 MA grid dead -> G1' survivors -> G2 deepening -> J14 low-churn -> J15
    combined exit -> J19 CE-machine transfer.
    """
    res = PATHS.results_dir
    cal = _read_json(os.path.join(res, "p2_calibration.json")) or {}
    dep = _read_json(os.path.join(res, "p2_survivors.json")) or {}
    lc = _read_json(os.path.join(res, "lowchurn_family.json")) or {}
    ce = _read_json(os.path.join(res, "combined_exit.json")) or {}
    ct = _read_json(os.path.join(res, "ce_transfer.json")) or {}
    p3p = _read_json(os.path.join(res, "p3_portfolio.json")) or {}
    lfc = _read_json(os.path.join(res, "lfc_p1.json")) or {}
    nsp = _read_json(os.path.join(res, "new_signal_p1.json")) or {}
    g2n = _read_json(os.path.join(res, "g2_nsp1.json")) or {}
    slp = _read_json(os.path.join(res, "sleeve_p3.json")) or {}
    p4b1 = _read_json(os.path.join(res, "shortline_p4_batch1.json")) or {}
    p5re = _read_json(os.path.join(res, "p5_random_entry.json")) or {}
    p4b2 = _read_json(os.path.join(res, "shortline_p4_batch2.json")) or {}
    p4p = _read_json(os.path.join(res, "shortline_p4_pairs.json")) or {}
    p4q = _read_json(os.path.join(res, "shortline_p4_queue.json")) or {}
    p4e = _read_json(os.path.join(res, "shortline_p4_ext_tilt.json")) or {}
    p2s = _read_json(os.path.join(res, "shortline_p2_synth.json")) or {}
    gm1 = _read_json(os.path.join(res, "p4_batch1.json")) or {}
    b2a = _read_json(os.path.join(res, "shortline_p4_batch2a.json")) or {}
    folk = _read_json(os.path.join(res, "shortline_p4_folk.json")) or {}
    p5b = _read_json(os.path.join(res, "p5b_new_traders.json")) or {}
    surv = cal.get("survivors_g1_prime") or []
    gate = cal.get("g1_prime_gate") or {}
    g2 = dep.get("verdicts_g2") or {}
    g2_pass = sum(1 for v in g2.values() if v.get("g2_pass"))
    lc_verdicts = lc.get("verdicts") or {}
    lc_pass = sum(1 for v in lc_verdicts.values() if v.get("g2_pass"))
    ce_v = ce.get("verdict") or {}
    ce_pass = 1 if ce_v.get("g2_pass") else 0
    ct_v = ct.get("verdict") or {}
    ct_pass = int(ct_v.get("n_pass") or 0)
    lfc_v = lfc.get("verdict") or {}
    lfc_pass = int(lfc_v.get("n_survivors") or 0) if not lfc_v.get("void") else 0
    lfc_gate = lfc.get("gate") or {}
    g2f = _read_json(os.path.join(res, "shortline_g2_folk.json")) or {}
    # Counting single-source rule (O-2250 T2): registered-roster count/ids come
    # from the firm/traders glob (same source as the org wall _traders()), NOT
    # from per-batch "traders_registered" lists -- those froze at J19 (3) and
    # missed G2_FOLK's 3 folk traders (stale-3 panel bug caught in r53 pixel
    # acceptance: strategy wall said 3 while the org wall showed 6 cards).
    # T-24 (2026-09-24): PROSPECT observation members live in the same dir
    # but are NOT registered roster -- excluded here + shown as a separate
    # prospect pool line (_prospect_state).
    _troot = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "firm", "traders")
    traders = []
    for f in sorted(os.listdir(_troot)):
        if not (f.endswith(".json") and not f.startswith("_")):
            continue
        t = _read_json(os.path.join(_troot, f))
        if t and t.get("level") != "PROSPECT":
            traders.append(f[:-5])
    # Counting single-source rule (O-2250 T2): panel N = data-driven ledger
    # chain head via science_gates.ledger_head (max total across
    # results/*.json). Replaces the r35-era hardcoded file cascade that
    # froze at p4_batch2 (2090) and missed P-5B (2727) / EW6 (2753).
    trials_total = 0
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), "scripts"))
        from science_gates import ledger_head
        trials_total = int(ledger_head(str(PATHS.results_dir))["total"])
    except Exception:
        trials_total = 0
    skill_bar = gate.get("effective_skill_bar")
    ct_note = ""
    if ct:
        greens = ct_v.get("green_entries") or []
        if ct_pass:
            ct_note = f"{'/'.join(greens)} ×2 成本存活，注册 {ct_pass} 员"
        elif greens:
            ct_note = f"{'/'.join(greens)} 1×绿但 ×2 未存活"
        else:
            ct_note = "迁移点 1× 即红"
    steps = [
        {"stage": "前代基线 · 432 组内置均线", "result": f"{bt['n_pass']}/{bt['n_combos']} 过线",
         "pass": bt["n_pass"] > 0, "note": "盲测全灭，信号层换血"},
        {"stage": "G1' 有效性门 · 预注册零假设校准(n=100)", "result": f"{len(surv)} 员幸存",
         "pass": len(surv) > 0,
         "note": f"技能线 Sharpe>{skill_bar}（随机p95+被动+0.1）" if skill_bar else ""},
        {"stage": "G2 深化门 · 邻域+成本×2", "result": f"{g2_pass} 员",
         "pass": g2_pass > 0, "note": "low_vol/composite 折戟成本关"},
        {"stage": "J14 低换手结构族", "result": f"{lc_pass} 员",
         "pass": lc_pass > 0, "note": "降频杀α整轴死刑，退出软化线索出土"},
        {"stage": "J15 组合退出软化 · 全G2一次总装", "result": f"{ce_pass} 员 PASS",
         "pass": ce_pass > 0,
         "note": f"代表点 {ce_v.get('representative', '-')} 成本×2 存活"},
    ]
    if ct:
        steps.append({"stage": "J19 CE 机跨入场迁移 · composite",
                      "result": f"{ct_pass} 员 PASS" if not ct_v.get("void")
                      else "无效（锚点破）",
                      "pass": ct_pass > 0, "note": ct_note})
    # r34 bm-c chain-integrity sweep #6: P3 portfolio validation (plan §四
    # stage, OS-round-13) was never wired -- J19(step6) jumped straight to
    # LFC(step7); wired here in chronological slot after J19, data-driven.
    if p3p:
        p3v = p3p.get("verdict") or {}
        ew_ok = bool(p3v.get("ew_validated"))
        iv_ok = bool(p3v.get("iv_validated"))
        ew_ben = p3v.get("ew_benefit")
        iv_ben = p3v.get("iv_benefit")
        steps.append({"stage": "P3 组合验证 · 三员 EW/IV 双载体",
                      "result": f"EW {'validated' if ew_ok else 'FAIL'}"
                                f"·IV {'同判过' if iv_ok else '异判'}",
                      "pass": ew_ok,
                      "note": (f"benefit EW +{ew_ben:.2f}/IV +{iv_ben:.2f}；"
                               "分散化素材=低相关；载体裁定=先验EW（择优禁令）"
                               if ew_ben is not None and iv_ben is not None
                               else "")})
    if lfc:
        p95 = lfc_gate.get("random_p95_full") or {}
        vb = lfc_gate.get("vi_bar")
        n_sleeve = int(lfc_v.get("n_sleeves") or 0)
        skill = max([v for v in (p95.get("ce"), p95.get("default"), vb)
                     if v is not None], default=None)
        steps.append({"stage": "LFC 低频低成本品种族 · 债金池 mini 海选",
                      "result": f"{lfc_pass} 员幸存" if not lfc_v.get("void")
                      else "无效（锚点破）",
                      "pass": lfc_pass > 0,
                      "note": (f"池本地技能线≈{skill}（随机p95+被动+0.1，为权益池3倍）；"
                               f"tsmom/donchian CE 最佳未达线；袖珍候选 {n_sleeve}"
                               if skill else "")})
    ns_v = nsp.get("verdict") or {}
    ns_pass = int(ns_v.get("n_survivors") or 0) if not ns_v.get("void") else 0
    if nsp:
        ns_gate = nsp.get("gate") or {}
        ns_ce_null = (ns_gate.get("random_p95_inbatch_full") or {}).get("ce")
        ns_sleeve = int(ns_v.get("n_sleeves") or 0)
        steps.append({"stage": "NSP1 新信号设计 · core48 mini 海选",
                      "result": f"{ns_pass} 员候选" if not ns_v.get("void")
                      else "无效（锚点破）",
                      "pass": ns_pass > 0,
                      "note": (f"core48 CE null 首档≈{ns_ce_null}；袖珍 {ns_sleeve}；"
                               f"候选过G1'待G2深化，本批不注册"
                               if ns_ce_null else "")})
    g2n_v = g2n.get("verdicts_g2") or {}
    g2n_pass = sum(1 for v in g2n_v.values() if v.get("g2_pass"))
    if g2n and not g2n.get("void"):
        g2n_x2 = (g2n.get("cost_stress") or {}).get("A_x2") or {}
        g2n_x2s = (g2n_x2.get("full") or {}).get("sharpe")
        steps.append({"stage": "G2_NSP1 深化门 · 两候选±邻域+成本×2",
                      "result": f"{g2n_pass} 员 PASS",
                      "pass": g2n_pass > 0,
                      "note": (f"triple_ma/high252 双双折戟×2成本关"
                               f"（A×2≈{g2n_x2s}），候选归档收线"
                               if g2n_x2s is not None else "")})
    sl_v = slp.get("verdict") or {}
    sl_adm = sl_v.get("sleeve_admission")
    n_p4_surv = None
    if p4b1:
        p4_v = p4b1.get("verdict") or {}
        n_p4_surv = 0 if p4_v.get("void") else int(p4_v.get("n_survivors") or 0)
    sl_schemes = slp.get("schemes") or {}
    if slp and not slp.get("void"):
        n_adm = len(sl_v.get("admitted_schemes") or [])
        b6 = ((sl_schemes.get("B-EW6") or {}).get("x1") or {}).get("full") or {}
        b6x2 = ((sl_schemes.get("B-EW6") or {}).get("x2") or {}).get("full") or {}
        base = ((sl_schemes.get("BASE-EW3") or {}).get("x1") or {}).get("full") or {}
        steps.append({"stage": "SLEEVE_P3 低相关袖并入决策 · 6 袖 vs 在位组合",
                      "result": f"{n_adm}/2 方案 admitted",
                      "pass": bool(sl_adm),
                      "note": (f"最佳 B-EW6 {b6.get('sharpe')} vs 在位 "
                               f"{base.get('sharpe')}，×2≈{b6x2.get('sharpe')}"
                               f" 成本传染+α稀释，池内素材收线"
                               if b6 and base else "")})
    if p2s:
        # P-2 GTJA191 synthesis (bm-b r34): factor V2 thin-pass but strategy
        # G1' 0/3 -- gtja_top5 cleared the i-line yet missed vi by a hair.
        # Live-read from batch JSON (counting single-source, O-2250 T2).
        _p2s_rc = p2s.get("recorded_constants") or {}
        _p2s_n = len(p2s.get("survivors_g1") or [])
        _p2s_cand = len(p2s.get("strategy") or {})
        _p2s_top5 = (((p2s.get("strategy") or {}).get("gtja_top5") or {})
                     .get("full") or {}).get("sharpe")
        steps.append({"stage": "P-2 合成 · GTJA191 因子合成→策略终审",
                      "result": f"{_p2s_n}/{_p2s_cand} 员过 G1'",
                      "pass": _p2s_n > 0,
                      "note": (f"gtja_top5 {_p2s_top5} 过 i 线 "
                               f"{_p2s_rc.get('i_bar')} 差 vi "
                               f"{_p2s_rc.get('vi_bar')} 一线；合成增益在 "
                               f"OOS 端（政体存活），ETF 外部库合成线收线"
                               if _p2s_top5 is not None else "")})
    if p4b1:
        p4_v = p4b1.get("verdict") or {}
        p4_slv = p4b1.get("sleeve_candidates") or []
        p4_ce_line = (p4b1.get("gate") or {}).get("i_bar_ce_used")
        steps.append({"stage": "P-4 动物园批一 · A 层易族 core48 mini 海选",
                      "result": (f"{n_p4_surv} 员候选 · 袖珍 {len(p4_slv)}"
                                 if not p4_v.get("void") else "无效（锚点破）"),
                      "pass": bool(n_p4_surv),
                      "note": (f"低相关素材 {'/'.join(p4_slv) or '无'}；"
                               f"CE i 线取严 {p4_ce_line}；52周低点=接飞刀，"
                               f"批一线诚实收线" if p4_ce_line else "")})
    if gm1:
        # GM-session P-4b1 dual implementation (O-1738 GM lane; R13
        # rename-union kept bm-b's canonical batch above -- this step reads
        # the GM variant's own file, +124 retro-counted real trials).
        # Live-read from batch JSON (counting single-source, O-2250 T2).
        _gm_s = gm1.get("survivors_g1_prime") or []
        _gm_g = gm1.get("gate_g1_prime") or {}
        _gm_tl = gm1.get("trial_ledger") or {}
        steps.append({"stage": "P-4 批一 GM 双实现 · A 层易族（超跌/深水/换手）",
                      "result": f"{len(_gm_s)} 员过 G1'",
                      "pass": bool(_gm_s),
                      "note": (f"双实现 +{_gm_tl.get('this_batch')} 真试验追溯"
                               f"入账；vi={_gm_g.get('vi')}（被动+随机p95抬线）；"
                               f"与 canonical 批一同判 0 幸存")})
    if p5re:
        # P-5 random-entry field check (O-1816 bm-a R13): K=50 starts, all
        # 3 then-registered traders FAILED the 0.70 beat line; drawdown
        # clause all-pass. Live-read from batch JSON (O-2250 T2).
        _p5j = p5re.get("judgment") or {}
        _p5p = p5re.get("pooled") or {}
        _p5t = p5re.get("per_trader") or {}
        _p5_fail = sum(1 for v in _p5t.values()
                       if (v.get("beat_rate_6m") or 0)
                       < (_p5j.get("beat_line_6m") or 1))
        steps.append({"stage": "P-5 随机起点实战检验 · K=50（O-1816）",
                      "result": f"{_p5_fail}/{len(_p5t)} 员 FAIL 跑赢线",
                      "pass": _p5_fail < len(_p5t),
                      "note": (f"跑赢线 {_p5j.get('beat_line_6m')}；pooled "
                               f"{_p5p.get('beat_rate_6m')}；回撤条款全过"
                               f"（最深 {_p5p.get('min_dd_6m')} vs 红线 "
                               f"{_p5j.get('dd_red_line')}）——政体依赖实证，"
                               f"α 成色归纸盘通道")})
    if b2a:
        # P-4 batch 2A TA migration (O-1828 GM lane): 3 G1' candidates
        # (engulf dual-exit + vol_breakout@ce) + 3 sleeve pockets;
        # candidates only, no registration this batch. Live-read (O-2250 T2).
        _b2a_v = b2a.get("verdict") or {}
        _b2a_s = b2a.get("survivors_g1_prime") or []
        _b2a_slv = b2a.get("sleeve_candidates") or []
        steps.append({"stage": "P-4 批 2A · TA 流派迁移海选（O-1828·9 流派）",
                      "result": (f"{_b2a_v.get('n_survivors', len(_b2a_s))} "
                                 f"G1' 候选 · 袖珍 {len(_b2a_slv)}"),
                      "pass": bool(_b2a_s),
                      "note": (f"{'/'.join(_b2a_s[:3])}；确认构造>形态+语境>"
                               f"指标超卖阶梯首证；strong_close/streak 跨域"
                               f"单向门深负；G2 深化另开预注册")})
    n_p4b2_surv = None
    if p4b2:
        n_p4b2_surv = len(p4b2.get("survivors_g1_prime") or [])
        vi_used = (p4b2.get("gate") or {}).get("vi_used") or {}
        steps.append({"stage": "P-4 批二 · 股票池 B 层七族海选（26bp+拒单撮合）",
                      "result": f"{n_p4b2_surv} 员幸存",
                      "pass": n_p4b2_surv > 0,
                      "note": (f"vi={vi_used.get('default')}（被动月度EW+0.10 主导）"
                               f"；七族全深负，打板/短持有线被成本碾压，"
                               f"B 层首开诚实判负" if vi_used else "")})
    if folk:
        # P4_FOLK expansion (O-2134 GM lane): 6 G1' candidates = 3 families
        # dual-exit (needle/drought/duck), ×2 survivors gave the best G2
        # prior in project history -> G2_FOLK followed. Live-read (O-2250 T2).
        _fk_v = folk.get("verdict") or {}
        _fk_s = folk.get("survivors_g1_prime") or []
        _fk_slv = folk.get("sleeve_candidates") or []
        steps.append({"stage": "P4_FOLK · 民间手法大扩容海选（O-2134·26 入场）",
                      "result": (f"{_fk_v.get('n_survivors', len(_fk_s))} "
                                 f"G1' 候选 · 袖珍 {len(_fk_slv)}"),
                      "pass": bool(_fk_s),
                      "note": (f"{'/'.join(_fk_s[:6])}；金针/地量 ×2 已存活="
                               f"史上最优出厂先验；红三兵跨域单向门、"
                               f"MACD 背离民谚降级；候选不注册待 G2")})
    g2f_reg = g2f.get("registered") or []
    if g2f:
        g2f_x3 = sum(1 for v in (g2f.get("verdicts") or [])
                     if (v.get("x3") is not None and skill_bar is not None
                         and v["x3"] >= skill_bar))
        steps.append({"stage": "G2_FOLK 出厂门 · 民间三族深化（邻域+成本×2/×3）",
                      "result": f"{len(g2f_reg)} 员 PASS 注册",
                      "pass": bool(g2f_reg),
                      "note": (f"{'/'.join(g2f_reg)} 过邻域+成本门注册；"
                               f"×3 亦越技能线 {g2f_x3} 员"
                               if g2f_reg else "0 员过门")})
    if p4q:
        # P4_QUEUE oscillator/divergence batch (O-2210): 0 G1' candidates +
        # 2 sleeve pockets (bb_squeeze dual-exit). Verdict laws: oscillator
        # oversold family extinction + divergence double-negative. All
        # live-read from batch JSON (counting single-source, O-2250 T2).
        _qv = p4q.get("verdict") or {}
        _qg = p4q.get("gate") or {}
        _q_slv = p4q.get("sleeve_candidates") or []
        steps.append({"stage": "P4_QUEUE · 振荡/背离排队族海选（O-2210·5 族）",
                      "result": (f"{_qv.get('n_survivors', 0)} G1' 候选 · "
                                 f"袖珍 {len(_q_slv)}"),
                      "pass": bool(_qv.get("n_survivors")),
                      "note": (f"vi={_qg.get('vi_bar_recorded')}；振荡超卖类"
                               f"四族全灭律+背离域双负律入法；袖珍=bb_squeeze"
                               f" 双制（正但差 i 线）")})
    if p5b:
        # P-5B new-trader due diligence (O-2345 bm-a R26): 150 parallel
        # engine runs, 3 new folk traders all FAILED the 0.70 line --
        # regime dependence now proven for all 6 members. Live-read
        # from batch JSON (counting single-source, O-2250 T2).
        _p5bj = p5b.get("judgment") or {}
        _p5bp = p5b.get("pooled") or {}
        _p5bt = p5b.get("per_trader") or {}
        _p5b_fail = sum(1 for v in _p5bt.values()
                        if (v.get("beat_rate_6m") or 0)
                        < (_p5bj.get("beat_line_6m") or 1))
        steps.append({"stage": "P-5B 新员随机起点尽调 · K=50 并行（O-2345）",
                      "result": f"{_p5b_fail}/{len(_p5bt)} 新员 FAIL 跑赢线",
                      "pass": _p5b_fail < len(_p5bt),
                      "note": (f"pooled {_p5bp.get('beat_rate_6m')}；政体依赖"
                               f"实证扩至全员 6/6；回撤条款全过（最深 "
                               f"{_p5bp.get('min_dd_6m')}）——账面 OOS 高分"
                               f"含政体红利，α 成色以纸盘为准")})
    if p4p:
        _pv = p4p.get("verdict") or {}
        _v2 = _pv.get("v2_gate") or {}
        _pl = ((p4p.get("pooled") or {}).get("full") or {}).get("sharpe")
        _np95 = (p4p.get("nulls") or {}).get("p95")
        _line = (_v2.get("skill_line") or {}).get("line")
        _mc = p4p.get("max_corr")
        steps.append({"stage": "P4_PAIRS · 配对协整长多形态（zoo #41·67 跑）",
                      "result": ("v2 过线（G2 另开预注册）" if _pv.get("v2_pass")
                                 else "0 候选收线"),
                      "pass": bool(_pv.get("v2_pass")),
                      "note": (f"池化 {_pl} < v2 线 {_line}，亦低于随机对同构 "
                               f"null p95 {_np95}（协整选择增益为负）；"
                               f"×2 转负；D6 低相关 {_mc}（信息列）")})
    if p4e:
        # P4_EXT_TILT (bm-b r68-69): extension-slot factor survivors failed
        # strategy-level conversion 0/5. Stock-domain own skill line (vi
        # floor 0.561 binding). Live-read from batch JSON (O-2250 T2).
        _ev = p4e.get("survivors") or []
        _eline = (p4e.get("vi") or {}).get("line")
        _ebest_k, _ebest_s = None, None
        for _c in (p4e.get("cells") or []):
            _s = ((_c.get("g1_prime_v2") or {}).get("sharpe_full"))
            if _s is not None and (_ebest_s is None or _s > _ebest_s):
                _ebest_k, _ebest_s = _c.get("key"), _s
        _emu = (p4e.get("null_pool") or {}).get("mu")
        steps.append({"stage": ("P4_EXT_TILT · 扩展槽因子→策略转化"
                                "（gdhs/dzjy·B 层长多倾斜）"),
                      "result": (f"{len(_ev)}/{len(p4e.get('cells') or [])} "
                                 f"员过 G1' v2"),
                      "pass": bool(_ev),
                      "note": (f"vi={_eline}（被动月度EW+0.10 主导·地板绑定）；"
                               f"最优 {_ebest_k} {_ebest_s} 仍差线；随机 null "
                               f"μ={_emu}——股票域摩擦墙：因子级幸存者"
                               f"≠策略级可转化")})
    ctap = _read_json(os.path.join(res, "shortline_cta_p1.json")) or {}
    if ctap:
        # CTA_P1 futures screen (bm-a R50): 0/16 honest close, futures-domain
        # own skill line (never core48 constants). All values live-read from
        # the batch JSON, counting single-source rule (O-2250 T2).
        _cl = ctap.get("skill_line") or {}
        _passers = ctap.get("g1_passers") or []
        _vg1 = ctap.get("verdicts_g1") or {}
        _best_k, _best_s = None, None
        for _k, _v in _vg1.items():
            _s = _v.get("sharpe_full")
            if _s is not None and (_best_s is None or _s > _best_s):
                _best_k, _best_s = _k, _s
        _np95 = ((ctap.get("nulls") or {}).get("summary") or {}).get("p95")
        _ncand = len(_vg1) or len(ctap.get("candidates") or [])
        steps.append({"stage": "CTA_P1 · 期货 CTA 海选（C 层首开·9 品种主力连续）",
                      "result": f"{len(_passers)}/{_ncand} 员过 G1' v2",
                      "pass": bool(_passers),
                      "note": (f"期货域技能线 {_cl.get('line')}=全项目最高域线"
                               f"（被动 {_cl.get('passive_term')} 主导）；最优 "
                               f"{_best_k} {_best_s} 超随机带 p95 {_np95}"
                               f" 但差线收线（律8 成本结构刻度）" if _cl else "")})
    ctap2 = _read_json(os.path.join(res, "shortline_cta_p2_noau.json")) or {}
    if ctap2:
        # CTA_P2_NOAU (bm-a R53): AU-drop mechanism decomposition, 0/16 honest
        # close. All values live-read from the batch JSON (O-2250 rule).
        _cl2 = ctap2.get("skill_line") or {}
        _p2 = ctap2.get("g1_passers") or []
        _vg2 = ctap2.get("verdicts_g1") or {}
        _b2k, _b2s = None, None
        for _k, _v in _vg2.items():
            _s = _v.get("sharpe_full")
            if _s is not None and (_b2s is None or _s > _b2s):
                _b2k, _b2s = _k, _s
        _p1b = None
        for _v in ((ctap.get("verdicts_g1") or {}) if ctap else {}).values():
            _s = _v.get("sharpe_full")
            if _s is not None and (_p1b is None or _s > _p1b):
                _p1b = _s
        steps.append({"stage": "CTA_P2_NOAU · 期货 CTA 复评（剔 AU 机制分解·8 品种）",
                      "result": f"{len(_p2)}/{len(_vg2)} 员过 G1' v2",
                      "pass": bool(_p2),
                      "note": (f"AU-β 嫌疑推翻：剔 AU 最优 {_b2k} {_b2s} "
                               f"未塌陷（vs 全9品种批 {_p1b}）；技能线 "
                               f"{_cl2.get('line')} 新高（律9 判线=宇宙宽度"
                               f"刻度·σ抬线）；CTA 复活收窄至 P1 署名门"
                               if _cl2 else "")})
    return {"steps": steps, "trials_total": trials_total,
            "n_g1_prime": len(surv), "n_g2": g2_pass, "n_lowchurn": lc_pass,
            "n_j19": ct_pass, "n_lfc": lfc_pass, "n_nsp": ns_pass,
            "n_g2nsp": g2n_pass,
            "n_sleeve_p3": (None if sl_adm is None else int(bool(sl_adm))),
            "n_p4b1": n_p4_surv, "n_p4b1_sleeve": (
                len(p4b1.get("sleeve_candidates") or []) if p4b1 else None),
            "n_p4b2": n_p4b2_surv,
            "n_traders": len(traders),
            "trader_ids": traders}

def _paper_state() -> dict:
    """Paper tracking state from results/paper/*_paper.json (live.paper output).

    started = pipeline has run and the anchor gate passed for >=1 trader
    (evidence accrual live); trades = window trades to date (0 until the
    hire-date bars start flowing). No hard-coded flags.
    """
    out = {"started": False, "n_active": 0, "months_tracked": 0,
           "trades": 0, "bars": 0, "last_update": None,
           "paper_start": None, "first_check": None, "month_progress": None,
           "x2_probation": 0, "x2_probation_names": []}
    d = os.path.join(PATHS.results_dir, "paper")
    if not os.path.isdir(d):
        return out
    for f in sorted(os.listdir(d)):
        if not f.endswith("_paper.json"):
            continue
        s = _read_json(os.path.join(d, f))
        if not s or not s.get("anchor_ok"):
            continue
        out["started"] = True
        out["n_active"] += 1
        x2w = s.get("x2_watch") or {}
        if x2w.get("probation"):
            out["x2_probation"] += 1
            tid = str(s.get("trader") or f[:-len("_paper.json")])
            out["x2_probation_names"].append(tid)
        out["months_tracked"] += int(s.get("months_tracked", 0))
        out["bars"] += int(s.get("bars", 0))
        wm = s.get("window_metrics") or {}
        out["trades"] += int(wm.get("num_trades", 0) or 0)
        u = s.get("updated")
        if u and (out["last_update"] is None or u > out["last_update"]):
            out["last_update"] = u
        ps = s.get("paper_start")
        if ps and (out["paper_start"] is None or ps < out["paper_start"]):
            out["paper_start"] = ps
    if out["paper_start"]:
        _add_month_progress(out)
    return out


def _scorecard_state() -> dict:
    """P-6 strategy scorecard (T-2026-09-23-07, framework firm/STRATEGY_EVALUATION.md).

    Reads results/scorecard_v1.json (scripts/scorecard.py output); report-only
    evaluation layer -- hr.py stays the sole level-mutation authority.
    Missing file = honest 'pending'; no hard-coded trader names/counts.
    v2 three-card face (T-2026-09-25-63 / O-20260925-1755): also reads
    results/strategy_scorecard.json (strategy/trader/portfolio cards);
    trader/portfolio composites render only after SCORECARD_CALIB_P1 frozen
    bands consumed (audit.calibration_consumed face, charter sec 8.5);
    discipline veto hits surface immediately.
    """
    out = {"present": False, "n_traders": None, "grade_counts": None,
           "best": None, "generated": None, "status": "none", "text": "记分卡待产出"}
    three = _read_json(os.path.join(PATHS.results_dir, "strategy_scorecard.json"))
    tsum = three.get("summary") or {} if three else {}
    vetoes = three.get("discipline_veto_hits") or {} if three else {}
    out["three_card"] = {"present": False} if not three else {
        "present": True, "generated": three.get("generated"),
        "n_strategy_cards": tsum.get("n_strategy_cards"),
        "n_trader_cards": tsum.get("n_trader_cards"),
        "n_portfolio_cards": tsum.get("n_portfolio_cards"),
        "calibration_state": ("calibrated (SCORECARD_CALIB_P1 frozen bands)"
                              if (three.get("audit") or {}).get("calibration_consumed")
                              else "pre-calibration readout (sec 8.5)"),
        "discipline_veto_hits": vetoes,
        "text": (f"三卡: 策略{tsum.get('n_strategy_cards')} "
                 f"交易员{tsum.get('n_trader_cards')} "
                 f"组合{tsum.get('n_portfolio_cards')}"
                 + (" | 总分分级已启用(冻结带)"
                    if (three.get("audit") or {}).get("calibration_consumed") else "")
                 + (f" | 纪律否决 {len(vetoes)}" if vetoes else " | 纪律否决 0")),
    }
    s = _read_json(os.path.join(PATHS.results_dir, "scorecard_v1.json"))
    if not s:
        return out
    summ = s.get("summary") or {}
    out["present"] = True
    out["n_traders"] = summ.get("n_traders")
    out["grade_counts"] = summ.get("grade_counts")
    out["generated"] = s.get("generated")
    best = summ.get("best") or {}
    out["best"] = best
    stale_days = None
    try:
        g = dt.datetime.fromisoformat(s["generated"])
        stale_days = (dt.datetime.now() - g).days
    except (KeyError, ValueError):
        pass
    out["stale_days"] = stale_days
    if out["n_traders"]:
        gc = out["grade_counts"] or {}
        out["status"] = "ok"
        out["text"] = (f"记分卡 {out['n_traders']} 员评级 "
                       f"S×{gc.get('S', 0)} A×{gc.get('A', 0)} "
                       f"B×{gc.get('B', 0)} C×{gc.get('C', 0)}")
    else:
        out["status"], out["text"] = "warn", "记分卡空员"
    return out


def _next_month(y, m):
    m += 1
    if m > 12:
        y, m = y + 1, 1
    return y, m


def _add_month_progress(out):
    """Progress toward the first paper promotion check.

    firm/hr.py whole-month rule: a month only counts when its first day falls
    on/after paper_start, so the first check lands at the end of the first
    such month (e.g. hire 2026-09-23 -> check 2026-10-31). Derived, not stored:
    when hr's paper_months_min changes, only this derivation tracks it.
    """
    try:
        p = dt.date.fromisoformat(out["paper_start"])
    except ValueError:
        return
    y, m = (p.year, p.month) if p.day == 1 else _next_month(p.year, p.month)
    nxt = _next_month(y, m)
    first_check = dt.date(nxt[0], nxt[1], 1) - dt.timedelta(days=1)
    out["first_check"] = first_check.isoformat()
    span = (first_check - p).days
    if span <= 0:
        out["month_progress"] = 1.0
    else:
        elapsed = (dt.date.today() - p).days
        out["month_progress"] = round(max(0.0, min(1.0, elapsed / span)), 4)


# ---- group (parallel-managed sibling projects, e.g. Biggame game lines) ----
# Paths are machine-local: absent on other machines -> panel degrades gracefully.
# Migration-portable (O-20260926-2000-bm-c): roots carry old+new candidates;
# first existing wins so the panel survives the E:\Minigame -> E:\Fluxgroup\MiniGame move.
_SIBLINGS = [
    {"name": "Biggame · biu你一下", "roots": [r"E:\Minigame\BiuNiYiXia\Logs", r"E:\Fluxgroup\MiniGame\BiuNiYiXia\Logs"]},
    {"name": "Biggame · HomeWreck", "roots": [r"E:\Minigame\HomeWreck\Logs", r"E:\Fluxgroup\MiniGame\HomeWreck\Logs"]},
    {"name": "Biggame · PhantomEscapeGo", "roots": [r"E:\Minigame\PhantomEscapeGo\Logs", r"E:\Fluxgroup\MiniGame\PhantomEscapeGo\Logs"]},
]
_GROUP_ALIVE_MIN = 30  # sibling loops run at 1-10 min cadence


_FLEET_STALE_WARN_MIN = 30   # heartbeat older -> yellow (loop cadence is 10 min)
_FLEAT_STALE_BAD_MIN = 120  # heartbeat older -> red


def _fleet_state() -> dict:
    """Fleet distributed-monitor state for dashboard.html (J10).

    Sources (all git-synced real files; each machine writes only its own
    heartbeat per fleet/README.md, so every node sees the whole fleet):
      - fleet/machines/*.json        : per-machine heartbeats
      - logs/iteration-loop/state*.json : per-machine OS-loop round numbers
        (bm-b keeps the legacy name state.json, others state-<id>.json)
      - fleet/tasks/T-*.json         : claim-lock task tickets
      - results/compute_audit.json   : latest audit sample (writer machine mixes)
      - results/ext_slots_pull_status.json + results/p1d_gates.json : P-1d chain
    Missing/absent files degrade to honest placeholders, never mock numbers.
    """
    out = {"present": False, "machines": [], "tickets": [],
           "n_open": 0, "n_claimed": 0, "n_done": 0,
           "audit": None, "p1d": None}
    now = dt.datetime.now()
    fdir = os.path.join(PATHS.root, "fleet", "machines")
    if os.path.isdir(fdir):
        for f in sorted(os.listdir(fdir)):
            if not f.endswith(".json"):
                continue
            m = _read_json(os.path.join(fdir, f))
            if not m:
                continue
            mid = m.get("machine_id") or f[:-5]
            age_min = None
            ep = m.get("heartbeat_epoch_utc")
            if isinstance(ep, (int, float)) and ep > 0:
                age_min = round(max(0.0, (dt.datetime.now().timestamp() - ep) / 60), 1)
            sfile = "state.json" if mid == "bm-b" else f"state-{mid}.json"
            st = _read_json(os.path.join(PATHS.logs_dir, "iteration-loop", sfile))
            if age_min is None:
                health = "unknown"
            elif age_min <= _FLEET_STALE_WARN_MIN:
                health = "ok"
            elif age_min <= _FLEAT_STALE_BAD_MIN:
                health = "warn"
            else:
                health = "bad"
            out["machines"].append({
                "id": mid,
                "last_seen": m.get("last_seen"),
                "age_min": age_min,
                "health": health,
                "cpu_cores": m.get("cpu_cores"),
                "idle_ram_gb": m.get("idle_ram_gb"),
                "gpu_idle_vram_mb": m.get("gpu_idle_vram_mb"),
                "current_task": m.get("current_task"),
                "verdict": m.get("verdict"),
                "orders_ack": m.get("orders_ack"),
                "clock_read": m.get("clock_read"),
                "round_no": (st or {}).get("round_no"),
            })
        out["present"] = bool(out["machines"])
    tdir = os.path.join(PATHS.root, "fleet", "tasks")
    if os.path.isdir(tdir):
        for f in sorted(os.listdir(tdir)):
            if not (f.startswith("T-") and f.endswith(".json")):
                continue
            t = _read_json(os.path.join(tdir, f))
            if not t:
                continue
            status = str(t.get("status") or "open")
            if status == "done":
                out["n_done"] += 1
            elif status == "claimed":
                out["n_claimed"] += 1
            else:
                out["n_open"] += 1
            out["tickets"].append({
                "id": t.get("id") or f[:-5],
                "type": t.get("type"),
                "priority": t.get("priority"),
                "status": status,
                "claimed_by": t.get("claimed_by"),
            })
    au = _read_json(os.path.join(PATHS.results_dir, "compute_audit.json"))
    if au and au.get("latest"):
        la = au["latest"]
        g = la.get("gpu") or {}
        out["audit"] = {
            "ts": la.get("ts"), "verdict": la.get("verdict"),
            "flags": la.get("flags") or [],
            "cpu_total_pct": la.get("cpu_total_pct"),
            "py_cpu_pct": la.get("py_cpu_pct"),
            "cores": la.get("cores"), "py_procs": la.get("py_procs"),
            "zombies": len(la.get("zombies") or []),
            "gpu_util_pct": g.get("util_pct"),
            "gpu_mem_used_mb": g.get("mem_used_mb"),
            "rogue_apps": g.get("rogue_apps") or [],
        }
    pull = _read_json(os.path.join(PATHS.results_dir, "ext_slots_pull_status.json"))
    gates = _read_json(os.path.join(PATHS.results_dir, "p1d_gates.json"))
    if pull or gates:
        legs = (pull or {}).get("legs") or {}
        gd = {k: (gates or {}).get(k) or {} for k in ("dzjy", "gdhs", "margin")}
        out["p1d"] = {
            "pull_updated": (pull or {}).get("updated"),
            "legs": {
                k: {"chunks": v.get("chunks"), "rows": v.get("rows"),
                    "done": bool(v.get("done")),
                    "failures": len(v.get("failures") or [])}
                for k, v in legs.items()},
            "gates": {k: {"coverage": v.get("coverage") or
                          (v.get("valid_quarters") and
                           f"{v.get('valid_quarters')}/{v.get('expected_quarters')}"),
                      "gate": v.get("gate"), "pass": v.get("pass")}
                      for k, v in gd.items()},
            "gates_date": (gates or {}).get("meta", {}).get("date"),
        }
    lhb = _read_json(os.path.join(PATHS.results_dir, "lhb_update_status.json"))
    if lhb:
        out["lhb"] = {"verdict": lhb.get("verdict"),
                      "cutoff": lhb.get("cutoff"),
                      "updated": lhb.get("updated"),
                      "new_rows": lhb.get("new_rows")}
    return out


def _group() -> dict:
    now = dt.datetime.now()

    def _newest_mtime(root: str):
        newest = None
        for dirpath, _dirs, files in os.walk(root):
            for fn in files:
                try:
                    m = os.path.getmtime(os.path.join(dirpath, fn))
                except OSError:
                    continue
                if newest is None or m > newest:
                    newest = m
        return newest

    sibs = []
    for s in _SIBLINGS:
        root = next((r for r in s["roots"] if os.path.isdir(r)), None)
        if root is None:
            continue  # machine without sibling sources: hide silently
        m = _newest_mtime(root)
        if m is None:
            continue
        age = (now - dt.datetime.fromtimestamp(m)).total_seconds() / 60
        sibs.append({"name": s["name"],
                     "last_active": dt.datetime.fromtimestamp(m).strftime("%m-%d %H:%M"),
                     "age_min": round(age, 1), "alive": age <= _GROUP_ALIVE_MIN})
    self_m = _newest_mtime(os.path.join(PATHS.logs_dir, "iteration-loop"))
    if self_m is not None:
        age = (now - dt.datetime.fromtimestamp(self_m)).total_seconds() / 60
        sibs.append({"name": "Bigmoney · 回测节点（本机）",
                     "last_active": dt.datetime.fromtimestamp(self_m).strftime("%m-%d %H:%M"),
                     "age_min": round(age, 1), "alive": age <= _GROUP_ALIVE_MIN})
    return {"siblings": sibs}


def _traders() -> list:
    out = []
    d = os.path.join(PATHS.root, "firm", "traders")
    for f in sorted(os.listdir(d)):
        if not f.endswith(".json") or f.startswith("_"):
            continue
        t = _read_json(os.path.join(d, f))
        if not t:
            continue
        if t.get("level") == "PROSPECT":
            continue   # T-24: observation tier -- wall = registered roster
        bt = t.get("backtest") or {}
        pp = t.get("paper") or {}
        out.append({
            "id": t.get("id"), "name": t.get("name"),
            "school": t.get("school"), "level": t.get("level"),
            "allocation_pct": t.get("live", {}).get("allocation_pct", 0),
            "is_sharpe": (bt.get("in_sample") or {}).get("sharpe"),
            "oos_sharpe": (bt.get("out_sample") or {}).get("sharpe"),
            "oos_trades": (bt.get("out_sample") or {}).get("trades"),
            "cost_x2_sharpe": (bt.get("cost_x2") or {}).get("sharpe"),
            "cost_x2_survive": (bt.get("cost_x2") or {}).get("survive"),
            "paper_months": pp.get("months_tracked"),
            "paper_as_of": pp.get("as_of"),
        })
    return out


def _prospect_state() -> dict:
    """T-24 PROSPECT pool line: observation members (level=PROSPECT in
    firm/traders) + anchor-repro batch state + paper-tracking lane state
    (slice-a: results/prospect_paper/_summary.json). Distinct from the
    registered 6 by construction (allocation permanently 0)."""
    out = {"count": 0, "ids": [], "anchor_pass": None, "anchor_complete": None,
           "batch": "none", "paper": None}
    d = os.path.join(PATHS.root, "firm", "traders")
    for f in sorted(os.listdir(d)):
        if not f.endswith(".json") or f.startswith("_"):
            continue
        t = _read_json(os.path.join(d, f))
        if t and t.get("level") == "PROSPECT":
            out["count"] += 1
            out["ids"].append(t.get("id", f[:-5]))
    b = _read_json(os.path.join(PATHS.results_dir, "t24_prospect_onboard.json"))
    if b:
        out["anchor_pass"] = b.get("n_pass")
        out["anchor_complete"] = b.get("complete")
        out["batch"] = b.get("batch", "none")
    s = _read_json(os.path.join(PATHS.results_dir, "prospect_paper",
                                "_summary.json"))
    if s:
        out["paper"] = {"n_pass": s.get("n_pass"),
                        "n_drift": s.get("n_drift"),
                        "months_total": s.get("months_total"),
                        "data_cutoff": s.get("data_cutoff"),
                        "generated": s.get("generated"),
                        "window_semantics": s.get("window_semantics")}
    g = _read_json(os.path.join(PATHS.results_dir, "prospect_promotion",
                                "_summary.json"))
    if g:
        out["promotion"] = {"n_eligible": g.get("n_eligible"),
                            "n_members": g.get("n_members"),
                            "leg_pass": g.get("leg_pass"),
                            "generated": g.get("generated")}
    return out


def _risk_lines() -> list:
    from config import RISK
    e = ExitConfig()
    return [
        f"单标的仓位 ≤ {RISK.max_position_pct:.0%}",
        f"总仓位 ≤ {RISK.max_total_pct:.0%}",
        f"单日亏损 {RISK.daily_loss_limit:.0%} 停开新仓",
        f"硬止损 {e.initial_stop:.0%}",
        f"亏损 {e.loss_time_days} 天强制清仓",
        f"持仓硬上限 {e.global_hard_limit} 天",
    ]


def _achievements(bt: dict, data: dict, smoke: dict, n_traders: int,
                  paper: dict) -> list:
    return [
        {"name": "数据就绪", "icon": "coin", "unlocked": data["fresh"] and data["n_core"] >= 40},
        {"name": "因子库建立", "icon": "gem", "unlocked": True},
        {"name": "回测引擎修复", "icon": "heart", "unlocked": smoke["ok"]},
        {"name": "持仓铁律", "icon": "heart", "unlocked": True},
        {"name": "首个策略过线", "icon": "star", "unlocked": n_traders > 0},
        {"name": "纸盘首笔交易", "icon": "coin", "unlocked": paper["trades"] > 0},
        {"name": "实盘上线", "icon": "dragon", "unlocked": False},
    ]


def _governance_state() -> dict:
    """Governance visibility (总经办 mandate): science-audit M-layer
    (O-2215 monthly) + monthly briefing (O-2205 ⑨). Audit findings are
    report-only by design — surface as warn, never bad; absence honest."""
    st = _read_json(os.path.join(PATHS.results_dir, "science_audit.json")) or {}
    cur = st.get("current") or {}
    summ = cur.get("summary") or {}
    verdicts = [v for v in summ.values() if isinstance(v, str)]
    n_checks = len(verdicts)
    n_ok = sum(1 for v in verdicts if v == "OK")
    findings = summ.get("n_findings")
    if findings is None and cur.get("checks"):
        findings = sum(1 for c in cur["checks"]
                       if str(c.get("verdict")) not in ("OK", "", "None"))
    a_gen = cur.get("generated")
    a_age_min = None
    try:
        a_age_min = int((dt.datetime.now()
                         - dt.datetime.fromisoformat(str(a_gen))).total_seconds() // 60)
    except Exception:
        pass
    audit = {"present": bool(cur), "generated": a_gen,
             "age_days": None if a_age_min is None else a_age_min // 1440,
             "checks": n_checks, "ok": n_ok, "findings": findings,
             "ledger_head": (cur.get("ledger_head") or {}).get("total")}
    b_month = None
    b_generated = None
    try:
        cands = sorted(glob.glob(os.path.join(PATHS.results_dir, "briefings",
                                               "BRIEF-*.md")))
        if cands:
            name = os.path.basename(cands[-1])
            if name.startswith("BRIEF-") and len(name) >= 12:
                b_month = f"{name[6:10]}-{name[10:12]}"
            with open(cands[-1], encoding="utf-8") as f:
                for line in f:
                    if line.startswith("##"):
                        break
                    if "生成时间" in line and "：" in line:
                        b_generated = line.split("：", 1)[1].split("（")[0].strip()
                        break
    except Exception:
        pass
    today = dt.date.today()
    prev_month = (today.replace(day=1) - dt.timedelta(days=1)).strftime("%Y-%m")
    stale = b_month is not None and b_month < prev_month
    briefing = {"present": b_month is not None, "month": b_month,
                 "generated": b_generated, "stale": stale}
    out = {"present": audit["present"] or briefing["present"],
           "audit": audit, "briefing": briefing,
           "status": "none", "text": "治理面待产出"}
    if audit["present"] and briefing["present"]:
        bad = bool(findings) or n_ok < n_checks or stale
        out["status"] = "warn" if bad else "ok"
        out["text"] = f"审计 {n_ok}/{n_checks} OK · findings {findings} · 简报 {b_month}"
    elif audit["present"]:
        out["status"] = "warn"
        out["text"] = f"审计 {n_ok}/{n_checks} OK · 简报待产出"
    elif briefing["present"]:
        out["status"] = "warn"
        out["text"] = f"科学审计待产出 · 简报 {b_month}"
    return out


_QUEUE_ARM_CN = {
    "portfolio-construction": "组合构建",
    "synthesis-crosslib": "跨库合成",
    "patterns-confirmation": "形态确认",
    "event-attention-factors": "事件注意力",
    "trend-timeseries": "趋势时序",
    "stock-pool-tilt": "股票池倾斜",
    "futures-cta": "期货CTA",
    "pairs-cointegration": "配对协整",
    "low-freq-asset": "低频品种",
    "regime-defense": "行情防线",
}


def _queue_bandit_state() -> dict:
    """Batch-queue bandit scheduler visibility (QUEUE_BANDIT v1, bm-a R62;
    O-1819 queue-never-empties mechanization). Advisory-only surface: UCB1
    lane ordering + candidate registry. Scheduler never initiates batches;
    every batch still needs prereg + claim (research/QUEUE_BANDIT.md §0)."""
    st = _read_json(os.path.join(PATHS.results_dir, "bandit_queue.json")) or {}
    arms = st.get("arms")
    if not arms:
        return {"present": False, "status": "none", "text": "队列排程待产出"}
    order = st.get("ucb1_policy_order") or []
    exploit = st.get("exploit_ranking") or []
    cands = st.get("engineering_candidates") or []
    tried = [k for k, a in arms.items() if a.get("n_pulls")]
    total_pulls = sum(int(a.get("n_pulls") or 0) for a in arms.values())
    positive = [k for k, a in arms.items() if (a.get("mean_reward") or 0) > 0]
    n_open = sum(1 for c in cands if c.get("status") == "open")
    n_gated = sum(1 for c in cands
                  if str(c.get("status", "")).startswith("gated"))
    next_lane = order[0] if order else None
    best_exploit = exploit[0] if exploit else None
    next_txt = _QUEUE_ARM_CN.get(next_lane, next_lane) if next_lane else "—"
    next_tag = ""
    if next_lane and not arms.get(next_lane, {}).get("n_pulls"):
        next_tag = "（未试）"
    pos_txt = "/".join(_QUEUE_ARM_CN.get(k, k) for k in positive) if positive else "无"
    return {
        "present": True,
        "generated": st.get("generated"),
        "schema": st.get("schema"),
        "n_arms": len(arms),
        "tried_arms": len(tried),
        "total_pulls": total_pulls,
        "next_lane": next_lane,
        "next_lane_cn": next_txt + next_tag,
        "best_exploit": best_exploit,
        "best_exploit_cn": (_QUEUE_ARM_CN.get(best_exploit, best_exploit)
                            if best_exploit else "—"),
        "positive_arms": positive,
        "positive_arms_cn": pos_txt,
        "n_open_candidates": n_open,
        "n_gated_candidates": n_gated,
        "unmapped_batches": len(st.get("unmapped_batches") or []),
        "evidence_cutoff": st.get("evidence_cutoff"),
        "status": "ok",
        "text": (f"下一 {next_txt}{next_tag} · 正收益 {pos_txt}"
                 f" · 开放{n_open} · P1门{n_gated}"),
    }


def _alloc_paper_state() -> dict:
    """O-20260925-1145 v5 asset-allocation research line: ALLOC-* forward
    paper accounts (results/alloc_paper/, T-66 s2 wiring). Read-only marks
    lane mirroring frozen s2 cells 1:1 — observation only, never enters the
    CEO scorecard/admission faces (three-line law: allocation face judgements
    are never borrowed by trading J-line or AGGR faces)."""
    out = {"present": False, "n_accounts": 0, "accounts": [],
           "capital_initial_cny": None, "inception_date": None,
           "cutoff_frozen": None, "latest_asof": None}
    d = os.path.join(PATHS.results_dir, "alloc_paper")
    if not os.path.isdir(d):
        return out
    first = None
    for f in sorted(os.listdir(d)):
        if not (f.startswith("ALLOC-") and f.endswith(".json")):
            continue
        j = _read_json(os.path.join(d, f))
        if not j:
            continue
        if first is None:
            first = j
        nav = j.get("latest_nav_cny")
        cap = j.get("capital_initial_cny")
        series = j.get("nav_series") or []
        asof = series[-1][0] if series else None
        stale = (j.get("data_quality") or {}).get("stale_leg_days") or {}
        out["accounts"].append({
            "id": j.get("account", f[:-5]),
            "latest_nav_cny": nav,
            "ret_pct": (nav / cap - 1.0) if (nav and cap) else None,
            "n_bars": j.get("n_bars"),
            "n_trades": j.get("n_trades"),
            "total_cost_cny": j.get("total_cost_cny"),
            "mode": j.get("mode"),
            "stale_leg_max": max(stale.values()) if stale else 0,
            "asof": asof,
        })
        if asof and (out["latest_asof"] is None or asof > out["latest_asof"]):
            out["latest_asof"] = asof
    if out["accounts"]:
        out["present"] = True
        out["n_accounts"] = len(out["accounts"])
        if first:
            out["capital_initial_cny"] = first.get("capital_initial_cny")
            out["inception_date"] = first.get("inception_date")
            out["cutoff_frozen"] = first.get("cutoff_frozen")
    return out


def build() -> dict:
    smoke = _smoke_health()
    data = _data_freshness()
    data["update"] = _update_state()
    data["heat"] = _heat_state()
    data["futures"] = _futures_state()
    data["moneyflow"] = _moneyflow_state()
    data["token"] = _token_state()
    data["watermark"] = _watermark_state()
    data["autofill"] = _autofill_state()
    data["saturation"] = _saturation_state()
    data["regime"] = _regime_state()
    data["portfolio"] = _portfolio_state()
    data["corr_watch"] = _corr_watch_state()
    data["governance"] = _governance_state()
    data["queue_bandit"] = _queue_bandit_state()
    data["alloc_paper"] = _alloc_paper_state()
    bt = _backtest_summary()
    chain = _gate_chain(bt)
    paper = _paper_state()
    fx = ExitConfig()
    payload = {
        "meta": {
            "company": "BIGMONEY 对冲基金",
            "stage": "筹备期 · Pre-Seed",
            "capital": 1_000_000,
            "nav": 1.0,
            "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        },
        "health": {"smoke": smoke, "network": _network()},
        "data": data,
        "fleet": _fleet_state(),
        "research": {"factor_top": _factor_top(),
                     "composite_plan": COMPOSITE_PLAN,
                     "factor_line": _factor_line()},
        "strategy": {**bt, "gate_chain": chain["steps"],
                     "trials_total": chain["trials_total"],
                     "n_traders": chain["n_traders"],
                     "ranking": _ranking_rows()},
        "risk": _risk_lines(),
        "trading": {"traders": _traders(),
                    "levels": ["PROSPECT", "INTERN", "TRAINEE", "TRADER",
                               "SENIOR", "PRINCIPAL"],
                    "prospect": _prospect_state(),
                    "paper_started": paper["started"],
                    "paper": paper,
                    "scorecard": _scorecard_state()},
        "gamification": {},
        "events": [],
        "group": _group(),
    }
    payload["gamification"]["achievements"] = _achievements(
        bt, data, smoke, chain["n_traders"], paper)
    payload["gamification"]["milestones_done"] = sum(
        1 for a in payload["gamification"]["achievements"] if a["unlocked"])
    payload["gamification"]["milestones_total"] = len(payload["gamification"]["achievements"])
    slp_txt = "" if chain["n_sleeve_p3"] is None else (
        f" → SLEEVE_P3 袖并入{'过' if chain['n_sleeve_p3'] else '收线'}")
    p4_txt = "" if chain["n_p4b1"] is None else (
        f" → P-4 动物园批一 {chain['n_p4b1']}候选·袖{chain['n_p4b1_sleeve']}")
    p4b2_txt = "" if chain["n_p4b2"] is None else (
        f" → P-4 批二股票池 {chain['n_p4b2']}员幸存")
    payload["events"] = [
        {"time": smoke["at"] or "-", "text": f"自检 {smoke['pass']}项通过/{smoke['fail']}失败"},
        {"time": "-", "text": f"门禁链定案（试验账本 N={chain['trials_total']}）："
                              f"432基线灭 → G1' {chain['n_g1_prime']}员 → G2 {chain['n_g2']} → "
                              f"J14 {chain['n_lowchurn']} → J15 1员 → J19 {chain['n_j19']}员"
                              f" → LFC 债金池 {chain['n_lfc']}员"
                              f" → NSP1 新信号 {chain['n_nsp']}候选"
                              f" → G2_NSP1 深化 {chain['n_g2nsp']}员"
                              f"{slp_txt}"
                              f"{p4_txt}"
                              f"{p4b2_txt}"
                              f"（累计 {chain['n_traders']} 员注册编制）"},
    ]
    if chain["trader_ids"]:
        payload["events"].insert(1, {
            "time": "-", "text": f"交易员 {'/'.join(chain['trader_ids'])} 过全 G2 门禁链持证上岗（INTERN）· "
                                 + ("paper 跟踪进行中，≥6 个月才可谈实盘" if paper["started"]
                                    else "paper 跟踪启动前不进实盘")})
    _pros = payload["trading"]["prospect"]
    if _pros["count"]:
        _anch = "?" if _pros["anchor_pass"] is None else _pros["anchor_pass"]
        _trk = ""
        if _pros.get("paper"):
            _trk = (f" · 纸面跟踪道已接线（过 {_pros['paper']['n_pass']}"
                    f"/{_pros['count']}·漂移 {_pros['paper']['n_drift']}"
                    f"·月账累积 {_pros['paper']['months_total']}）")
        _gate = ""
        if _pros.get("promotion"):
            _p = _pros["promotion"]
            _lp = _p.get("leg_pass") or {}
            _gate = (f" · 晋升门评估 {_p['n_eligible']}/{_p['n_members']}"
                     f" 达标（腿：纸面 {_lp.get('paper_months', 0)}"
                     f"/{_p['n_members']}·G2包 {_lp.get('g2_full', 0)}"
                     f"/{_p['n_members']}·T-22 {_lp.get('t22_beat_passive', 0)}"
                     f"/{_p['n_members']}）")
        payload["events"].insert(2, {
            "time": "-", "text": f"PROSPECT 观察池 {_pros['count']} 员入场（T-24 首批，配置恒 0）· "
                                 f"anchor-repro {_anch}/{_pros['count']} 通过"
                                 + ("" if _pros["anchor_complete"] else "（批在途）")
                                 + _trk + _gate
                                 + "· 晋升 INTERN 须全 G2+T-22 0.70 门禁不放宽"})
    if paper["started"]:
        payload["events"].insert(2, {
            "time": paper["last_update"] or "-",
            "text": f"paper 跟踪进行中 · {paper['n_active']} 员在册 · 累计 "
                    f"{paper['months_tracked']} 个月 · 窗口 {paper['trades']} 笔"
                    f"（每日自动 accrue · 锚定门禁先行）"})
        if paper["x2_probation"]:
            payload["events"].insert(3, {
                "time": paper["last_update"] or "-",
                "text": f"x2 看守 · {paper['x2_probation']} 员薄垫看护（"
                        f"{'/'.join(paper['x2_probation_names'])}）· "
                        f"margin<0.05 或不存活即 probation（T-04 F3 升级链）"})
    tail_events = []
    if data["update"]["present"]:
        tail_events.append({
            "time": data["update"]["last_run"] or "-",
            "text": f"数据链 · 日线更新 {data['update']['symbols']} 符号 · 新增 "
                    f"{data['update']['total_new_rows']} 行 · 失败 {data['update']['failures']}"
                    f" · cutoff {data['update']['data_cutoff']}"})
    heat = data["heat"]
    if heat["present"]:
        era_txt = (f" · era {heat['era_min']}→{heat['era_max']}"
                   if heat["era_min"] and heat["era_max"] else "")
        tail_events.append({
            "time": max(str(t) for t in (heat["l1_updated"], heat["l2_updated"]) if t) or "-",
            "text": f"热度链 · L1 人气榜快照 {heat['l1_snapshots'] or 0} 份 · L2 回填 "
                    f"{heat['l2_done'] if heat['l2_done'] is not None else '—'}/"
                    f"{heat['l2_target'] or 0} 件 · 拒 {heat['l2_rejects']}"
                    f"（真短史）{era_txt}"})
    fu = data["futures"]
    if fu["present"]:
        age_h = None if fu["age_min"] is None else fu["age_min"] // 60
        age_txt = "—" if age_h is None else (f"{age_h}h 前" if age_h else "刚跑")
        tail_events.append({
            "time": fu["last_attempt"] or "-",
            "text": f"期货链 · C 层 {fu['varieties']} 品种主力连续 · "
                    f"{fu['rows_total'] // 1000}k 行 · cutoff {fu['cutoff'] or '—'} · {age_txt}"})
    mf = data["moneyflow"]
    if mf["present"]:
        tail_events.append({
            "time": mf["last_attempt"] or "-",
            "text": f"数据链 · {mf['text']}（MF_COLLECTOR 前向 · bm-a R63）"})
    tok = data["token"]
    if tok["present"]:
        tail_events.append({
            "time": tok["generated"] or "-",
            "text": f"本地化 · token 粗估 状态 {tok['state_est']} · 报告 {tok['report_est']}"
                    f" · 回合固定载入 {tok['codely_context_est']}"
                    f"（byte/3.5 代理口径 · O-2325）"})
    wmz = data["watermark"]
    if wmz["present"]:
        py_curve = "→".join(str(v) for v in wmz["py_tail"])
        flag_txt = ("🚩红牌" if wmz["red"] else "绿")
        tail_events.append({
            "time": wmz["last_sample"] or "-",
            "text": f"算力水位 · py {py_curve}% · {flag_txt}"
                    f" · 近段红牌 {wmz['red_flags_recent']} 次"
                    f" · 僵尸处置 {len(wmz['zombies_killed'])} 例"
                    f"（watchdog C7 · O-1626 判定即处置）"})
    sat = data["saturation"]
    if sat["present"]:
        py_curve = "→".join(str(v) for v in sat["py_tail"]) or "—"
        state_txt = sat["load_state"] or "—"
        flag_txt = ("🚩池饿旗" if sat["starvation_flag"]
                    else ("池饿候选" if sat["starvation_candidate"] else "无旗"))
        tail_events.append({
            "time": sat["audit_ts"] or sat["py_last_sample"] or "-",
            "text": f"满载面 · 池 ready {sat['pool_ready']}/{(sat['pool_ready'] or 0) + (sat['pool_waiting'] or 0)}"
                    f" · 本机 py {py_curve}% · 态 {state_txt} · {flag_txt}"
                    f" · 近百采样旗 {sat['starvation_flags_recent']} 次"
                    f"（第七旗池饿 · O-20260925-1137 · 旗=供给义务非烧数许可）"})
    sc = payload["trading"]["scorecard"]
    if sc["present"]:
        b = sc["best"] or {}
        tail_events.append({
            "time": sc["generated"] or "-",
            "text": f"P-6 记分卡 · {sc['text']} · 最优 {b.get('id', '—')} "
                    f"{b.get('grade', '—')} {b.get('total', '—')} 分"
                    f"（评价面 · hr 仍为唯一编制权）"})
    fl_line = payload["research"]["factor_line"]
    if fl_line["present"]:
        parts = " · ".join(f"{b['id']} {b['text']}"
                           for b in fl_line["batches"]) or "批次件待产出"
        tail_events.append({
            "time": "-",
            "text": f"研究线 · 因子账本 N={fl_line['total'] or '—'} · {parts}"
                    f"（双系列口径 · 引擎账本 N={chain['trials_total']} 另计）"})
    rg = data["regime"]
    if rg["present"]:
        tail_events.append({
            "time": rg["asof"] or "-",
            "text": f"行情防线 · {rg['state_cn']} · 在态 {rg['days_in_state']} 日"
                    f" · {rg['mode']} 记录（触发：{'；'.join(rg['triggers']) or '无'}）"})
    pf = data["portfolio"]
    if pf["present"]:
        def _pf2(v):
            return format(v, ".2f") if isinstance(v, (int, float)) else "—"
        iv = pf.get("iv") or {}
        if iv.get("present"):
            iv_txt = (f" · IV6 风险预算 Sharpe {_pf2(iv['sharpe'])} · DR {_pf2(iv['dr'])}"
                      f"（报告制 pass 2 · v2 门{'过' if iv.get('v2_pass') else '未过'}"
                      f" · 采纳=章程 §五 T1 待批）")
        else:
            iv_txt = " · IV=待产出"
        tail_events.append({
            "time": pf["generated"] or "-",
            "text": f"组合层 · EW6 等权 {pf['members']} 员 · Sharpe {_pf2(pf['ew_sharpe'])}"
                    f" · 分散收益 +{_pf2(pf['benefit'])} · ×2 成本 {_pf2(pf['x2_sharpe'])} "
                    f"{('存活' if pf['x2_survive'] else '阵亡') if pf['x2_survive'] is not None else '—'}"
                    f"（T-06 报告制 · EW 载体）{iv_txt}"})
    cw = data["corr_watch"]
    if cw["present"]:
        def _cw2(v):
            return format(v, ".2f") if isinstance(v, (int, float)) else "—"
        tail_events.append({
            "time": cw["generated"] or "-",
            "text": f"相关性监控 · {cw['text']}"
                    f" · IS2 最高对 {_cw2(cw['max_is2_pair'])}"
                    f" · 尾窗均值 {_cw2(cw['rolling_avg_last'])}"
                    f" · ×2 垫最小 {_cw2(cw['x2_margin_min'])}"
                    f" · FL {cw['forward_status'] or '—'}"
                    f"（组合部 §一.2 · 月更 · twin{'OK' if cw['twin_ok'] else '红'}）"})
    gv = data["governance"]
    if gv["present"]:
        ga, gb = gv["audit"], gv["briefing"]
        parts = []
        if ga["present"]:
            parts.append(f"科学审计 {ga['ok']}/{ga['checks']} 检 OK · findings {ga['findings']}")
        if gb["present"]:
            parts.append(f"月度简报 {gb['month']} 在档")
        tail_events.append({
            "time": ga["generated"] or gb["generated"] or "-",
            "text": "治理面 · " + " · ".join(parts)
                    + "（月度 M 层 · 总经办 · findings 只报不阻断）"})
    qb = data["queue_bandit"]
    if qb["present"]:
        tail_events.append({
            "time": qb["generated"] or "-",
            "text": f"队列排程 · UCB1 advisory · {qb['text']}"
                    f" · 已试臂 {qb['tried_arms']}/{qb['n_arms']} · exploit 最优 {qb['best_exploit_cn']}"
                    f"（QUEUE_BANDIT v1 · O-1819 队列永不清空 · 只排序不发起批）"})
    fl = payload["fleet"]
    if fl["present"]:
        m_alive = sum(1 for m in fl["machines"] if m["health"] == "ok")
        p1d_txt = ""
        if fl["p1d"] and fl["p1d"]["gates"]:
            gs = fl["p1d"]["gates"]
            p1d_txt = (f" · P-1d 三槽门 dzjy{'✓' if gs['dzjy']['pass'] else '✗'}/"
                       f"gdhs{'✓' if gs['gdhs']['pass'] else '✗'}/"
                       f"margin{'✓' if gs['margin']['pass'] else '✗'}")
        tail_events.append({
            "time": fl["machines"][0]["last_seen"] if fl["machines"] else "-",
            "text": f"机队 · {len(fl['machines'])} 节点 {m_alive} 活 · 票据 "
                    f"done {fl['n_done']}/claimed {fl['n_claimed']}/"
                    f"open {fl['n_open']}{p1d_txt}"})
    payload["events"] += tail_events + [
        {"time": "-", "text": f"复合因子方案已立项：{COMPOSITE_PLAN}"},
        {"time": "-", "text": "Money02 前代系统已并入资产库，旧自动化停用"},
    ]
    return payload


def main() -> int:
    payload = build()
    js = "window.DASH_DATA = " + json.dumps(payload, ensure_ascii=False) + ";\n"
    out_js = os.path.join(PATHS.results_dir, "dashboard_status.js")
    out_json = os.path.join(PATHS.results_dir, "dashboard_status.json")
    with open(out_js, "w", encoding="utf-8") as f:
        f.write(js)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"dashboard status -> {out_js}")
    print(f"  factors={len(payload['research']['factor_top'])} "
          f"backtest={payload['strategy']['n_combos']}combos/{payload['strategy']['n_pass']}pass "
          f"traders={len(payload['trading']['traders'])} "
          f"milestones={payload['gamification']['milestones_done']}/{payload['gamification']['milestones_total']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
