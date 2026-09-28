"""Periodic self-review aggregator (CEO order O-20260924-1110; ticket T-2026-09-24-12; charter=firm/SELF_REVIEW.md v1.0).

L1 deterministic aggregator, monthly_briefing.py pattern: zero network / zero
engine / zero token. SR1-SR5 checklist frozen v1.0 in the charter BEFORE first
run (science_audit precedent); SR6 (v1.1, O-20260928-1712 sec.3 wiring)
consumes the INCIDENT-20260928 sec.3 five 30-day zero-recurrence acceptance
clauses via POINTER -- criteria stay frozen in the incident canon, zero
re-legislation here. Findings are REPORT-ONLY and never block; P0
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
    "判据=firm/SELF_REVIEW.md v1.1 冻结清单（SR1-SR5+SR6 事故验收面）；发现只报不阻断；"
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
    except UnicodeDecodeError:
        # PS-redirect writers emit UTF-16 (fffe BOM family, live-fire
        # r401: results/_r239_*.json crash leg); same tolerance family as
        # the utf-8-sig read above (monthly_briefing precedent).
        try:
            with open(path, encoding="utf-16") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError, UnicodeDecodeError):
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
    three = _read_json(base / "results" / "strategy_scorecard.json") or {}
    return {
        "traders_n": len(traders),
        "traders_ids": [p.stem for p in traders],
        "engine_ledger": engine,
        "factor_ledger": factor,
        "paper": paper[:8],
        "portfolio_ew6_sharpe": (ew6.get("portfolios") or ew6).get("sharpe_full") if isinstance((ew6.get("portfolios") or ew6), dict) else None,
        "portfolio_iv6_sharpe": (iv6.get("portfolios_iv") or iv6.get("portfolios") or iv6).get("sharpe_full") if isinstance((iv6.get("portfolios_iv") or iv6.get("portfolios") or iv6), dict) else None,
        "scorecard_best": sc.get("best") or (sc.get("summary") or {}).get("best"),
        "three_card_calibrated": bool((three.get("audit") or {}).get("calibration_consumed")),
        "three_card_vetoes": len(three.get("discipline_veto_hits") or {}),
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
    # D-20260928-03(1) slice-3 (r383): lane-merged audit read (sec.7);
    # sr5 keeps its own tmp-dir fixture path via results_dir (hermetic).
    from merge_lane_views import face_view
    ca = face_view("compute_audit", results_dir=str(base / "results")) or {}
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


# ---------------------------------------------------------------- SR6 incident

# O-20260928-1712 sec.3 item-3 (CEO direct-order wiring, T-75 lane): the
# INCIDENT-20260928 sec.3 five 30-day zero-recurrence acceptance clauses join
# the monthly package as SR6. Criteria are FROZEN IN THE INCIDENT CANON
# (pointer consumption here, zero re-legislation); window anchor = the order
# issuance window 2026-09-28 17:00 (O-1710/1712 same-window).
INCIDENT_FILE = "research/INCIDENT-20260928-cpu-idleness.md"
SR6_ANCHOR = datetime(2026, 9, 28, 17, 0, 0)
SR6_MANUAL_MARKERS = ("亲复", "enable+run", "手动复活", "manual resurrect")


def _git_subjects(base, since_dt):
    """Commit subjects ('%cI|%s') since a datetime; [] on any fault."""
    try:
        out = subprocess.run(
            ["git", "-C", str(base), "log", "--since",
             since_dt.strftime("%Y-%m-%d %H:%M:%S"), "--pretty=format:%cI|%s"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=30, check=True)
        return out.stdout.splitlines()
    except Exception:
        return []


def _incident_clauses(base):
    """Parse sec.3 numbered acceptance clauses from the incident canon."""
    try:
        text = open(base / INCIDENT_FILE, encoding="utf-8").read()
    except OSError:
        return None
    clauses, in_sec = [], False
    for line in text.splitlines():
        if line.startswith("## 三"):
            in_sec = True
            continue
        if in_sec and line.startswith("## "):
            break
        m = re.match(r"^([1-9])\.\s+(.+)$", line.strip()) if in_sec else None
        if m:
            clauses.append({"n": int(m.group(1)), "text": m.group(2).strip()})
    return clauses


def _manual_resurrection_events(subject_lines):
    """Pure clause-1 matcher: commit subjects carrying manual task-family
    resurrection markers (zero-manual-intervention surveillance)."""
    evts = []
    for line in subject_lines:
        try:
            ts_s, subj = line.split("|", 1)
        except ValueError:
            continue
        if any(mk.lower() in subj.lower() for mk in SR6_MANUAL_MARKERS):
            evts.append({"ts": ts_s[:19], "subject": subj.strip()[:120]})
    return evts


def _gate_refusal_scan(lines):
    """Pure clause-4 splitter: anchor-face family (same-type as the incident
    G-VOL misconfig) vs dependency-gate family (honest context, not a
    clause-4 violation)."""
    anchor_family, dep_family = [], []
    for line in lines:
        if "面错配" in line:
            anchor_family.append(line[:160])
        elif "G-VOL" in line and ("FAILED" in line or "refuse" in line.lower() or "拒" in line):
            anchor_family.append(line[:160])
        elif "JUDGE-GATE" in line:
            dep_family.append(line[:160])
    return anchor_family, dep_family


def sr6_incident_acceptance(base, now=None):
    """30-day zero-recurrence surveillance for INCIDENT-20260928 sec.3.

    L1 deterministic faces (report-only): (1) git subjects post-anchor for
    manual task-family resurrection; (2) compute_audit ignition_sla_breach_ids
    post-anchor; (3) supply-gap CLEAN misses post-anchor (v2.4 never-CLEAN);
    (4) gate-refusal lines -- main autofill log (ts-gated) + per-entry runner
    logs (mtime-gated; runner stdout carries no timestamps); (5) working-day
    py>=70 longest/current streak vs the 3-day acceptance line.
    """
    now = now or datetime.now()
    window_ends = SR6_ANCHOR + timedelta(days=30)
    res = {"source": INCIDENT_FILE + " sec.3 (criteria frozen there, pointer)",
           "anchor": SR6_ANCHOR.strftime("%Y-%m-%d %H:%M"),
           "window_ends": window_ends.strftime("%Y-%m-%d"),
           "clauses_n": 0, "faces": {}, "clause_status": []}
    clauses = _incident_clauses(base)
    if not clauses:
        res["clause_status"].append(
            {"clause": 0, "state": "SOURCE-MISSING",
             "note": "incident canon absent/unparseable -- cannot surveil (honest miss)"})
        return res
    res["clauses_n"] = len(clauses)

    # clause 1 -- manual task-family resurrection since anchor
    manual = _manual_resurrection_events(_git_subjects(base, SR6_ANCHOR))
    res["faces"]["manual_resurrection_events"] = manual
    res["clause_status"].append(
        {"clause": 1, "state": "PASS" if not manual else "VIOLATION",
         "note": f"manual task-family resurrection events post-anchor: {len(manual)}"})

    # clauses 2/3/5 -- compute_audit history since anchor (lane-merged face)
    from merge_lane_views import face_view
    ca = face_view("compute_audit", results_dir=str(base / "results")) or {}
    post = []
    for h in ca.get("history") or []:
        t = _parse_ts(h.get("ts"))
        if t is not None and t >= SR6_ANCHOR:
            post.append(h)
    sla = [{"ts": h.get("ts"), "ids": h.get("ignition_sla_breach_ids")}
           for h in post if h.get("ignition_sla_breach_ids")]
    res["faces"]["ignition_sla_breaches"] = sla
    res["clause_status"].append(
        {"clause": 2, "state": "PASS" if not sla else "VIOLATION",
         "note": f"ignition SLA breaches (ready claim) post-anchor: {len(sla)}"})
    gap_clean = [{"ts": h.get("ts"), "verdict": h.get("verdict")} for h in post
                 if str(h.get("verdict")).upper() == "CLEAN" and h.get("supply_gap_candidate")]
    res["faces"]["supply_gap_clean_misses"] = gap_clean
    res["clause_status"].append(
        {"clause": 3, "state": "PASS" if not gap_clean else "VIOLATION",
         "note": f"supply-gap CLEAN misses post-anchor: {len(gap_clean)} (v2.4 never-CLEAN)"})

    # clause 4 -- gate-refusal lines post-anchor
    lines = []
    logs_dir = base / "logs"
    try:
        for line in open(logs_dir / "autofill.log", encoding="utf-8",
                         errors="replace").read().splitlines():
            m = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s", line)
            if m:
                t = _parse_ts(m.group(1))
                if t is not None and t >= SR6_ANCHOR:
                    lines.append(line)
    except OSError:
        pass
    if logs_dir.exists():
        for p in sorted(logs_dir.glob("autofill_*.log")):
            try:
                if p.stat().st_mtime < SR6_ANCHOR.timestamp():
                    continue
                lines.extend(p.read_text(encoding="utf-8", errors="replace").splitlines())
            except OSError:
                continue
    anchor_fam, dep_fam = _gate_refusal_scan(lines)
    res["faces"]["same_type_gate_refusals"] = anchor_fam[:8]
    res["faces"]["dependency_gate_refusals_n"] = len(dep_fam)
    res["clause_status"].append(
        {"clause": 4, "state": "PASS" if not anchor_fam else "VIOLATION",
         "note": (f"anchor-face same-type rejections post-anchor: {len(anchor_fam)}; "
                  f"dependency-gate refusals (context, not violations): {len(dep_fam)}")})

    # clause 5 -- working-day py>=70 streak (O-1614 3-day acceptance line)
    day_max = {}
    for h in post:
        t = _parse_ts(h.get("ts"))
        py = h.get("py_cpu_pct")
        if t is None or t.weekday() >= 5 or not isinstance(py, (int, float)):
            continue
        day_max[t.date()] = max(day_max.get(t.date(), 0.0), float(py))
    longest = cur = 0
    for d in sorted(day_max):
        cur = cur + 1 if day_max[d] >= 70.0 else 0
        longest = max(longest, cur)
    cur = 0
    for d in sorted(day_max, reverse=True):
        if day_max[d] >= 70.0:
            cur += 1
        else:
            break
    res["faces"]["workingday_py70"] = {
        "days_measured": len(day_max), "longest_streak_days": longest,
        "current_streak_days": cur,
        "daily_max_py": {d.isoformat(): round(day_max[d], 1) for d in sorted(day_max)[-10:]}}
    if longest >= 3:
        c5, c5_note = "PASS", f"py>=70 working-day streak reached {longest} days (need 3)"
    elif now > window_ends:
        c5, c5_note = "VIOLATION", f"window ended with longest py>=70 streak {longest}/3"
    else:
        c5 = "PENDING"
        c5_note = (f"in-window (ends {res['window_ends']}); longest py>=70 "
                   f"working-day streak {longest}/3 so far")
    res["clause_status"].append({"clause": 5, "state": c5, "note": c5_note})
    return res


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
    sr6 = sr6_incident_acceptance(base, now)

    findings = list(sr4.get("findings") or [])
    for d in sr3["narrative_drift"]:
        findings.append({"check": "SR3", "severity": "P1", "text": f"law-vs-reality drift: {d}"})
    for st in sr6.get("clause_status", []):
        if st.get("state") == "VIOLATION":
            sev = "P0" if st.get("clause") == 1 else "P1"
            findings.append({"check": "SR6", "severity": sev,
                             "text": (f"INCIDENT-20260928 sec.3 clause {st['clause']} "
                                      f"zero-recurrence VIOLATION: {st['note']}")})
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
            "sr5": sr5, "sr6": sr6, "findings": findings}
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
    L.append(f"- 三卡面（T-63）：{'校准后总分分级已启用（SCORECARD_CALIB_P1 冻结带）' if s2.get('three_card_calibrated') else '校准前读数卡（总分分级未启用）'}；纪律否决 {s2.get('three_card_vetoes')}")
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
    s6 = d["sr6"]
    L.append(f"## SR6 事故防复现验收面（INCIDENT-20260928 §三·O-1712 接线·窗至 {s6['window_ends']}）")
    L.append(f"- 条款来源：{s6['source']}（{s6['clauses_n']} 条指针消费·判据不在本册复制）")
    for st in s6.get("clause_status", []):
        L.append(f"- 条款 {st['clause']}：{st['state']} —— {st['note']}")
    f6 = s6.get("faces", {})
    mr = f6.get("manual_resurrection_events") or []
    if mr:
        L.append(f"- 人工复活事件明细（前 3）：{json.dumps(mr[:3], ensure_ascii=False)}")
    sg = f6.get("same_type_gate_refusals") or []
    if sg:
        L.append(f"- 同型门拒明细（前 3）：{json.dumps(sg[:3], ensure_ascii=False)}")
    w70 = f6.get("workingday_py70") or {}
    if w70:
        L.append(f"- py≥70 工作日线（日最大·近 {len(w70.get('daily_max_py') or {})} 日）：{json.dumps(w70.get('daily_max_py'), ensure_ascii=False)}")
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
             "sr6_violations": sum(1 for st in data["sr6"].get("clause_status", [])
                                   if st.get("state") == "VIOLATION"),
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
        # 6b SR6 incident acceptance (O-20260928-1712 wiring)
        (td / "research").mkdir(parents=True, exist_ok=True)
        _atomic_write(td / "research" / "INCIDENT-20260928-cpu-idleness.md",
                      "# INCIDENT\n\n## 一、时间线\n\n## 三、防复现验收（30 天零复现条款·入月度自审包盯梢）\n\n"
                      "1. 任务族死亡：Watchdog 自愈响应≤15 分钟，30 天内人工介入复活任务=0 例为过；\n"
                      "2. 点火 SLA：ready 批认领≤10 分钟（D2 后≤60 秒），30 天超时=0 例为过；\n"
                      "3. supply-gap CLEAN 漏报：30 天=0 例（v2.4 已杜绝·抽验）；\n"
                      "4. 锚面错配烧批死亡：新预注册 100% 带面定义四元组，30 天同型拦截=0 例为过；\n"
                      "5. 工作时段三机 py≥70% 连续 3 日=满载机制成立验收（O-1614 线）。\n\n## 四、结语\n")
        cl6 = _incident_clauses(td)
        check("SR6 clause parsing (5 numbered)", cl6 and len(cl6) == 5 and cl6[0]["n"] == 1
              and "Watchdog" in cl6[0]["text"])
        ev6 = _manual_resurrection_events([
            "2026-09-28T18:00:00+08:00|round X: task Disabled, GM 亲复 enable+run",
            "2026-09-28T18:05:00+08:00|round Y: routine digest (no marker)"])
        check("SR6 manual-resurrection matcher (pure)",
              len(ev6) == 1 and "亲复" in ev6[0]["subject"])
        af6, df6 = _gate_refusal_scan([
            "GENERATE-GATE: G-VOL probe anchors FAILED on the core48 face -- refuse (prereg sec.2 fail-closed)",
            "JUDGE-GATE: judge_state.json absent -- judge-prep + screen-finalize required first",
            "2026-09-28 18:00:00 INFO: unrelated tick line"])
        check("SR6 gate-refusal splitter (anchor vs dep family)",
              len(af6) == 1 and "G-VOL" in af6[0] and len(df6) == 1)
        res6 = td / "results"
        _atomic_write(res6 / "compute_audit.json", json.dumps({
            "latest": {"cpu_total_pct": 10.0, "flags": []},
            "history": [
                {"ts": "2026-09-28 16:00:00", "verdict": "CLEAN", "supply_gap_candidate": True,
                 "ignition_sla_breach_ids": [], "py_cpu_pct": 10.0},
                {"ts": "2026-09-28 18:00:00", "verdict": "CLEAN", "supply_gap_candidate": True,
                 "ignition_sla_breach_ids": ["X-1"], "py_cpu_pct": 72.0},
                {"ts": "2026-09-29 18:10:00", "verdict": "FLAG:x", "supply_gap_candidate": True,
                 "ignition_sla_breach_ids": [], "py_cpu_pct": 80.0},
                {"ts": "2026-09-30 18:20:00", "verdict": "FLAG:y", "supply_gap_candidate": False,
                 "ignition_sla_breach_ids": [], "py_cpu_pct": 30.0}]}))
        (td / "logs").mkdir(exist_ok=True)
        _atomic_write(td / "logs" / "autofill.log",
                      "2026-09-28 16:59:00 JUDGE-GATE: pre-anchor line (excluded)\n"
                      "2026-09-28 18:01:00 JUDGE-GATE: judge_state.json absent -- context\n")
        pe6 = td / "logs" / "autofill_E1.log"
        _atomic_write(pe6, "GENERATE-GATE: G-VOL probe anchors FAILED on the core48 face -- refuse\n")
        import os as _os
        _os.utime(pe6, (1790590000.0, 1790590000.0))  # ~2026-09-28 18:06 local, post-anchor
        s6 = sr6_incident_acceptance(td, now=datetime(2026, 9, 30, 21, 0, 0))
        st6 = {x["clause"]: x["state"] for x in s6["clause_status"]}
        check("SR6 c1 PASS (no manual events in tmp tree)",
              st6.get(1) == "PASS" and s6["faces"]["manual_resurrection_events"] == [])
        check("SR6 c2 VIOLATION (post-anchor SLA breach)",
              st6.get(2) == "VIOLATION" and s6["faces"]["ignition_sla_breaches"][0]["ids"] == ["X-1"])
        check("SR6 c3 VIOLATION (pre-anchor CLEAN excluded, post-anchor caught)",
              st6.get(3) == "VIOLATION" and len(s6["faces"]["supply_gap_clean_misses"]) == 1)
        check("SR6 c4 VIOLATION (per-entry mtime gate catches G-VOL, main-log ts gate dep family)",
              st6.get(4) == "VIOLATION" and len(s6["faces"]["same_type_gate_refusals"]) == 1
              and s6["faces"]["dependency_gate_refusals_n"] == 1)
        w70 = s6["faces"]["workingday_py70"]
        check("SR6 c5 PENDING (longest 2/3, current 0 broken by latest day)",
              st6.get(5) == "PENDING" and w70["longest_streak_days"] == 2
              and w70["current_streak_days"] == 0 and w70["days_measured"] == 3)
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
        check("markdown rendered", f"SELF-REVIEW-202609" in r1 and "SR5" in r1 and "SR6" in r1)
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
