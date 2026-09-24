"""Periodic self-review aggregator (CEO order O-20260924-1110; ticket T-2026-09-24-12; charter=firm/SELF_REVIEW.md v1.0).

L1 deterministic aggregator, monthly_briefing.py pattern: zero network / zero
engine / zero token. SR1-SR5 checklist frozen v1.0 in the charter BEFORE first
run (science_audit precedent); findings are REPORT-ONLY and never block; P0
findings auto-ticket; CEO is surfaced only for the 4 reserved items. Scores and
judgements never gate anything here -- hr.py/science_audit.py stay the sole
authorities in their domains; this file only aggregates existing on-disk
evidence and references (zero double-legislation).

Subcommands:
  run [--month YYYYMM] : write results/self_review/SELF-REVIEW-<YYYYMM>.md and
                         refresh the append-only monthly ledger + team ledger.
                         Default month = previous month (monthly package for M
                         is produced in first rounds of M+1). Idempotent.
  selftest             : offline synthetic-fixture checks (J18 self-consistency:
                         fixtures match the real aggregation shapes). Zero
                         network, zero writes outside temp dir.

Exit codes: 0 normal (findings never block); 2 mechanism error.
"""

import json
import re
import subprocess
import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SR_DIR = ROOT / "results" / "self_review"
LEDGER = SR_DIR / "self_review_ledger.json"
TEAM_LEDGER = SR_DIR / "team_ledger.json"

CHARTER_NOTE = (
    "判据=firm/SELF_REVIEW.md v1.0 冻结清单（SR1-SR5）；发现只报不阻断；"
    "P0=修复单自动入队；特别重大（实盘/红线/使命/重大资源）=唯一 CEO 呈报面。"
    "本包=只读聚合台账，集团夜轮/周轮/科学审计唯一权威引用不重跑，计数单源零手抄。"
)

_CN_NUM = {"零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6,
           "七": 7, "八": 8, "九": 9, "十": 10, "十一": 11, "十二": 12}


def _read_json(path):
    try:
        with open(path, encoding="utf-8-sig") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except (json.JSONDecodeError, OSError):
        return None


def _f(x, nd=4):
    try:
        return f"{float(x):.{nd}f}"
    except (TypeError, ValueError):
        return "-"


def _month_gate(s):
    """YYYYMM gate (briefing R57 precedent): 6 digits, month 01-12."""
    if not (isinstance(s, str) and len(s) == 6 and s.isdigit()):
        return False
    m = int(s[4:6])
    return 1 <= m <= 12


def _prev_month(today=None):
    today = today or date.today()
    y, m = today.year, today.month - 1
    if m == 0:
        y, m = y - 1, 12
    return f"{y:04d}{m:02d}"


def _parse_ts(s):
    if not isinstance(s, str):
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(s[:19] if "%z" not in fmt else s, fmt)
        except ValueError:
            continue
    return None


def _age_min(ts, now=None):
    t = _parse_ts(ts)
    if t is None:
        return None
    return round(((now or datetime.now()) - t).total_seconds() / 60.0, 1)


def _fmt_ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------- SR1 science

def sr1_science(base):
    """Reference latest science_audit run (never re-run it)."""
    d = _read_json(base / "results" / "science_audit.json") or {}
    cur = d.get("current") or {}
    checks = cur.get("checks") or []
    non_ok = []
    for c in checks:
        name = c.get("check") or c.get("name") or "?"
        verdict = str(c.get("verdict") or c.get("status") or c.get("result") or "?")
        if "OK" not in verdict.upper():
            non_ok.append(f"{name}:{verdict}")
    hist = d.get("history") or []
    c2_trend = []
    for h in hist:
        n = 0
        for c in (h.get("checks") or []):
            name = str(c.get("check") or c.get("name") or "")
            verdict = str(c.get("verdict") or c.get("status") or c.get("result") or "")
            if name.startswith("C2") and "OK" not in verdict.upper():
                n += 1
        c2_trend.append(n)
    head = (cur.get("ledger_head") or {}).get("total")
    return {
        "source": "results/science_audit.json (reference only)",
        "generated": cur.get("generated"),
        "ledger_head_total": head,
        "checks_total": len(checks),
        "checks_non_ok": non_ok,
        "history_runs": len(hist),
        "c2_violation_trend": c2_trend,
    }


