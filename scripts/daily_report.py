# -*- coding: utf-8 -*-
"""Daily battle report -- T-75 (O-20260926-0940): ONE page + JSON twin, five faces + token line.

Faces (aggregation ONLY, zero new metrics/judgments invented; missing faces get honest labels):
  (a) COMBAT: paper-account scoreboard across families (6 in-register traders via
      results/paper_export/latest.json; AGGR-* via results/aggr_paper/*_paper.json;
      ALLOC-* via results/alloc_paper/*.json; CN-* when live) + market-clock current call
      (results/market_clock/call_latest.json) + guard face (per-trader regime_guard).
  (a2) CEO LIVE (T-105 v1.3): embedded live-usage section -- reads today's
      docs/live_usage/LIVE-<day>.json twin (sibling ceo_live_usage.py leg),
      renders state/rung/cap/heat/clock row + direct link; missing twin = honest label.
  (b) R&D: 24h throughput (commits, verdict/result JSONs landed, research digests, prereg files)
      + in-flight batch watermark (results/watermark.jsonl tail, local file) + compute audit
      latest (results/compute_audit.json).
  (c) DECISION: tail of firm/DECISIONS.md (canon T-75).
  (d) TOMORROW: fleet/tasks tickets status open|claimed with owner line.
  (e) ENGINE-WAVE (r594 bm-b, J10 line): perpetual N1 candidate-production
      chain face -- chain head / merged-pool K / recent waves / seat state,
      SINGLE-SOURCE reuse of monitor.build_status._engine_wave_state()
      (r593 law: N1_BANDS registry + shard products + finalize ledger +
      seat MSGs; honest degrade, never fabricated, zero re-derivation).
  token line (T-77 slice-d): results/token_usage.json local/api estimates.

Output: docs/daily_report/REPORT-YYYYMMDD.md + REPORT-YYYYMMDD.json (today by wall clock;
same-day rerun regenerates in place, other days never touched -- append-only across days).
Idempotent per day EXCEPT generated_at audit field.

Usage:
  python scripts/daily_report.py run        # generate/refresh today's report
  python scripts/daily_report.py selftest   # hermetic offline self-check

Exit codes: 0 = written/selftest pass; 2 = mechanism failure (honest, report as-is).
"""
import glob
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
import statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "docs", "daily_report")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import merge_lane_views as lane_views


def _lane_view(face):
    """A-family lane-merged view (D-20260928-03 batch-1 consumer switch):
    deterministic union of per-machine lane files + the legacy shared file
    (conflict-resolver laws on the read side, scripts/merge_lane_views.py).
    No sources at all = {} (honest not-yet); identity contradictions fail
    closed (r98)."""
    sources = lane_views.load_sources(face)
    if not sources:
        return {}
    merged, _notes = lane_views.merge_face(face, sources)
    return merged


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


# ---------------------------------------------------------------- combat face
def _combat_face():
    px = _read_json(os.path.join(ROOT, "results", "paper_export", "latest.json")) or {}
    traders = []
    for t in px.get("traders", []):
        traders.append({
            "trader": t.get("trader"),
            "capital_cny": t.get("capital_cny"),
            "positions": t.get("positions_count"),
            "dd": (t.get("metrics") or {}).get("current_dd"),
            "guard": t.get("regime_guard"),
        })
    fams = []
    for f in sorted(glob.glob(os.path.join(ROOT, "results", "aggr_paper", "*_paper.json"))):
        d = _read_json(f) or {}
        eq = d.get("equity_cny") or (d.get("marks") or {}).get("equity_cny")
        fams.append({"family": "AGGR", "account": d.get("account") or os.path.basename(f),
                     "equity_cny": eq, "state_label": d.get("status") or d.get("guard")})
    for f in sorted(glob.glob(os.path.join(ROOT, "results", "alloc_paper", "ALLOC-*.json"))):
        d = _read_json(f) or {}
        eq = d.get("equity_cny") or (d.get("marks") or {}).get("equity_cny")
        fams.append({"family": "ALLOC", "account": d.get("account") or os.path.basename(f),
                     "equity_cny": eq, "state_label": d.get("status") or d.get("mode")})
    clock = _read_json(os.path.join(ROOT, "results", "market_clock", "call_latest.json")) or {}
    return {
        "paper_summary": px.get("summary"),
        "traders": traders,
        "account_families": fams,
        "market_clock": {k: clock.get(k) for k in
                         ("asof", "clock_cell", "position_cap_ladder", "active_sleeves")},
        "marks_asof": px.get("export_date") or px.get("evidence_cutoff"),
    }


# ---------------------------------------------------------------- R&D face
def _rd_face(now):
    cutoff = now - timedelta(hours=24)
    since = cutoff.strftime("%Y-%m-%d %H:%M:%S")
    try:
        n_commits = int(subprocess.run(
            ["git", "log", "--since=" + since, "--oneline"], capture_output=True, text=True,
            cwd=ROOT, encoding="utf-8", errors="replace").stdout.count("\n"))
    except Exception:
        n_commits = None
    def _mtime_recent(pat):
        return [f for f in glob.glob(pat)
                if os.path.getmtime(f) >= cutoff.timestamp()]
    verdicts = _mtime_recent(os.path.join(ROOT, "results", "*.json"))
    digests = _mtime_recent(os.path.join(ROOT, "research", "digests", "*.md"))
    preregs = _mtime_recent(os.path.join(ROOT, "research", "*.md"))
    audit = _lane_view("compute_audit") or {}
    latest_audit = audit.get("latest") or {}
    wm = None
    try:
        with open(os.path.join(ROOT, "results", "watermark.jsonl"), encoding="utf-8") as f:
            lines = [ln for ln in f.read().splitlines() if ln.strip()]
        if lines:
            wm = json.loads(lines[-1])
    except Exception:
        pass
    pool = _lane_view("runnable_pool") or {}
    return {
        "commits_24h": n_commits,
        "result_jsons_landed_24h": len(verdicts),
        "digests_landed_24h": len(digests),
        "prereg_md_touched_24h": len(preregs),
        "compute_audit_latest": {k: latest_audit.get(k) for k in
                                 ("ts", "cpu_pct", "py_cpu_pct", "flags", "verdict")
                                 if k in latest_audit} or latest_audit and {"keys": list(latest_audit)[:8]},
        "watermark_verdict": (wm or {}).get("verdict"),
        "pool_keys_n": len(pool) if isinstance(pool, dict) else None,
        "batch_in_flight": (wm or {}).get("local_batch_running"),
    }


# ---------------------------------------------------------------- decision + queue faces
def _decision_face(n=6):
    p = os.path.join(ROOT, "firm", "DECISIONS.md")
    try:
        lines = open(p, encoding="utf-8").read().splitlines()
    except Exception:
        return ["DECISIONS.md missing (honest label)"]
    return [ln for ln in lines if ln.startswith("- 2026")][-n:]


def _queue_face():
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "fleet", "tasks", "T-*.json"))):
        d = _read_json(f)
        if not d or d.get("status") not in ("open", "claimed", "in_progress"):
            continue
        out.append({"id": d.get("id"), "status": d.get("status"),
                    "type": d.get("type"), "immediate": bool(d.get("immediate")),
                    "owner": (d.get("claimed_by") or "")[:40]})
    return out


def _token_face():
    t = _read_json(os.path.join(ROOT, "results", "token_usage.json")) or {}
    return {k: t.get(k) for k in
            ("total_state_tokens_est", "total_report_tokens_est", "delta_vs_prev", "method")}


# ---------------------------------------------------------------- live face (T-105)
def _live_face(day):
    """CEO live-usage embedded section (T-105 v1.3 wiring): reads today's
    docs/live_usage/LIVE-<day>.json twin (same-day, produced by the sibling
    ceo_live_usage.py leg in the same S6 chain).  Aggregation-only linkout;
    missing twin -> honest label, never fabricated."""
    d = _read_json(os.path.join(ROOT, "docs", "live_usage",
                                f"LIVE-{day}.json"))
    if not d:
        return {"status": "missing",
                "note": "LIVE-{}.json 未生成（ceo_live_usage.py 腿未跑或"
                        "机制故障）——如实标注，禁编数".format(day)}
    m = d.get("market") or {}
    ldr = d.get("ladder") or {}
    return {
        "status": "ok",
        "day": d.get("day"),
        "state": m.get("state"),
        "rung": ldr.get("current_state"),
        "cap": ldr.get("current_cap"),
        "heat": m.get("heat"),
        "clock_cell": m.get("clock_cell"),
        "members": len(d.get("members") or []),
        "md_link": f"../live_usage/LIVE-{day}.md",
    }


