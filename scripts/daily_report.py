# -*- coding: utf-8 -*-
"""Daily battle report -- T-75 (O-20260926-0940): ONE page + JSON twin, four faces + token line.

Faces (aggregation ONLY, zero new metrics/judgments invented; missing faces get honest labels):
  (a) COMBAT: paper-account scoreboard across families (6 in-register traders via
      results/paper_export/latest.json; AGGR-* via results/aggr_paper/*_paper.json;
      ALLOC-* via results/alloc_paper/*.json; CN-* when live) + market-clock current call
      (results/market_clock/call_latest.json) + guard face (per-trader regime_guard).
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
    audit = _read_json(os.path.join(ROOT, "results", "compute_audit.json")) or {}
    latest_audit = audit.get("latest") or {}
    wm = None
    try:
        with open(os.path.join(ROOT, "results", "watermark.jsonl"), encoding="utf-8") as f:
            lines = [ln for ln in f.read().splitlines() if ln.strip()]
        if lines:
            wm = json.loads(lines[-1])
    except Exception:
        pass
    pool = _read_json(os.path.join(ROOT, "results", "runnable_pool.json")) or {}
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


def build_report(now):
    return {
        "report_date": now.strftime("%Y-%m-%d"),
        "generated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "combat": _combat_face(),
        "rd": _rd_face(now),
        "decisions_tail": _decision_face(),
        "tomorrow_queue": _queue_face(),
        "token_line": _token_face(),
        "canon_refs": ["T-75 ticket (O-20260926-0940)", "results/paper_export/latest.json",
                       "results/market_clock/call_latest.json", "results/token_usage.json"],
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
    L.append("## 二、研发面（24h）")
    r = rep["rd"]
    L.append(f"- 提交 {r.get('commits_24h')} · 判定/结果件落地 {r.get('result_jsons_landed_24h')} · "
             f"调研 digest {r.get('digests_landed_24h')} · 预注册/正典触碰 {r.get('prereg_md_touched_24h')}")
    L.append(f"- 在飞批：{'是' if r.get('batch_in_flight') else '否'} · 水位判定 `{r.get('watermark_verdict')}` · "
             f"算力审计 `{json.dumps(r.get('compute_audit_latest'), ensure_ascii=False)[:160]}`")
    L.append("")
    L.append("## 三、决策面（今日 GM 自主决策日志尾）")
    for ln in rep.get("decisions_tail", []):
        L.append(f"- {ln[2:]}")
    L.append("")
    L.append("## 四、明日队列（公司自排优先级）")
    for q in rep.get("tomorrow_queue", [])[:12]:
        imm = " [immediate]" if q.get("immediate") else ""
        L.append(f"- {q['id']}({q['status']}{imm}) {q.get('type')} ← {q.get('owner') or '无人认领'}")
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
    print(f"daily report written: REPORT-{day}.md/.json faces=4 token=1")
    return 0


def selftest():
    """Hermetic: synthetic faces -> page renders with all four faces + token line."""
    global _combat_face, _rd_face, _decision_face, _queue_face, _token_face
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
    rep = build_report(datetime(2026, 9, 26, 10, 0, 0))
    md = render_md(rep)
    for marker in ("一、实战面", "二、研发面", "三、决策面", "四、明日队列", "Token 行", "ORANGE_COOL"):
        assert marker in md, marker
    assert rep["combat"]["traders"][0]["trader"] == "T1"
    assert rep["report_date"] == "2026-09-26"
    print("daily_report selftest: PASS (4 faces + token line + clock cell render)")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        sys.exit(selftest())
    if cmd == "run":
        sys.exit(run())
    print("usage: run | selftest", file=sys.stderr)
    sys.exit(2)