# -------------------------------------------------------------------- SR2 KPI

def _ledger_head(base, sub=""):
    """Single-source counts: max trials_ledger.total over results JSONs."""
    best = 0
    src = None
    for p in sorted((base / "results").glob(f"{sub}*.json")) + (sorted((base / "results" / "shortline").glob("*.json")) if sub == "" else []):
        d = _read_json(p)
        if not isinstance(d, dict):
            continue
        tl = d.get("trials_ledger")
        if isinstance(tl, dict) and isinstance(tl.get("total"), (int, float)):
            if tl["total"] > best:
                best, src = tl["total"], p.name
        elif isinstance(tl, list) and tl:
            tot = sum(x.get("n", 0) for x in tl if isinstance(x, dict))
            if tot > best:
                best, src = tot, p.name
    return {"total": best, "file": src}


def sr2_kpi(base):
    """KPI snapshot via pointer files (counts single-source, no hardcodes)."""
    traders = [p for p in sorted((base / "firm" / "traders").glob("*.json")) if not p.stem.startswith("_")]
    engine = _ledger_head(base, "")
    factor = _ledger_head(base, "shortline_")
    paper = []
    for p in sorted((base / "results" / "paper").glob("*_paper.json")):
        d = _read_json(p) or {}
        paper.append({"id": p.stem.replace("_paper", ""),
                      "months": d.get("months_tracked"),
                      "bars": len(d.get("bars", [])) if isinstance(d.get("bars"), list) else d.get("bars")})
    ew6 = _read_json(base / "results" / "portfolio_ew6.json") or {}
    iv6 = _read_json(base / "results" / "portfolio_iv6.json") or {}
    sc = _read_json(base / "results" / "scorecard_v1.json") or {}
    return {
        "traders_n": len(traders),
        "traders_ids": [p.stem for p in traders],
        "engine_ledger": engine,
        "factor_ledger": factor,
        "paper": paper[:8],
        "portfolio_ew6_sharpe": (ew6.get("portfolios") or ew6).get("sharpe_full") if isinstance((ew6.get("portfolios") or ew6), dict) else None,
        "portfolio_iv6_sharpe": (iv6.get("portfolios_iv") or iv6.get("portfolios") or iv6).get("sharpe_full") if isinstance((iv6.get("portfolios_iv") or iv6.get("portfolios") or iv6), dict) else None,
        "scorecard_best": sc.get("best") or (sc.get("summary") or {}).get("best"),
    }


# --------------------------------------------------------------------- SR3 org

def _team_rows(base):
    """Parse org_chart v3 team table (| 部门 | 团队 | mandate | 近期交付 |)."""
    path = base / "firm" / "org_chart.md"
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return []
    rows = []
    in_table = False
    for line in text.splitlines():
        if line.strip().startswith("#") and "团队表" in line:
            in_table = True
            continue
        if in_table:
            if line.strip().startswith("#"):
                break
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 4 and cells[1] and "团队" not in cells[1][:2] and set(cells[0]) != {"-"}:
                rows.append({"dept": cells[0], "team": cells[1], "mandate": cells[2]})
    return rows