# ---------------------------------------------------- utilization face (T-107)
def _utilization_face(now):
    """O-20260928-1614 sec.6 CEO-visible utilization section (T-107 face,
    SATURATION_DESIGN D6 baseline): per-machine py series + supply-floor
    compliance + ignition-SLA violation counts + latest audit verdict,
    aggregated from the per-machine compute_audit lane files (D-03(1)
    machine-suffixed lanes, single-writer per machine). Aggregation only,
    zero new metrics; missing samples = honest labels. Fill-ladder ledger
    direction = T-107/T-108 pending slices, never fabricated."""
    machines = {}
    for mid in ("bm-a", "bm-b", "bm-c"):
        d = _read_json(os.path.join(ROOT, "results",
                                    f"compute_audit.{mid}.json"))
        hist = (d or {}).get("history") or []
        latest = (d or {}).get("latest") or (hist[-1] if hist else {})
        series = [(str(s.get("ts", ""))[11:16], s.get("py_cpu_pct"))
                  for s in hist[-12:] if s.get("ts")]
        today = now.strftime("%Y-%m-%d")
        th = [s for s in hist if str(s.get("ts", "")).startswith(today)]
        floor_ok = sum(1 for s in th
                       if (s.get("supply_floor") or {}).get("breach") is False)
        sla_n = sum(1 for s in th if "ignition_sla" in (s.get("flags") or []))
        gap_n = sum(1 for s in th if "supply_gap" in (s.get("flags") or []))
        machines[mid] = {
            "latest_ts": latest.get("ts"),
            "py_pct": latest.get("py_cpu_pct"),
            "cpu_pct": latest.get("cpu_total_pct"),
            "ready": latest.get("pool_ready_count"),
            "streak_min": latest.get("supply_family_streak_min"),
            "verdict": latest.get("verdict"),
            "py_series_tail": series,
            "today_samples": len(th),
            "today_floor_ok": floor_ok,
            "today_sla_flags": sla_n,
            "today_supply_gap_flags": gap_n,
        }
    return {"machines": machines,
            "fill_ledger": "T-107 slice-2 / T-108 D4 (catalog generator) "
                           "pending -- honest label",
            "canon": "O-20260928-1614 sec.6 + O-20260928-1630 D6 "
                     "(two-pool sovereignty face merges when D7 lands)"}


# ------------------------------------------------- core-spread face (T-134 s4)
def _core_spread_face(day):
    """T-134 s4 (CEO order O-2026-09-30-2355) three-machine core-spread +
    parallel-efficiency comparison row: per-machine judged batches,
    weighted effective cores (core-seconds / wall-seconds), single-core
    red-flag counts -- aggregated from results/pool_core_samples.jsonl
    rows dated <day> (    law-2 launch sampler, Tools/core_sampler.py; rows
    propagate per machine via git).  Aggregation only; machines without
    samples today get honest zero rows, never fabricated.
    r503 merge (T-134 s4 follow-up, r502 next-pointer): each machine's
    latest per-machine compute_audit lane (results/compute_audit.<mid>.json
    -> latest.parallel_efficiency, 60-min trailing window, readable flag)
    is joined as audit_window -- so a zero-sample machine renders its
    sampler-health state (zero launches vs unreadable sampler) instead of
    a bare N/A that reads like a data gap."""
    per = {mid: {"batches_judged": 0, "core_seconds": 0.0, "wall_seconds": 0.0,
                 "effective_cores": None, "single_core_burn": 0,
                 "multicore_burn": 0, "too_short": 0, "last_ts": None}
           for mid in ("bm-a", "bm-b", "bm-c")}
    path = os.path.join(ROOT, "results", "pool_core_samples.jsonl")
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except Exception:
        return {"day": day, "machines": per,
                "note": "pool_core_samples.jsonl 未读出——如实标注，禁编数"}
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        try:
            r = json.loads(ln)
        except Exception:
            continue
        if not isinstance(r, dict):
            continue   # junk/non-dict line (r570 blob-face): never fatal
        if not str(r.get("ts", "")).startswith(day):
            continue
        mid = r.get("machine_id")
        if mid not in per:
            continue
        d = per[mid]
        d["last_ts"] = str(r.get("ts"))
        v = r.get("verdict")
        if v == "too_short_to_sample":
            d["too_short"] += 1
            continue
        if v in ("multicore_burn", "single_core_burn"):
            d["batches_judged"] += 1
            d[v] += 1
            d["core_seconds"] += float(r.get("cpu_s") or 0.0)
            d["wall_seconds"] += float(r.get("wall_s") or 0.0)
    for d in per.values():
        if d["wall_seconds"] > 0:
            d["effective_cores"] = round(d["core_seconds"] / d["wall_seconds"], 2)
        d["core_seconds"] = round(d["core_seconds"], 1)
        d["wall_seconds"] = round(d["wall_seconds"], 1)
    for mid, d in per.items():
        aud = _read_json(os.path.join(ROOT, "results",
                                      f"compute_audit.{mid}.json")) or {}
        latest_aud = aud.get("latest") or {}
        pe = latest_aud.get("parallel_efficiency") or {}
        d["audit_window"] = {
            "readable": pe.get("readable"),
            "window_min": pe.get("window_min"),
            "audit_batches": pe.get("batches_judged"),
            "audit_ts": latest_aud.get("ts"),
        }
    return {"day": day, "machines": per,
            "canon": "T-134 s4 (O-2026-09-30-2355) -- law-2 sampler rows "
                     "results/pool_core_samples.jsonl + per-machine "
                     "compute_audit parallel_efficiency window merge (r503)"}


# --------------------------------------- PnL attribution face (A2 / G4)
def _series_tail_delta(series):
    """Day-over-day tail delta from an account's own daily series.
    Aggregation only (zero new judgments): accepts dict mark rows
    ({date, equity_cny[, daily_ret]}) or [date, nav] pairs; honest degrade
    (no_data / first_day) when the series cannot yield a delta."""
    rows = []
    last_dict = None
    for r in series or []:
        if isinstance(r, dict):
            d, v = r.get("date"), r.get("equity_cny")
            if d is not None and v is not None:
                rows.append((str(d), float(v)))
                last_dict = r
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            d, v = r[0], r[1]
            if d is not None and v is not None:
                rows.append((str(d), float(v)))
    if not rows:
        return {"status": "no_data"}
    asof, eq = rows[-1]
    if len(rows) < 2:
        return {"status": "first_day", "asof": asof, "prior": None,
                "day_pnl_cny": None, "day_ret": None,
                "equity_cny": round(eq, 2)}
    pasof, peq = rows[-2]
    day_ret = None
    if isinstance(last_dict, dict) and last_dict.get("daily_ret") is not None:
        day_ret = last_dict.get("daily_ret")
    elif peq:
        day_ret = eq / peq - 1.0
    return {"status": "ok", "asof": asof, "prior": pasof,
            "day_pnl_cny": round(eq - peq, 2),
            "day_ret": (round(float(day_ret), 6)
                        if day_ret is not None else None),
            "equity_cny": round(eq, 2)}


def _top_position(t):
    """Top |unrealized PnL| open position (existing cumulative face,
    since-entry -- explicitly NOT a daily figure)."""
    best = None
    for p in t.get("open_positions") or []:
        u = p.get("unrealized_pnl_cny")
        if u is None:
            continue
        if best is None or abs(float(u)) > abs(float(best[1])):
            best = (p.get("symbol"), float(u))
    if best is None:
        return None
    return {"symbol": best[0], "unrealized_pnl_cny": round(best[1], 2)}


_P6_STATUS_LABEL = {"first_day": "首日无前值", "no_data": "缺数据",
                    "no_prior_export": "前值 export 件缺", "no_equity": "权益面缺"}


