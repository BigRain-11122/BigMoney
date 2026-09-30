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
        "canon_refs": ["T-75 ticket (O-20260926-0940)", "results/paper_export/latest.json",
                       "results/market_clock/call_latest.json", "results/token_usage.json",
                       "T-105 v1.3 live-usage embedded section (docs/live_usage/)",
                       "O-20260928-1614 sec.6 utilization face (T-107)",
                       "T-134 s4 core-spread/parallel-efficiency row (O-2026-09-30-2355)"],
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
    global _utilization_face, _live_face, _core_spread_face
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
    rep = build_report(datetime(2026, 9, 26, 10, 0, 0))
    md = render_md(rep)
    for marker in ("一、实战面", "二、CEO 实盘使用面（T-105 直达）", "三、研发面",
                   "四、决策面", "五、明日队列", "Token 行", "ORANGE_COOL",
                   "六、算力利用率", "T-107 slice-2 pending", "FLAG:supply_floor",
                   "实盘一页纸直达", "核分布/并行效率三机对照（T-134 s4",
                   "有效核 5.5", "单核红牌 1", "有效核 N/A",
                   "当日零发射·采样器健康（近60min窗 0 批）",
                   "采样器读出不可用（compute_audit 面如实标注）"):
        assert marker in md, marker
    assert rep["combat"]["traders"][0]["trader"] == "T1"
    assert rep["report_date"] == "2026-09-26"
    assert rep["live_usage"]["status"] == "ok"
    print("daily_report selftest: PASS (5 faces + token line + clock cell render)")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        sys.exit(selftest())
    if cmd == "run":
        sys.exit(run())
    print("usage: run | selftest", file=sys.stderr)
    sys.exit(2)