def _narrative_numbers(text):
    """Extract explicit count mentions: returns dict of kind->[(num, snippet)]."""
    found = {"machines": [], "depts": [], "teams": [], "roster": []}
    for m in re.finditer(r"([一二三四五六七八九十\d]+)\s*(?:台机器|机(?!制|构|遇|器|会))", text):
        found["machines"].append((_CN_NUM.get(m.group(1), None) if not m.group(1).isdigit() else int(m.group(1)), m.group(0)))
    for m in re.finditer(r"([一二三四五六七八九十\d]+)\s*部门", text):
        found["depts"].append((_CN_NUM.get(m.group(1), None) if not m.group(1).isdigit() else int(m.group(1)), m.group(0)))
    for m in re.finditer(r"([一二三四五六七八九十\d]+)\s*团队", text):
        found["teams"].append((_CN_NUM.get(m.group(1), None) if not m.group(1).isdigit() else int(m.group(1)), m.group(0)))
    for m in re.finditer(r"([一二三四五六七八九十\d]+)\s*员", text):
        found["roster"].append((_CN_NUM.get(m.group(1), None) if not m.group(1).isdigit() else int(m.group(1)), m.group(0)))
    return found


def sr3_org(base, team_ledger, now=None):
    """Law-vs-reality reconciliation + team anti-vanity ledger (90d/30d warn)."""
    now = now or datetime.now()
    machines = sorted((base / "fleet" / "machines").glob("*.json"))
    machine_ids = [p.stem for p in machines]
    traders = [p for p in sorted((base / "firm" / "traders").glob("*.json")) if not p.stem.startswith("_")]
    rows = _team_rows(base)
    narrative_text = ""
    for f in ("firm/org_chart.md", "firm/OPERATING_PLAN.md"):
        try:
            narrative_text += open(base / f, encoding="utf-8").read()
        except OSError:
            pass
    narr = _narrative_numbers(narrative_text)

    drift = []
    for kind, actual in (("machines", len(machine_ids)), ("teams", len(rows)), ("roster", len(traders))):
        nums = {n for n, _ in narr[kind] if n is not None}
        if nums and actual not in nums:
            drift.append(f"{kind}: narrative {sorted(nums)} vs actual {actual} ({', '.join(s for _, s in narr[kind][:3])})")

    for r in rows:
        t = team_ledger["teams"].setdefault(r["team"], {"first_seen": _fmt_ts(), "last_delivery": None})
        t.setdefault("first_seen", _fmt_ts())
    team_states = []
    for name, t in team_ledger["teams"].items():
        ld = _parse_ts(t.get("last_delivery"))
        age_days = (now - ld).days if ld else None
        state = "no_delivery_history"
        if age_days is not None:
            if age_days > 90:
                state = "ANTI_VANITY_BREACH >90d"
            elif age_days > 60:
                state = "warn_30d"
        team_states.append({"team": name, "age_days": age_days, "state": state})
    return {
        "machines": machine_ids,
        "traders_n": len(traders),
        "teams_n": len(rows),
        "narrative_drift": drift,
        "team_ledger_states": team_states,
        "team_ledger_note": "delivery history starts at T-12 (2026-09); 90-day anti-vanity law accrues going forward; last_delivery set by future rounds",
    }


# ---------------------------------------------------------------- SR4 process

def _order_tokens(base):
    toks = []
    for p in sorted((base / "fleet" / "orders").glob("O-*.md")):
        stem = p.stem
        parts = stem.split("-")
        toks.append("-".join(parts[:3]) if len(parts) >= 3 else stem)
    return toks