def _paper6_attribution():
    """Six in-register paper traders (one trader = one leg): day-over-day
    equity delta from the dated export chain results/paper_export/export-*
    .json (T-35 d3 daily twins); honest degrade when the chain is absent."""
    files = sorted(glob.glob(os.path.join(
        ROOT, "results", "paper_export", "export-*.json")))
    if not files:
        d = _read_json(os.path.join(
            ROOT, "results", "paper_export", "latest.json")) or {}
        rows = [{"trader": t.get("trader"),
                 "equity_cny": ((t.get("capital_cny") or {}).get("equity")),
                 "day_pnl_cny": None, "day_ret": None, "status": "no_prior_export",
                 "top_position": _top_position(t)}
                for t in d.get("traders", [])]
        return {"rows": rows, "asof": d.get("export_date") or d.get("evidence_cutoff"),
                "prior": None, "family_day_pnl_cny": None,
                "note": "无逐日 export 件——前值面缺，如实标注"}
    latest = _read_json(files[-1]) or {}
    prior = _read_json(files[-2]) if len(files) >= 2 else None
    prior_eq = {}
    if prior:
        for t in prior.get("traders", []):
            prior_eq[t.get("trader")] = (t.get("capital_cny") or {}).get("equity")
    asof = latest.get("export_date") or os.path.basename(files[-1])[7:-5]
    rows, total = [], 0.0
    for t in latest.get("traders", []):
        name = t.get("trader")
        eq = (t.get("capital_cny") or {}).get("equity")
        pe = prior_eq.get(name)
        if eq is None:
            rows.append({"trader": name, "status": "no_equity",
                         "status_label": _P6_STATUS_LABEL["no_equity"]})
            continue
        if pe is None:
            rows.append({"trader": name, "equity_cny": round(float(eq), 2),
                         "day_pnl_cny": None, "day_ret": None,
                         "status": "no_prior_export",
                         "status_label": _P6_STATUS_LABEL["no_prior_export"],
                         "top_position": _top_position(t)})
            continue
        pnl = float(eq) - float(pe)
        total += pnl
        rows.append({"trader": name, "equity_cny": round(float(eq), 2),
                     "day_pnl_cny": round(pnl, 2),
                     "day_ret": (round(float(eq) / float(pe) - 1.0, 6)
                                 if pe else None),
                     "status": "ok", "top_position": _top_position(t)})
    return {"rows": rows, "asof": str(asof),
            "prior": (prior or {}).get("export_date"),
            "family_day_pnl_cny": (round(total, 2) if prior else None)}


def _marks_family(pattern, family, label):
    """One account = one leg: per-account day delta from each account file's
    own marks/nav series; SYSV1 rows additionally carry the frozen route
    weight face (rev_osc/trend/lowvol/cash) + state from the last mark."""
    rows, total, asof, missing = [], 0.0, None, 0
    for f in sorted(glob.glob(pattern)):
        d = _read_json(f) or {}
        account = d.get("account") or os.path.basename(f)
        series = d.get("marks")
        if series is None:
            series = d.get("nav_series")
        info = _series_tail_delta(series)
        info["account"] = account
        if family == "SYSV1":
            last = None
            for r in (d.get("marks") or []):
                if isinstance(r, dict):
                    last = r
            if last:
                info["state"] = last.get("state")
                info["route"] = last.get("route")
                info["w_eff"] = last.get("w_eff")
                info["pure_sleeve"] = bool(
                    last.get("ret") is not None
                    and last.get("series") is not None
                    and abs(float(last.get("ret")) - float(last.get("series"))) < 1e-12)
        if info.get("status") != "ok":
            missing += 1
        else:
            total += info["day_pnl_cny"]
            if asof is None or str(info.get("asof")) > asof:
                asof = str(info.get("asof"))
        rows.append(info)
    return {"family": family, "label": label, "n": len(rows), "rows": rows,
            "asof": asof, "family_day_pnl_cny": (round(total, 2)
                                                 if any(r.get("status") == "ok"
                                                        for r in rows) else None),
            "missing_n": missing}


def _attribution_face(now):
    """G4 daily PnL attribution ledger (AUTOMATION-LINE-PLAN-v1 batch A2):
    which leg made/lost money today. Aggregation only -- day-over-day deltas
    come from each face's own series (paper-6 export chain, AGGR/GRID/SYSV1
    marks, ALLOC nav_series); missing data gets honest labels, never
    fabricated. Marks asof is data-driven (pre-15:30 = prior trading day)."""
    p6 = _paper6_attribution()
    families = [
        _marks_family(os.path.join(ROOT, "results", "aggr_paper", "*_paper.json"),
                      "AGGR", "进攻族"),
        _marks_family(os.path.join(ROOT, "results", "alloc_paper", "ALLOC-*.json"),
                      "ALLOC", "配置族"),
        _marks_family(os.path.join(ROOT, "results", "grid_paper", "*.json"),
                      "GRID", "网格族"),
        _marks_family(os.path.join(ROOT, "results", "system_v1_paper", "*_paper.json"),
                      "SYSV1", "路由族"),
    ]
    grand, n_ok, n_missing = 0.0, 0, 0
    if p6.get("family_day_pnl_cny") is not None:
        grand += p6["family_day_pnl_cny"]
    n_ok += sum(1 for r in p6.get("rows", []) if r.get("status") == "ok")
    n_missing += sum(1 for r in p6.get("rows", []) if r.get("status") != "ok")
    asof = p6.get("asof")
    for fam in families:
        if fam.get("family_day_pnl_cny") is not None:
            grand += fam["family_day_pnl_cny"]
        n_ok += sum(1 for r in fam.get("rows", []) if r.get("status") == "ok")
        n_missing += fam.get("missing_n") or 0
        if fam.get("asof") and (asof is None or str(fam["asof"]) > str(asof)):
            asof = fam["asof"]
    today = now.strftime("%Y-%m-%d")
    return {
        "status": "ok" if (p6.get("rows") or any(f.get("rows") for f in families)) else "no_data",
        "asof": asof, "report_day": today,
        "asof_note": (None if asof == today else
                      "面板 marks asof=%s（当日 bar 未出=前交易日口径，如实标注）" % asof),
        "paper6": p6,
        "families": families,
        "grand_day_pnl_cny": round(grand, 2),
        "accounts_attributed": n_ok,
        "accounts_missing": n_missing,
        "method_note": "日对日差分=各面自带序列尾两行/六员逐日 export 链（聚合面零新判据）",
        "leg_note": "六员=一员一腿；AGGR/ALLOC/GRID=一账户一腿；SYSV1=route 腿权重面"
                    "（rev_osc/trend/lowvol/cash·逐腿收益序列未单列=如实标注）；"
                    "持仓浮盈 top=自入场累计（非当日）",
        "canon": "research/AUTOMATION-LINE-PLAN-v1.md batch A2 (G4) · "
                 "acceptance V2: REPORT 归因节连续 ≥5 交易日（缺数据如实标注合法）",
    }


# ------------------------------------------------ engine-wave face (r594 bm-b)
def _engine_wave_face():
    """Perpetual N1 engine-wave chain face (J10 line, r594 bm-b): the main
    candidate production line wired into the CEO daily report.  SINGLE
    SOURCE reuse -- monitor.build_status._engine_wave_state() (r593): the
    derivation reads only N1_BANDS registry + shard products + finalize
    ledger + seat MSGs.  Missing sources degrade to honest labels."""
    try:
        from monitor.build_status import _engine_wave_state
        st = _engine_wave_state()
    except Exception:
        return {"present": False,
                "note": "常青波链面派生不可用（monitor.build_status 导入失败）"
                        "——如实标注，禁编数"}
    return st


# ------------------------------------- stage x style matrix face (r1088 bm-b)
def _stage_style_face():
    """Stage x style combo face (CEO order O-20261019-2230 sec.2.4, due 2026-10-26).

    Pure aggregation of the two frozen readout faces -- the P4 verdict from
    FINALIZE-SSCOMBO-P1.json and the descriptive stage x style matrix.  No new
    judgment line, no ledger booking, no threshold invented here: the pass/fail
    reading is carried verbatim from the batch finalize face.
    Missing sources degrade to an honest label (never fabricated numbers)."""
    base = os.path.join(ROOT, "results", "stagestyle_combo_p1")
    fin = _read_json(os.path.join(base, "FINALIZE-SSCOMBO-P1.json"))
    mat = _read_json(os.path.join(base, "STAGE-STYLE-MATRIX-v1.json"))
    if not fin or not mat:
        return {"present": False,
                "note": "阶段×风格面未产出（readout 件缺）——如实标注，禁编数"}
    v = fin.get("verdict") or {}
    cells = list(mat.get("cells") or [])
    states = ("BEAR", "GRIND", "CHOP", "SUPPORT", "BULL")
    best_by_state = {}
    for st in states:
        cand = [(c, ((mat.get("matrix") or {}).get(c) or {}).get(st) or {})
                for c in cells]
        cand = [(c, d) for c, d in cand if isinstance(d.get("sharpe_ann"), (int, float))]
        if not cand:
            continue
        c, d = max(cand, key=lambda kv: kv[1]["sharpe_ann"])
        best_by_state[st] = {"cell": c, "sharpe": round(d["sharpe_ann"], 4),
                             "n_days": d.get("n_days")}
    return {
        "present": True,
        "cutoff": fin.get("evidence_cutoff") or mat.get("source_evidence_cutoff"),
        "window": fin.get("window") or mat.get("window"),
        "reading": v.get("reading"),
        "rule": v.get("rule"),
        "best_combo": v.get("best_combo"),
        "best_unconditional": v.get("best_unconditional"),
        "margin": v.get("margin"),
        "attribution": v.get("attribution"),
        "cells": cells,
        "state_days": mat.get("state_days"),
        "best_by_state": best_by_state,
        "source": "results/stagestyle_combo_p1/{FINALIZE-SSCOMBO-P1,STAGE-STYLE-MATRIX-v1}.json",
    }