def sr4_process(base, log_lines=None):
    """Ticket aging / orders ack diff / duplicate maintenance scan / C2 trend."""
    now = datetime.now()
    findings = []
    tickets = []
    for p in sorted((base / "fleet" / "tasks").glob("*.json")):
        d = _read_json(p)
        if not d:
            continue
        st = d.get("status")
        created = _parse_ts(d.get("created_at"))
        claimed = _parse_ts(d.get("claimed_at"))
        age_h = round((now - created).total_seconds() / 3600.0, 1) if created else None
        tickets.append({"id": d.get("id"), "status": st, "age_h": age_h})
        if st == "open" and age_h is not None and age_h > 72:
            findings.append({"check": "SR4", "severity": "P1",
                             "text": f"ticket {d.get('id')} open >72h ({age_h}h) -> FLEET-OPS s5 release clause review"})
        if st == "claimed" and claimed is not None:
            ch = round((now - claimed).total_seconds() / 3600.0, 1)
            if ch > 24:
                findings.append({"check": "SR4", "severity": "P2",
                                 "text": f"ticket {d.get('id')} claimed >24h ({ch}h) -> release-clause check"})

    ack_missing = {}
    tokens = _order_tokens(base)
    for m in sorted((base / "fleet" / "machines").glob("*.json")):
        d = _read_json(m) or {}
        ack = d.get("orders_ack")
        ack = " ".join(ack) if isinstance(ack, list) else (ack or "")
        miss = [t for t in tokens if t not in ack]
        if miss:
            ack_missing[m.stem] = miss
    for mid, miss in ack_missing.items():
        findings.append({"check": "SR4", "severity": "P1",
                         "text": f"orders_ack diff non-empty on {mid}: {', '.join(miss)}"})

    if log_lines is None:
        try:
            out = subprocess.run(
                ["git", "-C", str(base), "log", "--since=14 days ago",
                 "--pretty=format:%cI|%s"],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30, check=True)
            log_lines = out.stdout.splitlines()
        except Exception:
            log_lines = []
    dups = _maintenance_duplicate_scan(log_lines)
    for w, machines in dups:
        findings.append({"check": "SR4", "severity": "P2",
                         "text": f"same-window periodic maintenance by {len(machines)} machines at {w} (F-09 family): {', '.join(sorted(machines))}"})
    return {"tickets": tickets, "ack_missing": ack_missing,
            "duplicate_windows": dups, "findings": findings}


def _maintenance_duplicate_scan(log_lines):
    """30-min-bucket scan: >1 machine doing periodic maintenance in one bucket."""
    kw = ("HANDOVER", "5x", "science_audit", "monthly_briefing", "scorecard", "token")
    buckets = {}
    for line in log_lines:
        try:
            ts_s, subject = line.split("|", 1)
        except ValueError:
            continue
        low = subject.lower()
        if not any(k in low for k in kw):
            continue
        mach = None
        for m in ("bm-a", "bm-b", "bm-c"):
            if m in subject:
                mach = m
                break
        if not mach:
            continue
        t = _parse_ts(ts_s)
        if t is None:
            continue
        bucket = t.strftime("%Y-%m-%d %H:") + ("00" if t.minute < 30 else "30")
        buckets.setdefault(bucket, set()).add(mach)
    return [(w, ms) for w, ms in sorted(buckets.items()) if len(ms) > 1]


# --------------------------------------------------------------- SR5 resources

def sr5_resources(base, prev_entry, now=None):
    now = now or datetime.now()
    tu = _read_json(base / "results" / "token_usage.json") or {}
    codely_bytes = 0
    try:
        codely_bytes = (base / "CODELY.md").stat().st_size
    except OSError:
        pass
    ca = _read_json(base / "results" / "compute_audit.json") or {}
    latest = ca.get("latest") or {}
    flags = latest.get("flags") or []
    blocked = []
    for p in sorted((base / "results").glob("*update_status.json")) + [base / "results" / "pb_heat_pull_status.json"]:
        if not p.exists():
            continue
        d = _read_json(p)
        if not isinstance(d, dict):
            continue
        mode = str(d.get("mode") or d.get("status") or "")
        if "block" in mode or "conn_stopped" in mode:
            ts = d.get("last_attempt") or d.get("ts") or d.get("generated")
            blocked.append({"file": p.name, "mode": mode, "age_min": _age_min(ts, now)})
    tokens_est = tu.get("total_state_tokens_est")
    prev_bytes = (prev_entry or {}).get("codely_bytes")
    return {
        "token_state_est": tokens_est,
        "token_delta_vs_prev": tu.get("delta_vs_prev"),
        "codely_bytes": codely_bytes,
        "codely_bytes_delta_vs_prev": (codely_bytes - prev_bytes) if prev_bytes else None,
        "compute_flags": flags,
        "compute_cpu_pct": latest.get("cpu_total_pct"),
        "blocked_sources": blocked,
    }