# ------------------------------------- market risk tape (r1153 bm-a)
ZT_PANEL_LABELS = {"zt": "涨停池", "zbgc": "炸板池", "dtgc": "跌停池",
                   "strong": "强势池"}
ZT_DATE_COL = "日期"
ZT_NAME_COL = "名称"
ZT_STREAK_COL = "连板数"
ZT_SERIES_DAYS = 10   # r1154: how many tracked bars the tape shows as a trajectory


def _zt_panel_day(key, root=None):
    """One forward-accumulated zt-pool panel: the last two bar dates and their
    row counts (a row IS a member, so the count is the member count).

    Forward panels (O-20261001-2103): a trading day either got captured or it is
    permanently gone -- so an absent panel or a missing day must read as absent,
    never as 0 members (r1149 marks-coverage law)."""
    root = root or ROOT
    path = os.path.join(root, "data", "zt_pool", f"{key}.parquet")
    if not os.path.exists(path):
        return {"key": key, "label": ZT_PANEL_LABELS[key], "status": "absent"}
    try:
        import pandas as pd
        df = pd.read_parquet(path)
    except Exception as exc:                                  # noqa: BLE001
        return {"key": key, "label": ZT_PANEL_LABELS[key],
                "status": "unreadable", "detail": str(exc)[:120]}
    if df is None or len(df) == 0 or ZT_DATE_COL not in df.columns:
        return {"key": key, "label": ZT_PANEL_LABELS[key], "status": "empty"}
    days = df[ZT_DATE_COL].map(lambda v: str(v)[:10])
    counts = {d: int(n) for d, n in days.value_counts().items()}
    order = sorted(counts)
    cutoff = order[-1]
    prev = order[-2] if len(order) > 1 else None
    out = {"key": key, "label": ZT_PANEL_LABELS[key], "status": "ok",
           "cutoff": cutoff, "count": counts[cutoff],
           "prev_cutoff": prev, "prev_count": counts[prev] if prev else None,
           "days_tracked": len(order),
           "series": {d: counts[d] for d in order[-ZT_SERIES_DAYS:]}}
    if key == "zt":
        row = df[days == cutoff]
        ladder = {}
        if ZT_STREAK_COL in row.columns:
            for v in row[ZT_STREAK_COL]:
                try:
                    k = int(v)
                except (TypeError, ValueError):
                    continue
                ladder[k] = ladder.get(k, 0) + 1
        out["ladder"] = {str(k): ladder[k] for k in sorted(ladder)}
        if ladder and ZT_NAME_COL in row.columns:
            top_k = max(ladder)
            names = [str(n) for n, v in zip(row[ZT_NAME_COL], row[ZT_STREAK_COL])
                     if str(v).strip().split(".")[0] == str(top_k)]
            out["top_streak"] = {"streak": top_k, "n": ladder[top_k],
                                 "names": names[:5]}
    return out


def _zt_risk_face(day=None, root=None):
    """Market risk tape from the four forward zt-pool panels.

    Aggregation only: member counts on each panel's newest bar, the same number
    on the bar before it (direction), the sealed rate = 涨停/(涨停+炸板), and the
    streak ladder carried straight out of the panel's 连板数 column.  The two
    reading rules are mechanical and printed on the page, so nothing here is a
    hidden threshold."""
    panels = {k: _zt_panel_day(k, root) for k in ZT_PANEL_LABELS}
    ok = {k: v for k, v in panels.items() if v.get("status") == "ok"}
    if not ok:
        return {"present": False, "panels": panels,
                "note": "四面板全缺——前向池未采（缺面禁读成 0）"}
    cutoffs = sorted({v["cutoff"] for v in ok.values()})
    face = {"present": True, "panels": panels, "cutoff": cutoffs[-1],
            "cutoffs": cutoffs,
            "aligned": len(cutoffs) == 1 and len(ok) == len(panels)}
    up = ok.get("zt", {}).get("count")
    dn = ok.get("dtgc", {}).get("count")
    broke = ok.get("zbgc", {}).get("count")
    if up is not None and broke is not None and (up + broke) > 0:
        face["seal_rate"] = round(up / float(up + broke), 4)
    if isinstance(up, int) and isinstance(dn, int):
        face["down_over_up"] = round(dn / float(up), 3) if up else None
        face["kill_day"] = dn >= up
    if ok.get("zt", {}).get("ladder"):
        face["ladder"] = ok["zt"]["ladder"]
        face["top_streak"] = ok["zt"].get("top_streak")
    # r1154 trajectory: a single bar's counts say nothing about direction, and a page
    # that only ever shows one bar hides a regime. Union of the dates each panel
    # actually captured (a day missing from a panel stays None = absent, never 0), and
    # the seal rate is re-derived per day from that day's own two counts, not carried.
    dates = sorted({d for v in ok.values() for d in (v.get("series") or {})})
    dates = dates[-ZT_SERIES_DAYS:]
    series = []
    for d in dates:
        row = {"date": d}
        for k in ("zt", "zbgc", "dtgc"):
            s = (ok.get(k) or {}).get("series") or {}
            row[k] = s.get(d)
        if isinstance(row["zt"], int) and isinstance(row["zbgc"], int) \
                and (row["zt"] + row["zbgc"]) > 0:
            row["seal_rate"] = round(row["zt"] / float(row["zt"] + row["zbgc"]), 4)
        series.append(row)
    if series:
        face["series"] = series
    return face


def build_report(now):
    return {
        "report_date": now.strftime("%Y-%m-%d"),
        "generated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "combat": _combat_face(),
        "live_usage": _live_face(now.strftime("%Y-%m-%d")),
        "rd": _rd_face(now),
        "decisions_tail": _decision_face(),
        "tomorrow_queue": _queue_face(),
        "token_line": _token_face(),
        "utilization": _utilization_face(now),
        "core_spread": _core_spread_face(now.strftime("%Y-%m-%d")),
        "pnl_attribution": _attribution_face(now),
        "engine_wave": _engine_wave_face(),
        "stage_style": _stage_style_face(),
        "market_risk": _zt_risk_face(now.strftime("%Y-%m-%d")),
        "canon_refs": ["T-75 ticket (O-20260926-0940)", "results/paper_export/latest.json",
                       "results/market_clock/call_latest.json", "results/token_usage.json",
                       "T-105 v1.3 live-usage embedded section (docs/live_usage/)",
                       "O-20260928-1614 sec.6 utilization face (T-107)",
                       "T-134 s4 core-spread/parallel-efficiency row (O-2026-09-30-2355)",
                       "perpetual N1 engine-wave chain face (J10 r593/r594, monitor/build_status._engine_wave_state)",
                       "G4 PnL-attribution daily ledger (AUTOMATION-LINE-PLAN-v1 batch A2, <=10-23)",
                       "stage x style combo face (O-20261019-2230 sec.2.4, due 2026-10-26)"],
    }


def render_md(rep):
    L = [f"# 每日战报 — {rep['report_date']}", ""]
    L.append(f"> 生成 {rep['generated_at']} · 聚合面零新判据 · 缺面如实标注")
    c = rep["combat"]
    L.append("")
    L.append("## 一、实战面")
    mc = c.get("market_clock") or {}
    L.append(f"- **市场时钟**：`{mc.get('clock_cell')}`（asof {mc.get('asof')}）· 仓位阶梯帽 {mc.get('position_cap_ladder')}")
    L.append(f"- **激活袖**：{'；'.join(mc.get('active_sleeves') or ['N/A'])}")
    ps = c.get("paper_summary") or {}
    L.append(f"- **在册交易员**（{ps.get('traders')} 员 · marks {c.get('marks_asof')}）：总权益 "
             f"{ps.get('total_equity_cny')} CNY · 总持仓 {ps.get('total_positions')} · 当日入场 {ps.get('entries_today')} / 出场 {ps.get('exits_today')}")
    for t in c.get("traders", []):
        L.append(f"  - {t.get('trader')}: 资本 {t.get('capital_cny')} · 持仓 {t.get('positions')} · dd {t.get('dd')} · 守卫 {t.get('guard')}")
    fams = c.get("account_families") or []
    L.append(f"- **实验账户族**（{len(fams)} 个：AGGR/ALLOC/CN 纸盘）：")
    for fam in fams[:24]:
        L.append(f"  - [{fam['family']}] {fam.get('account')}: equity {fam.get('equity_cny') or 'N/A(面未产出)'} · {fam.get('state_label') or ''}")
    if not fams:
        L.append("  - （无在飞账户族，如实标注）")
    L.append("")
    L.append("## 二、CEO 实盘使用面（T-105 直达）")
    lv = rep.get("live_usage") or {}
    if lv.get("status") == "ok":
        L.append(f"- **[实盘一页纸直达]({lv.get('md_link')})**（"
                 f"LIVE-{lv.get('day')}）：政体态 **{lv.get('state')}** · "
                 f"有效档位 **{lv.get('rung')}** → 股票敞口总帽 "
                 f"{lv.get('cap'):.0%} · 温度计 {lv.get('heat')} · "
                 f"市场时钟 `{lv.get('clock_cell')}` · 六员 "
                 f"{lv.get('members')} 员持仓见一页纸")
    else:
        L.append(f"- {lv.get('note')}")
    L.append("")
    L.append("## 三、研发面（24h）")
    r = rep["rd"]
    L.append(f"- 提交 {r.get('commits_24h')} · 判定/结果件落地 {r.get('result_jsons_landed_24h')} · "
             f"调研 digest {r.get('digests_landed_24h')} · 预注册/正典触碰 {r.get('prereg_md_touched_24h')}")
    L.append(f"- 在飞批：{'是' if r.get('batch_in_flight') else '否'} · 水位判定 `{r.get('watermark_verdict')}` · "
             f"算力审计 `{json.dumps(r.get('compute_audit_latest'), ensure_ascii=False)[:160]}`")
    ew = rep.get("engine_wave") or {}
    if ew.get("present"):
        waves = " | ".join(
            "W{w} {o} {d}/{t} {fin}".format(
                w=w.get("wave"), o=w.get("owner") or "?",
                d=w.get("shards_done") if w.get("shards_done") is not None else "?",
                t=w.get("shards_total") if w.get("shards_total") is not None else "?",
                fin="账落" if w.get("finalize_landed") else "账待落")
            for w in (ew.get("waves") or [])) or "（零注册波，如实标注）"
        seats = "、".join("W{s}（{m}）".format(s=s.get("wave"), m=s.get("machine"))
                         for s in (ew.get("seats") or [])) or "无"
        L.append(f"- **候选产线 · 常青 N1 波链**：链头 {ew.get('chain_head')} runs · "
                 f"合并池 K {ew.get('k')} · 注册尾 W{ew.get('last_registered')}"
                 f"（{ew.get('last_owner')}）· 下一注册 W{ew.get('next_registration')}")
        L.append(f"  - 近波：{waves}")
        L.append(f"  - 席位：已占席 {seats} · 下一可席 W{ew.get('next_seatable')}")
    else:
        L.append(f"- 候选产线 · 常青 N1 波链：{ew.get('note') or '面未产出——如实标注'}")
    L.append("")
    L.append("## 四、决策面（今日 GM 自主决策日志尾）")
    for ln in rep.get("decisions_tail", []):
        L.append(f"- {ln[2:]}")
    L.append("")
    L.append("## 五、明日队列（公司自排优先级）")
    for q in rep.get("tomorrow_queue", [])[:12]:
        imm = " [immediate]" if q.get("immediate") else ""
        L.append(f"- {q['id']}({q['status']}{imm}) {q.get('type')} ← {q.get('owner') or '无人认领'}")
    L.append("")
    L.append("## 六、算力利用率（O-1614 满载机制 · T-107 面）")
    u = rep.get("utilization") or {}
    for mid, m in (u.get("machines") or {}).items():
        series = " ".join(f"{t}={p}%" for t, p in (m.get("py_series_tail") or [])
                          if p is not None)
        L.append(f"- **{mid}**：py {m.get('py_pct')}%（总机 {m.get('cpu_pct')}% · {m.get('latest_ts')}）"
                 f"· 池 ready {m.get('ready')} · 今日底线合规 {m.get('today_floor_ok')}/{m.get('today_samples')}"
                 f"· SLA 旗 {m.get('today_sla_flags')} · 供给缺口旗 {m.get('today_supply_gap_flags')}"
                 f"· 家族旗龄 {m.get('streak_min')}min · `{m.get('verdict')}`")
        if series:
            L.append(f"  - py 序列（近 {len(m.get('py_series_tail') or [])} 采样）：{series}")
    L.append(f"- 填充台账：{u.get('fill_ledger')}")
    cs = rep.get("core_spread") or {}
    parts = []
    for mid, m in (cs.get("machines") or {}).items():
        eff = m.get("effective_cores")
        seg = (f"**{mid}** 有效核 {eff if eff is not None else 'N/A'}"
               f"（判 {m.get('batches_judged')} 批 · 多核达标 {m.get('multicore_burn')}"
               f" · 单核红牌 {m.get('single_core_burn')} · 短跑不计 {m.get('too_short')}）")
        if eff is None:
            aw = m.get("audit_window") or {}
            if aw.get("readable"):
                wm = aw.get("window_min")
                wm_s = f"{wm:g}" if isinstance(wm, (int, float)) else "?"
                seg += (f"——当日零发射·采样器健康"
                        f"（近{wm_s}min窗 {aw.get('audit_batches')} 批）")
            elif aw:
                seg += "——采样器读出不可用（compute_audit 面如实标注）"
        parts.append(seg)
    if parts:
        L.append(f"- **核分布/并行效率三机对照（T-134 s4 · {cs.get('day')}）**：" + "；".join(parts))
    if cs.get("note"):
        L.append(f"  - {cs.get('note')}")
    # ---- section 7: PnL attribution daily ledger (A2 / G4)
    at = rep.get("pnl_attribution") or {}

    def _fm(v):
        return f"{v:,.2f}" if isinstance(v, (int, float)) else "N/A(缺数据)"

    def _fr(v):
        return f"{v:+.4%}" if isinstance(v, (int, float)) else "N/A"

    L.append("")
    L.append("## 七、盈亏归因日账（A2 · G4 · 按 sleeve/腿）")
    if at.get("status") != "ok":
        L.append(f"- 归因面未产出：{at.get('asof_note') or '数据面缺——如实标注，禁编数'}")
    else:
        if at.get("asof_note"):
            L.append(f"- **口径**：{at.get('method_note')} · {at.get('asof_note')}")
        else:
            L.append(f"- **口径**：{at.get('method_note')}")
        p6 = at.get("paper6") or {}
        if p6.get("rows"):
            seg6 = (f"- **纸盘六员**（asof {p6.get('asof')} · 前值 {p6.get('prior') or '—'}）："
                    f"日 PnL 合计 {_fm(p6.get('family_day_pnl_cny'))} CNY")
            note6 = p6.get("note")
            L.append(seg6 + (f" · {note6}" if note6 else ""))
            for r in p6.get("rows", []):
                seg = (f"  - {r.get('trader')}: 日 PnL {_fm(r.get('day_pnl_cny'))}"
                       f"（{_fr(r.get('day_ret'))}）· 权益 {_fm(r.get('equity_cny'))}")
                tp = r.get("top_position") or {}
                if tp.get("symbol"):
                    seg += (f" · 持仓浮盈 top {tp.get('symbol')} "
                            f"{_fm(tp.get('unrealized_pnl_cny'))}（自入场累计）")
                if r.get("status") != "ok":
                    seg += f" · {r.get('status_label') or '前值缺'}"
                L.append(seg)
        for fam in at.get("families") or []:
            if not fam.get("rows"):
                continue
            segf = (f"- **{fam.get('family')} {fam.get('label')}**（{fam.get('n')} 账户 · "
                    f"asof {fam.get('asof') or '—'}）：日 PnL 合计 "
                    f"{_fm(fam.get('family_day_pnl_cny'))} CNY")
            if fam.get("missing_n"):
                segf += f" · 缺数据 {fam.get('missing_n')} 账户"
            L.append(segf)
            for r in fam.get("rows", []):
                seg = (f"  - {r.get('account')}: 日 PnL {_fm(r.get('day_pnl_cny'))}"
                       f"（{_fr(r.get('day_ret'))}）· 权益 {_fm(r.get('equity_cny'))}")
                if r.get("status") != "ok":
                    seg += " · 首日无前值" if r.get("status") == "first_day" else " · 缺数据"
                if fam.get("family") == "SYSV1" and r.get("status") == "ok":
                    rt = r.get("route") or {}
                    legs = "/".join(f"{k} {v:.0%}" for k, v in rt.items()
                                    if isinstance(v, (int, float)))
                    seg += f" · 政体 {r.get('state')} · 路由 {legs}"
                    if r.get("pure_sleeve"):
                        seg += "（纯 rev_osc 袖：ret=series）"
                    if r.get("w_eff") is not None:
                        seg += f" · w_eff {r.get('w_eff')}"
                L.append(seg)
        L.append(f"- **跨族日 PnL 总计**：{_fm(at.get('grand_day_pnl_cny'))} CNY"
                 f"（可归因账户 {at.get('accounts_attributed')} · 缺数据 {at.get('accounts_missing')}）")
        if at.get("leg_note"):
            L.append(f"- 腿级注记：{at.get('leg_note')}")
    # ---- section 8: stage x style combo face (O-20261019-2230 sec.2.4)
    ss = rep.get("stage_style") or {}
    L.append("")
    L.append("## 八、阶段×风格组合面（CEO 终面 2026-10-26 交付面）")
    if not ss.get("present"):
        L.append(f"- {ss.get('note') or '面未产出——如实标注'}")
    else:
        L.append(f"- **证据截止** {ss.get('cutoff')} · 窗 {(ss.get('window') or {}).get('lo')}"
                 f"..{(ss.get('window') or {}).get('hi')}（{(ss.get('window') or {}).get('bars')} bar）"
                 f" · 纯描述读出面（零新判据 · 禁在此改判线）")
        bc = ss.get("best_combo") or {}
        bu = ss.get("best_unconditional") or {}
        L.append(f"- **判决（P4 原判据）**：{ss.get('reading')} — 最佳组合 "
                 f"{bc.get('cell')} sharpe {bc.get('sharpe_x1')} vs 无条件 "
                 f"{bu.get('face')} {bu.get('sharpe_x1')}"
                 f"（margin {ss.get('margin'):+.4f}）" if isinstance(ss.get("margin"), (int, float))
                 else f"- **判决（P4 原判据）**：{ss.get('reading')}")
        L.append(f"  - 判据：{ss.get('rule')}")
        if ss.get("attribution"):
            L.append(f"  - 归因：{ss.get('attribution')}")
        bbs = ss.get("best_by_state") or {}
        sd = ss.get("state_days") or {}
        seg = " · ".join(
            f"{st} **{d.get('cell')}** {d.get('sharpe'):+.2f}（{sd.get(st, d.get('n_days'))}d）"
            for st, d in bbs.items() if isinstance(d.get("sharpe"), (int, float)))
        if seg:
            L.append(f"- **各阶段态最优袖**（state 内 sharpe 排序，{len(ss.get('cells') or [])} 袖面）：{seg}")
    L.append("")
    L.append("## 九、市场风险面（涨跌停/炸板/连板梯队 · 前向池四面板）")
    mr = rep.get("market_risk") or {}
    if not mr.get("present"):
        L.append(f"- {mr.get('note') or '风险面未产出——如实标注'}")
        absent = [v.get("label") for v in (mr.get("panels") or {}).values()
                  if v.get("status") != "ok"]
        if absent:
            L.append(f"  - 缺面：{'、'.join(str(a) for a in absent)}（缺面禁读成 0）")
    else:
        pn = mr.get("panels") or {}

        def _cnt(k):
            v = pn.get(k) or {}
            if v.get("status") != "ok":
                return f"{v.get('label')}=缺面"
            seg = f"**{v.get('label')} {v.get('count')}**"
            if v.get("prev_count") is not None:
                seg += f"（前 {v.get('prev_cutoff')} {v.get('prev_count')}，{v.get('count') - v.get('prev_count'):+d}）"
            else:
                seg += "（无前一日对照）"
            return seg

        L.append("- 截止日：" + (
            f"四面同为 **{mr.get('cutoff')}**"
            if mr.get("aligned") else
            "各面板不一致（" + "、".join(f"{k}={v.get('cutoff')}"
                                       for k, v in pn.items() if v.get("status") == "ok")
            + "）——如实标注"))
        L.append("- " + " · ".join(_cnt(k) for k in ("zt", "dtgc", "zbgc", "strong")))
        if mr.get("seal_rate") is not None:
            L.append(f"- **封板率 {mr.get('seal_rate'):.1%}**（涨停/(涨停+炸板)，机械口径）")
        lad = mr.get("ladder") or {}
        if lad:
            seg = " / ".join(f"{k} 板 {v}" for k, v in lad.items())
            L.append(f"- 连板梯队：{seg}")
        top = mr.get("top_streak") or {}
        if top.get("streak"):
            names = "、".join(top.get("names") or []) or "（名册缺）"
            L.append(f"- 最高 **{top.get('streak')} 连板**（{top.get('n')} 只）：{names}")
        if mr.get("down_over_up") is not None:
            L.append(f"- 跌停/涨停 = **{mr.get('down_over_up')}**")
        if "kill_day" in mr:
            L.append("- 读法（机械口径，不含判据）：跌停数 ≥ 涨停数 → 记为**杀跌日**；"
                     f"今日 {'是' if mr.get('kill_day') else '否'}")
        ser = mr.get("series") or []
        if len(ser) > 1:
            L.append("")
            L.append(f"- **近 {len(ser)} 个采集日轨迹**（一格一日；缺面记 — 不记 0）：")
            L.append("")
            L.append("  | 日期 | 涨停 | 炸板 | 跌停 | 封板率 |")
            L.append("  |---|---|---|---|---|")

            def _cell(v):
                return "—" if v is None else str(v)

            for r in ser:
                sr = r.get("seal_rate")
                L.append(f"  | {r.get('date')} | {_cell(r.get('zt'))} | {_cell(r.get('zbgc'))} "
                         f"| {_cell(r.get('dtgc'))} | {'—' if sr is None else f'{sr:.1%}'} |")
            ups = [r["zt"] for r in ser if isinstance(r.get("zt"), int)]
            srs = [r["seal_rate"] for r in ser if r.get("seal_rate") is not None]
            if len(ups) > 1:
                lo, hi = min(ups), max(ups)
                lo_d = [r["date"][5:] for r in ser if r.get("zt") == lo]
                hi_d = [r["date"][5:] for r in ser if r.get("zt") == hi]
                L.append(f"  - 本窗涨停数 {lo}~{hi}，中位 {statistics.median(ups):g}"
                         f"（低 {'/'.join(lo_d)} · 高 {'/'.join(hi_d)}）；"
                         f"封板率中位 {'—' if not srs else f'{statistics.median(srs):.1%}'}")
            L.append("")
        L.append("- 口径：前向积累制（2026-10-08 起），日账只有真正采到的日子——"
                 "缺日不补、不记 0；面板由宿主采集，他机接管时在 results/zt_pool_update_status.json 留痕")
    L.append("")
    L.append("## Token 行（T-77 · L1 本地零 token/L3 云端该用就用）")
    t = rep.get("token_line") or {}
    L.append(f"- 状态面估计 {t.get('total_state_tokens_est')} · 报告面估计 {t.get('total_report_tokens_est')} · "
             f"增量 {json.dumps(t.get('delta_vs_prev'), ensure_ascii=False)[:120]} · 口径 {t.get('method')}")
    L.append("")
    L.append("> 判负与缺口照报不粉饰；三态标注（立法/生效/验收）见各票。")
    return "\n".join(L)