# -------------------------------------------------------------- gather/render

def gather(month, base=ROOT, now=None):
    now = now or datetime.now()
    ledger = _read_json(LEDGER) if base == ROOT else _read_json(base / "results" / "self_review" / "self_review_ledger.json")
    ledger = ledger or {"history": []}
    team_ledger = _read_json(TEAM_LEDGER) if base == ROOT else _read_json(base / "results" / "self_review" / "team_ledger.json")
    team_ledger = team_ledger or {"teams": {}}
    prev = next((h for h in reversed(ledger["history"]) if h.get("month") != month), None)

    sr1 = sr1_science(base)
    sr2 = sr2_kpi(base)
    sr3 = sr3_org(base, team_ledger, now)
    sr4 = sr4_process(base)
    sr5 = sr5_resources(base, prev, now)

    findings = list(sr4.get("findings") or [])
    for d in sr3["narrative_drift"]:
        findings.append({"check": "SR3", "severity": "P1", "text": f"law-vs-reality drift: {d}"})
    for b in sr5["blocked_sources"]:
        if (b.get("age_min") or 0) > 60:
            findings.append({"check": "SR5", "severity": "P2",
                             "text": f"data source blocked/parked >60min: {b['file']} ({b['mode']}, {b['age_min']}min)"})
    if sr5["token_state_est"] is not None and sr5["token_state_est"] > 100000:
        findings.append({"check": "SR5", "severity": "P1",
                         "text": f"token red flag ongoing (F-07/F-10): state-token estimate {sr5['token_state_est']} >100k per round"})
    if sr5["codely_bytes"] and sr5["codely_bytes"] > 400_000:
        findings.append({"check": "SR5", "severity": "P2",
                         "text": f"CODELY.md size {sr5['codely_bytes']} bytes >400KB (F-07 hot-layer growth)"})
    for t in sr3["team_ledger_states"]:
        if t["state"].startswith("ANTI_VANITY"):
            findings.append({"check": "SR3", "severity": "P2", "text": f"team {t['team']}: {t['state']}"})

    data = {"month": month, "generated": _fmt_ts(), "sr1": sr1, "sr2": sr2,
            "sr3": sr3, "sr4": {k: v for k, v in sr4.items() if k != "findings"},
            "sr5": sr5, "findings": findings}
    return data, ledger, team_ledger


def render(d):
    L = []
    L.append(f"# 月度自审包 SELF-REVIEW-{d['month']}")
    L.append("")
    L.append(f"> 生成：{d['generated']} · 章程：firm/SELF_REVIEW.md v1.0（判据冻结） · {CHARTER_NOTE}")
    L.append("")
    s1, s2, s3, s4, s5 = d["sr1"], d["sr2"], d["sr3"], d["sr4"], d["sr5"]
    L.append("## SR1 科学面（science_audit 引用·不重跑）")
    L.append(f"- 最新 run：{s1['generated']} · 链头 N={s1['ledger_head_total']} · checks {s1['checks_total']} 项（非 OK：{', '.join(s1['checks_non_ok']) or '无'}）· history {s1['history_runs']} 轮 · C2 违规趋势 {s1['c2_violation_trend']}")
    L.append("")
    L.append("## SR2 经营面（KPI 指针快照·计数单源）")
    L.append(f"- 在册交易员 {s2['traders_n']}（{', '.join(s2['traders_ids']) or '-'}）· 引擎账本 N={_f(s2['engine_ledger']['total'], 0)}（{s2['engine_ledger']['file']}）· 因子账本 N={_f(s2['factor_ledger']['total'], 0)}（{s2['factor_ledger']['file']}）")
    if s2["scorecard_best"]:
        L.append(f"- 记分卡最优：{s2['scorecard_best']}")
    pp = ", ".join(f"{x['id']} {x['months']}月" for x in s2["paper"]) or "-"
    L.append(f"- paper：{pp} · EW6 Sharpe {_f(s2['portfolio_ew6_sharpe'], 4)} · IV6 Sharpe {_f(s2['portfolio_iv6_sharpe'], 4)}")
    L.append("")
    L.append("## SR3 组织面（法件实况对账+团队台账）")
    L.append(f"- 机器 {len(s3['machines'])}（{', '.join(s3['machines'])}）· 部门叙述扫描 · 团队表 {s3['teams_n']} 行 · 在册 {s3['traders_n']}")
    L.append(f"- 叙述漂移：{'; '.join(s3['narrative_drift']) or '无'}")
    L.append(f"- 团队台账：{s3['team_ledger_note']}")
    for t in s3["team_ledger_states"]:
        L.append(f"  - {t['team']}: {t['state']}" + (f"（{t['age_days']}d）" if t["age_days"] is not None else ""))
    L.append("")
    L.append("## SR4 流程面（票据 aging/令牌差集/重复维护/C2 趋势）")
    tk = ", ".join(f"{t['id']}={t['status']}({t['age_h']}h)" for t in s4["tickets"]) or "-"
    L.append(f"- 票据：{tk}")
    L.append(f"- 令牌 ack 差集：{json.dumps(s4['ack_missing'], ensure_ascii=False) if s4['ack_missing'] else 'EMPTY（全机已回执）'}")
    L.append(f"- 同窗维护重复（14d/30min 桶）：{len(s4['duplicate_windows'])} 例" + (f"——{s4['duplicate_windows']}" if s4["duplicate_windows"] else ""))
    L.append("")
    L.append("## SR5 资源面（token/CODELY 体积/算力/阻断源）")
    L.append(f"- token 状态层粗估 {s5['token_state_est']} /轮 · 增量 {s5['token_delta_vs_prev']} · CODELY.md {s5['codely_bytes']} B（环比 {s5['codely_bytes_delta_vs_prev']}）")
    L.append(f"- compute_audit 旗：{s5['compute_flags'] or 'CLEAN'} · CPU {s5['compute_cpu_pct']}%")
    bl = ", ".join(f"{b['file']}（{b['mode']}，{b['age_min']}min）" for b in s5["blocked_sources"]) or "无"
    L.append(f"- 阻断/停泊源：{bl}")
    L.append("")
    L.append("## 发现（只报不阻断）")
    if d["findings"]:
        for f_ in d["findings"]:
            L.append(f"- [{f_['severity']}] {f_['text']}")
    else:
        L.append("- 无")
    L.append("")
    L.append("> P0 发现→修复单自动入队；特别重大=唯一 CEO 呈报面（四类保留）；本包并入月度经营简报「自审」节。")
    L.append("")
    return "\n".join(L)


def _atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    import os
    os.replace(tmp, path)


def cmd_run(month):
    if not _month_gate(month):
        print(f"self_review: invalid month '{month}' (expect YYYYMM, month 01-12)", file=sys.stderr)
        return 2
    data, ledger, team_ledger = gather(month)
    entry = {"month": month, "generated": data["generated"],
             "findings_n": len(data["findings"]),
             "findings": [f["text"] for f in data["findings"]],
             "codely_bytes": data["sr5"]["codely_bytes"],
             "token_state_est": data["sr5"]["token_state_est"],
             "engine_n": data["sr2"]["engine_ledger"]["total"],
             "factor_n": data["sr2"]["factor_ledger"]["total"],
             "traders_n": data["sr2"]["traders_n"]}
    ledger["history"] = [h for h in ledger["history"] if h.get("month") != month]
    ledger["history"].append(entry)
    ledger["history"].sort(key=lambda h: h.get("month") or "")
    _atomic_write(SR_DIR / "self_review_ledger.json",
                 json.dumps(ledger, ensure_ascii=False, indent=1))
    _atomic_write(TEAM_LEDGER, json.dumps(team_ledger, ensure_ascii=False, indent=1))
    _atomic_write(SR_DIR / f"SELF-REVIEW-{month}.md", render(data))
    _atomic_write(SR_DIR / f"SELF-REVIEW-{month}.json", json.dumps(data, ensure_ascii=False, indent=1, default=str))
    print(f"self_review: SELF-REVIEW-{month}.md written; findings={len(data['findings'])} (report-only)")
    for f_ in data["findings"]:
        print(f"  [{f_['severity']}] {f_['text']}")
    return 0