def run():
    os.makedirs(OUT_DIR, exist_ok=True)
    now = datetime.now()
    rep = build_report(now)
    day = rep["report_date"]
    with open(os.path.join(OUT_DIR, f"REPORT-{day}.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
    with open(os.path.join(OUT_DIR, f"REPORT-{day}.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(rep))
    print(f"daily report written: REPORT-{day}.md/.json faces=5 token=1")
    return 0


def selftest():
    """Hermetic: synthetic faces -> page renders with all five faces + token line."""
    global _combat_face, _rd_face, _decision_face, _queue_face, _token_face
    global _utilization_face, _live_face, _core_spread_face, _engine_wave_face
    global _attribution_face, _stage_style_face, _zt_risk_face
    # ---- A2/G4 helper legs (series tail delta, honest degrade paths)
    d = _series_tail_delta([{"date": "2026-09-01", "equity_cny": 100.0},
                            {"date": "2026-09-02", "equity_cny": 101.0}])
    assert d["status"] == "ok" and abs(d["day_pnl_cny"] - 1.0) < 1e-9, d
    assert d["prior"] == "2026-09-01" and d["asof"] == "2026-09-02"
    d2 = _series_tail_delta([["2026-09-01", 200.0], ["2026-09-02", 198.0]])
    assert d2["status"] == "ok" and abs(d2["day_pnl_cny"] - (-2.0)) < 1e-9, d2
    d3 = _series_tail_delta([{"date": "2026-09-01", "equity_cny": 100.0}])
    assert d3["status"] == "first_day" and d3["day_pnl_cny"] is None, d3
    d4 = _series_tail_delta([])
    assert d4["status"] == "no_data", d4
    d5 = _series_tail_delta([{"date": "2026-09-02", "equity_cny": 101.0,
                              "daily_ret": 0.01},
                             {"date": "2026-09-03", "equity_cny": 102.0,
                              "daily_ret": 0.0099}])
    assert abs(d5["day_ret"] - 0.0099) < 1e-9, d5  # stored face preferred
    # ---- r1153 market risk tape legs: real parquet fixture, counts + direction +
    # ladder + the honest absence path (an uncaptured forward day is not "0 members")
    import tempfile
    import pandas as pd
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "data", "zt_pool"), exist_ok=True)

    def _mk(key, rows):
        pd.DataFrame(rows).to_parquet(
            os.path.join(tmp, "data", "zt_pool", f"{key}.parquet"), index=False)

    _mk("zt", [{"日期": "2026-10-28", "名称": "A", "连板数": 1},
               {"日期": "2026-10-29", "名称": "B", "连板数": 1},
               {"日期": "2026-10-29", "名称": "C", "连板数": 3},
               {"日期": "2026-10-29", "名称": "D", "连板数": 2}])
    _mk("zbgc", [{"日期": "2026-10-28"}, {"日期": "2026-10-29"},
                 {"日期": "2026-10-29"}])
    _mk("dtgc", [{"日期": "2026-10-29"}])
    f = _zt_risk_face(root=tmp)
    assert f["present"] and f["cutoff"] == "2026-10-29", f
    assert f["panels"]["zt"]["count"] == 3, f          # rows are members
    assert f["panels"]["zt"]["prev_count"] == 1, f     # direction needs the prior bar
    assert f["panels"]["strong"]["status"] == "absent", f
    assert "count" not in f["panels"]["strong"], f     # absence is never 0 members
    assert f["aligned"] is False, f                    # one panel missing = not aligned
    assert f["ladder"] == {"1": 1, "2": 1, "3": 1}, f
    assert f["top_streak"]["streak"] == 3 and f["top_streak"]["names"] == ["C"], f
    assert abs(f["seal_rate"] - 3 / 5.0) < 1e-9, f      # 涨停/(涨停+炸板)
    assert f["kill_day"] is False, f                   # 1 跌停 vs 3 涨停
    assert abs(f["down_over_up"] - 1 / 3.0) < 1e-3, f
    # ---- r1154 trajectory legs: one bar is a level, two bars are not a trend; the
    # series is the union of captured dates with per-day seal rates re-derived, and a
    # day one panel never captured stays None instead of becoming a 0
    ser = f.get("series") or []
    assert [r["date"] for r in ser] == ["2026-10-28", "2026-10-29"], ser
    assert ser[0]["zt"] == 1 and ser[0]["zbgc"] == 1 and ser[0]["dtgc"] is None, ser
    assert abs(ser[0]["seal_rate"] - 0.5) < 1e-9, ser[0]
    assert ser[1]["zt"] == 3 and ser[1]["zbgc"] == 2 and ser[1]["dtgc"] == 1, ser[1]
    assert abs(ser[1]["seal_rate"] - 3 / 5.0) < 1e-9, ser[1]
    _mk("zt", [{"日期": f"2026-09-{d:02d}", "名称": f"N{d}", "连板数": 1}
               for d in range(1, 15)])
    _p = _zt_panel_day("zt", root=tmp)
    assert len(_p["series"]) == ZT_SERIES_DAYS, _p["series"]   # window capped
    assert max(_p["series"]) == "2026-09-14", _p["series"]     # newest kept
    long_s = (_zt_risk_face(root=tmp).get("series") or [])
    assert len(long_s) == ZT_SERIES_DAYS, long_s               # union capped too
    assert long_s[-1]["date"] == "2026-10-29", long_s          # other panels' newest wins
    _mk("zt", [{"日期": "2026-10-28", "名称": "A", "连板数": 1},
               {"日期": "2026-10-29", "名称": "B", "连板数": 1},
               {"日期": "2026-10-29", "名称": "C", "连板数": 3},
               {"日期": "2026-10-29", "名称": "D", "连板数": 2}])
    assert _zt_risk_face(root=os.path.join(tmp, "nope")).get("series") is None
    empty = _zt_risk_face(root=os.path.join(tmp, "nope"))
    assert empty["present"] is False and "缺" in empty["note"], empty
    _combat_face = lambda: {
        "paper_summary": {"traders": 1, "total_equity_cny": 100, "total_positions": 2,
                          "entries_today": 2, "exits_today": 0},
        "traders": [{"trader": "T1", "capital_cny": 1000000, "positions": 2, "dd": -0.01, "guard": "shadow"}],
        "account_families": [{"family": "AGGR", "account": "AGGR-X", "equity_cny": 1000001, "state_label": "ok"}],
        "market_clock": {"asof": "2026-09-24", "clock_cell": "ORANGE_COOL",
                         "position_cap_ladder": 0.5, "active_sleeves": ["chop-corps on duty"]},
        "marks_asof": "2026-09-24",
    }
    _rd_face = lambda now: {"commits_24h": 3, "result_jsons_landed_24h": 5, "digests_landed_24h": 1,
                            "prereg_md_touched_24h": 2, "compute_audit_latest": {"cpu_pct": 90},
                            "watermark_verdict": "loaded_ok", "pool_keys_n": 2, "batch_in_flight": True}
    _decision_face = lambda n=6: ["- 2026-09-26 09:47 · test-decision · reason · ptr"]
    _queue_face = lambda: [{"id": "T-X", "status": "open", "type": "t", "immediate": True, "owner": ""}]
    _token_face = lambda: {"total_state_tokens_est": 1000, "total_report_tokens_est": 500,
                           "delta_vs_prev": {}, "method": "bytes/3.5 est"}
    _utilization_face = lambda now: {
        "machines": {"bm-c": {"latest_ts": "2026-09-26 10:00:00",
                              "py_pct": 4.2, "cpu_pct": 23.0, "ready": 2,
                              "streak_min": None, "verdict": "FLAG:supply_floor",
                              "py_series_tail": [("10:00", 4.2), ("09:50", 3.1)],
                              "today_samples": 2, "today_floor_ok": 0,
                              "today_sla_flags": 0, "today_supply_gap_flags": 0}},
        "fill_ledger": "T-107 slice-2 pending -- honest label",
        "canon": "O-20260928-1614 sec.6"}
    _live_face = lambda day: {
        "status": "ok", "day": "2026-09-26", "state": "ORANGE",
        "rung": "ORANGE", "cap": 0.5, "heat": "COOL",
        "clock_cell": "ORANGE_COOL", "members": 6,
        "md_link": f"../live_usage/LIVE-2026-09-26.md"}
    _core_spread_face = lambda day: {
        "day": "2026-09-26",
        "machines": {"bm-a": {"batches_judged": 2, "core_seconds": 330.0,
                              "wall_seconds": 60.0, "effective_cores": 5.5,
                              "single_core_burn": 1, "multicore_burn": 1,
                              "too_short": 0, "last_ts": "x"},
                     "bm-b": {"batches_judged": 0, "core_seconds": 0.0,
                              "wall_seconds": 0.0, "effective_cores": None,
                              "single_core_burn": 0, "multicore_burn": 0,
                              "too_short": 0, "last_ts": None,
                              "audit_window": {"readable": True, "window_min": 60.0,
                                               "audit_batches": 0,
                                               "audit_ts": "2026-09-26 09:00:00"}},
                     "bm-c": {"batches_judged": 0, "core_seconds": 0.0,
                              "wall_seconds": 0.0, "effective_cores": None,
                              "single_core_burn": 0, "multicore_burn": 0,
                              "too_short": 0, "last_ts": None,
                              "audit_window": {"readable": False, "window_min": 60.0,
                                               "audit_batches": 0,
                                               "audit_ts": None}}},
        "canon": "T-134 s4"}
    _engine_wave_face = lambda: {
        "present": True, "last_registered": 113, "last_owner": "bm-c",
        "next_registration": 114, "next_seatable": 115,
        "chain_head": 610948, "k": 244320,
        "waves": [{"wave": 111, "owner": "bm-b", "a": None, "b_exit": None,
                   "shards_done": 12, "shards_total": 12,
                   "finalize_landed": True, "ledger_total": 610348,
                   "merged_mu": -0.0927, "merged_sigma": 0.2448, "k": 244200},
                  {"wave": 112, "owner": "bm-a", "a": None, "b_exit": None,
                   "shards_done": 12, "shards_total": 12,
                   "finalize_landed": True, "ledger_total": 610948,
                   "merged_mu": -0.0928, "merged_sigma": 0.2449, "k": 244320},
                  {"wave": 113, "owner": "bm-c", "a": None, "b_exit": None,
                   "shards_done": 12, "shards_total": 12,
                   "finalize_landed": False}],
        "seats": [{"wave": 114, "machine": "bm-a"}]}
    _attribution_face = lambda now: {
        "status": "ok", "asof": "2026-09-26", "report_day": "2026-09-26",
        "asof_note": "面板 marks asof=2026-09-26（当日 bar 未出=前交易日口径，如实标注）",
        "paper6": {"rows": [
            {"trader": "T1", "equity_cny": 1001000.0, "day_pnl_cny": 1000.0,
             "day_ret": 0.001, "status": "ok",
             "top_position": {"symbol": "511010", "unrealized_pnl_cny": 390.31}},
            {"trader": "T2", "equity_cny": 999000.0, "day_pnl_cny": None,
             "day_ret": None, "status": "no_prior_export",
             "status_label": "前值 export 件缺"}],
            "asof": "2026-09-26", "prior": "2026-09-25",
            "family_day_pnl_cny": 1000.0},
        "families": [
            {"family": "AGGR", "label": "进攻族", "n": 2, "asof": "2026-09-26",
             "family_day_pnl_cny": -500.0, "missing_n": 1, "rows": [
                 {"account": "AGGR-X", "status": "ok", "asof": "2026-09-26",
                  "prior": "2026-09-25", "day_pnl_cny": -500.0, "day_ret": -0.005,
                  "equity_cny": 995000.0},
                 {"account": "AGGR-Y", "status": "first_day", "asof": "2026-09-26",
                  "prior": None, "day_pnl_cny": None, "day_ret": None,
                  "equity_cny": 1000000.0}]},
            {"family": "SYSV1", "label": "路由族", "n": 1, "asof": "2026-09-26",
             "family_day_pnl_cny": 117.0, "missing_n": 0, "rows": [
                 {"account": "SYSTEM-V1", "status": "ok", "asof": "2026-09-26",
                  "prior": "2026-09-25", "day_pnl_cny": 117.0, "day_ret": 0.000117,
                  "equity_cny": 1000117.0, "state": "ORANGE", "w_eff": 0.3,
                  "pure_sleeve": False,
                  "route": {"rev_osc": 0.3, "trend": 0.1, "lowvol": 0.1, "cash": 0.5}}]},
            {"family": "ALLOC", "label": "配置族", "n": 0, "asof": None,
             "family_day_pnl_cny": None, "missing_n": 0, "rows": []}],
        "grand_day_pnl_cny": 617.0, "accounts_attributed": 3,
        "accounts_missing": 2,
        "method_note": "日对日差分=各面自带序列尾两行/六员逐日 export 链（聚合面零新判据）",
        "leg_note": "六员=一员一腿；AGGR/ALLOC/GRID=一账户一腿；SYSV1=route 腿权重面",
    }
    _zt_risk_face = lambda day=None, root=None: {
        "present": True, "cutoff": "2026-09-26", "cutoffs": ["2026-09-26"],
        "aligned": True,
        "panels": {
            "zt": {"label": "涨停池", "status": "ok", "count": 39,
                   "prev_cutoff": "2026-09-25", "prev_count": 44},
            "dtgc": {"label": "跌停池", "status": "ok", "count": 141,
                     "prev_cutoff": "2026-09-25", "prev_count": 35},
            "zbgc": {"label": "炸板池", "status": "ok", "count": 25,
                     "prev_cutoff": "2026-09-25", "prev_count": 20},
            "strong": {"label": "强势池", "status": "ok", "count": 119,
                       "prev_cutoff": "2026-09-25", "prev_count": 100}},
        "seal_rate": 0.6094, "down_over_up": 3.615, "kill_day": True,
        "ladder": {"1": 33, "2": 4, "3": 1, "4": 1},
        "top_streak": {"streak": 4, "n": 1, "names": ["TEST股份"]},
    }
    _stage_style_face = lambda: {
        "present": True, "cutoff": "2026-10-19",
        "window": {"lo": "2013-04-01", "hi": "2026-10-19", "bars": 3290},
        "reading": "UNSUPPORTED (honest negative)",
        "rule": "prereg sec.3/4 P4: best combo sharpe >= U-divlowvol + 0.10",
        "best_combo": {"cell": "C1", "sharpe_x1": 1.082985},
        "best_unconditional": {"face": "U-divlowvol", "sharpe_x1": 1.208542},
        "margin": -0.125557,
        "attribution": "combo gains trace to the divlowvol sleeve it already holds",
        "cells": ["C1", "C2", "U-divlowvol"],
        "state_days": {"BEAR": 786, "BULL": 201},
        "best_by_state": {"BEAR": {"cell": "U-EW", "sharpe": 0.11, "n_days": 786},
                          "BULL": {"cell": "C1", "sharpe": 2.98, "n_days": 201}},
    }
    rep = build_report(datetime(2026, 9, 26, 10, 0, 0))
    md = render_md(rep)
    for marker in ("一、实战面", "二、CEO 实盘使用面（T-105 直达）", "三、研发面",
                   "四、决策面", "五、明日队列", "Token 行", "ORANGE_COOL",
                   "六、算力利用率", "T-107 slice-2 pending", "FLAG:supply_floor",
                   "实盘一页纸直达", "核分布/并行效率三机对照（T-134 s4",
                   "有效核 5.5", "单核红牌 1", "有效核 N/A",
                   "当日零发射·采样器健康（近60min窗 0 批）",
                   "采样器读出不可用（compute_audit 面如实标注）",
                   "候选产线 · 常青 N1 波链", "链头 610948 runs",
                   "合并池 K 244320", "注册尾 W113（bm-c）",
                   "W111 bm-b 12/12 账落", "W113 bm-c 12/12 账待落",
                   "已占席 W114（bm-a）", "下一可席 W115",
                   "七、盈亏归因日账（A2 · G4 · 按 sleeve/腿）",
                   "面板 marks asof=2026-09-26（当日 bar 未出=前交易日口径，如实标注）",
                   "纸盘六员", "日 PnL 合计 1,000.00 CNY",
                   "T1: 日 PnL 1,000.00（+0.1000%）",
                   "持仓浮盈 top 511010 390.31（自入场累计）",
                   "前值 export 件缺",
                   "AGGR 进攻族", "AGGR-X: 日 PnL -500.00（-0.5000%）",
                   "AGGR-Y: 日 PnL N/A(缺数据)", "首日无前值", "缺数据 1 账户",
                   "SYSV1 路由族", "SYSTEM-V1: 日 PnL 117.00",
                   "路由 rev_osc 30%/trend 10%/lowvol 10%/cash 50%",
                   "w_eff 0.3", "跨族日 PnL 总计", "617.00 CNY",
                   "可归因账户 3 · 缺数据 2", "腿级注记",
                   "八、阶段×风格组合面", "UNSUPPORTED (honest negative)",
                   "C1 sharpe 1.082985 vs 无条件 U-divlowvol 1.208542",
                   "margin -0.1256", "各阶段态最优袖", "BULL **C1** +2.98（201d）",
                   "九、市场风险面", "四面同为 **2026-09-26**",
                   "**涨停池 39**（前 2026-09-25 44，-5）",
                   "**跌停池 141**（前 2026-09-25 35，+106）",
                   "封板率 60.9%", "连板梯队：1 板 33 / 2 板 4 / 3 板 1 / 4 板 1",
                   "最高 **4 连板**（1 只）：TEST股份", "跌停/涨停 = **3.615**",
                   "记为**杀跌日**；今日 是"):
        assert marker in md, marker
    assert rep["combat"]["traders"][0]["trader"] == "T1"
    assert rep["report_date"] == "2026-09-26"
    assert rep["live_usage"]["status"] == "ok"
    assert rep["pnl_attribution"]["grand_day_pnl_cny"] == 617.0
    print("daily_report selftest: PASS (5 faces + token line + clock cell "
          "+ A2/G4 attribution ledger legs)")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        sys.exit(selftest())
    if cmd == "run":
        sys.exit(run())
    print("usage: run | selftest", file=sys.stderr)
    sys.exit(2)