# ------------------------------------------------------------------- selftest

def _mkfixture(td):
    """Synthetic fixtures matching REAL aggregation shapes (J18 self-consistency)."""
    res = td / "results"
    (res / "self_review").mkdir(parents=True, exist_ok=True)
    (res / "briefings").mkdir(exist_ok=True)
    (td / "firm" / "traders").mkdir(parents=True, exist_ok=True)
    (td / "fleet" / "machines").mkdir(parents=True, exist_ok=True)
    (td / "fleet" / "tasks").mkdir(parents=True, exist_ok=True)
    (td / "fleet" / "orders").mkdir(parents=True, exist_ok=True)
    _atomic_write(res / "science_audit.json", json.dumps({
        "current": {"generated": "2026-09-24 08:20:45",
                    "ledger_head": {"total": 3041, "file": "x.json"},
                    "checks": [{"check": "C1_null_drift", "verdict": "OK"},
                               {"check": "C2_lockbox", "verdict": "VIOLATION: file z"}]},
        "history": [{"generated": "2026-09-24 04:20:00",
                     "checks": [{"check": "C2_lockbox", "verdict": "OK"}]}]}))
    for i in range(3):
        _atomic_write(td / "firm" / "traders" / f"TR-{i}.json", json.dumps({"id": f"TR-{i}"}))
    _atomic_write(res / "shortline_x.json", json.dumps({"trials_ledger": {"total": 100}}))
    _atomic_write(res / "paper" / "T-0_paper.json", json.dumps({"months_tracked": 0})) if (res / "paper").mkdir(exist_ok=True) is None else None
    _atomic_write(td / "firm" / "org_chart.md",
                  "## 团队表（11 团队）\n\n| 部门 | 团队 | mandate | 近期交付 |\n|---|---|---|---|\n"
                  "| 数据部 | 双源与核名团队 | 日线双腿 | fallback 实证 |\n"
                  "| 工程部 | 盯防与算力运维团队 | watchdog | 首例 |\n\n正文提到六员与三机。\n")
    _atomic_write(td / "firm" / "OPERATING_PLAN.md", "九部门三机拓扑。\n")
    _atomic_write(td / "fleet" / "machines" / "bm-a.json",
                  json.dumps({"machine_id": "bm-a", "orders_ack": "O-20260901-0100"}))
    _atomic_write(td / "fleet" / "machines" / "bm-b.json",
                  json.dumps({"machine_id": "bm-b", "orders_ack": ["O-20260901-0100", "O-20260902-0200"]}))
    _atomic_write(td / "fleet" / "orders" / "O-20260901-0100-bm-a.md", "# o1")
    _atomic_write(td / "fleet" / "orders" / "O-20260902-0200-bm-c.md", "# o2")
    _atomic_write(td / "fleet" / "tasks" / "T-OLD.json",
                  json.dumps({"id": "T-OLD", "status": "open", "created_at": "2026-09-01 00:00:00"}))
    _atomic_write(td / "fleet" / "tasks" / "T-CL.json",
                  json.dumps({"id": "T-CL", "status": "claimed", "created_at": "2026-09-20 00:00:00",
                              "claimed_at": "2026-09-20 01:00:00"}))
    _atomic_write(res / "token_usage.json",
                  json.dumps({"total_state_tokens_est": 110000, "delta_vs_prev": 100}))
    _atomic_write(res / "moneyflow_update_status.json",
                  json.dumps({"mode": "refresh source-blocked", "last_attempt": "2026-09-24 08:00:00"}))
    _atomic_write(res / "compute_audit.json",
                  json.dumps({"latest": {"cpu_total_pct": 10.0, "flags": []}}))
    return res


def cmd_selftest():
    ok = 0
    total = 0

    def check(name, cond):
        nonlocal ok, total
        total += 1
        print(f"  [selftest] {name}... {'PASS' if cond else 'FAIL'}")
        if cond:
            ok += 1

    with tempfile.TemporaryDirectory() as tds:
        td = Path(tds)
        _mkfixture(td)
        # 1 month gate
        check("month gate valid/invalid", _month_gate("202609") and not _month_gate("2026-13") and not _month_gate("2026-9"))
        # 2 SR1 reference extraction (real shape)
        s1 = sr1_science(td)
        check("SR1 non-OK extraction", s1["checks_total"] == 2 and len(s1["checks_non_ok"]) == 1 and s1["ledger_head_total"] == 3041)
        check("SR1 C2 trend", s1["c2_violation_trend"] == [0])
        # 3 SR3 drift: narrative 六员(6)/三机(3) vs actual roster 3 / machines 2
        tl = {"teams": {}}
        s3 = sr3_org(td, tl, now=datetime(2026, 9, 24, 11, 0, 0))
        check("SR3 team rows parsed", s3["teams_n"] == 2)
        check("SR3 drift detected", any("roster" in x for x in s3["narrative_drift"]) and any("machines" in x for x in s3["narrative_drift"]))
        check("SR3 team ledger cold-start", all(t["state"] == "no_delivery_history" for t in s3["team_ledger_states"]))
        # 4 SR4 aging + ack diff (real shapes)
        s4 = sr4_process(td)
        check("SR4 ticket aging >72h fired", any("T-OLD" in f["text"] for f in s4["findings"]))
        check("SR4 claimed >24h note", any("T-CL" in f["text"] for f in s4["findings"]))
        check("SR4 ack diff (bm-a missing o2)", s4["ack_missing"].get("bm-a") == ["O-20260902-0200"])
        # 5 duplicate scan pure fn
        dups = _maintenance_duplicate_scan([
            "2026-09-24T10:31:00+08:00|round 43 bm-c: HANDOVER 5x check",
            "2026-09-24T10:35:00+08:00|round 60 bm-a: science_audit run monthly",
            "2026-09-24T11:05:00+08:00|round 61 bm-a: research batch (no kw)"])
        check("SR4 dup scan flags same-window", len(dups) == 1 and dups[0][1] == {"bm-a", "bm-c"})
        # 6 SR5 blocked + token red flag
        s5 = sr5_resources(td, None, now=datetime(2026, 9, 24, 11, 0, 0))
        check("SR5 blocked source aged", s5["blocked_sources"] and s5["blocked_sources"][0]["age_min"] == 180.0)
        check("SR5 token est read", s5["token_state_est"] == 110000)
        # 7 full gather + determinism
        d1, led, tld = gather("202609", base=td, now=datetime(2026, 9, 24, 11, 0, 0))
        r1 = render(d1)
        d2, _, _ = gather("202609", base=td, now=datetime(2026, 9, 24, 11, 0, 0))
        check("gather+render deterministic", r1 == render(d2))
        check("findings aggregated across SRs",
              any(f["check"] == "SR3" for f in d1["findings"]) and
              any(f["check"] == "SR4" for f in d1["findings"]) and
              any(f["check"] == "SR5" for f in d1["findings"]))
        check("token red flag finding (>=1 real class)", any("token red flag" in f["text"] for f in d1["findings"]))
        check("markdown rendered", f"SELF-REVIEW-202609" in r1 and "SR5" in r1)
    print(f"selftest: {ok}/{total} PASS")
    return 0 if ok == total else 2


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "selftest":
        return cmd_selftest()
    if argv and argv[0] == "run":
        month = None
        if "--month" in argv:
            i = argv.index("--month")
            month = argv[i + 1] if i + 1 < len(argv) else None
        month = month or _prev_month()
        return cmd_run(month)
    print("usage: self_review.py run [--month YYYYMM] | selftest", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
