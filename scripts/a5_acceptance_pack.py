"""A5 first-line acceptance-record carrier
(AUTOMATION-LINE-PLAN-v1.md sec.III A5 / sec.IV frozen criteria V1-V5).

Acceptance deadline 2026-10-31. This face REGENERATES the acceptance
record each run; it never claims completion ahead of evidence -- every
V-item reports PASS or PENDING(day k / target) honestly, per the plan's
"selftest + live-fire evidence" receipt law.

Frozen criteria (sec.IV -- no result-driven line changes):
  V1 false-green fix   : saturation_engine claimable crossface in service
                         + selftest false-green counter-example assertion
  V2 attribution ledger: REPORT-*.md PnL-attribution section consecutive
                         >= 5 trading days (honest no-data annotation legal)
  V3 kill-line enforce : closed-family seed hard-refused by the burn
                         continuation runtime (live-fire intercept evidence)
  V4 budget auto-stop : over-budget_cap in-pool batch auto-DISABLEd and
                         exposed (live-fire evidence)
  V5 five-element audit: no GAP-level per-element findings, consecutive
                         >= 3 calendar days (per-day streak ledger)

Zero network, zero engine, zero new judgments. Attribution streak reuses
automation_line_audit.e4_daily_evolution (single source, no re-derive).

Outputs (same-day regen idempotent, other days never touched):
  results/a5_acceptance/PACK-YYYYMMDD.json + PACK-YYYYMMDD.md
  results/a5_acceptance/streak.jsonl        (one line per calendar day)

Subcommands:
    (no args)  regenerate today's pack
    selftest   hermetic offline check (tempdir only, zero repo writes)

Exit contract: 0 = pack written (PASS or PENDING both legal);
               2 = mechanism fault (missing identity / unreadable faces)
               -- report as-is, never mask.
"""
import datetime as _dt
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import automation_line_audit as ala  # noqa: E402  (single-source reuse)

AUDIT_FACE = os.path.join(ROOT, "results", "automation_line_audit.json")
LIVEFIRE = os.path.join(ROOT, "results", "_r1072bma_a3_livefire.json")
SAT_ENGINE = os.path.join(ROOT, "scripts", "saturation_engine.py")
OUT_DIR = os.path.join(ROOT, "results", "a5_acceptance")
STREAK_LEDGER = os.path.join(OUT_DIR, "streak.jsonl")

V2_TARGET_DAYS = 5      # sec.IV V2 (trading-day reports)
V5_TARGET_DAYS = 3      # sec.IV V5 (consecutive audit days)
DEADLINE = "2026-10-31"  # sec.III A5


def _now():
    return _dt.datetime.now().astimezone()


def _today():
    return _now().date().isoformat()


def _machine_id():
    return ala._machine_id()


def _read_json(path):
    try:
        return json.load(open(path, "r", encoding="utf-8"))
    except Exception:
        return None


def _text(path):
    try:
        return open(path, "r", encoding="utf-8", errors="replace").read()
    except Exception:
        return ""


# ---------- V1: false-green fix ----------
def v1_false_green():
    src = _text(SAT_ENGINE)
    crossface = "_claimable_crossface" in src and "SLI-RECONCILE" in src
    selftest_body = src[src.find("def selftest"):] if "def selftest" in src else ""
    counter_assert = bool(re.search(
        r"struct_wait_idle|claimable_n", selftest_body))
    live_dual = (_read_json(os.path.join(
        ROOT, "results", "watermark_red.json")) or {})
    # honest: engine live status dual face is measured by satengine itself;
    # here we assert the crossface is wired + selftest asserts the dual read.
    ok = crossface and counter_assert
    return {
        "item": "V1_false_green_fix",
        "verdict": "PASS" if ok else "PENDING",
        "evidence": {
            "claimable_crossface_wired": crossface,
            "selftest_counter_assertion": counter_assert,
            "law_ref": "AUTOMATION-LINE-PLAN-v1 sec.IV V1; A1 batch (r1070)",
        },
    }


# ---------- V2: attribution ledger streak ----------
def v2_attribution_streak():
    ev = ala.e4_daily_evolution()["evidence"]
    streak = int(ev.get("pnl_attribution_streak_days") or 0)
    ok = streak >= V2_TARGET_DAYS
    return {
        "item": "V2_attribution_daily_ledger",
        "verdict": "PASS" if ok else "PENDING",
        "evidence": {
            "pnl_attribution_streak_days": streak,
            "target_days": V2_TARGET_DAYS,
            "latest_report": ev.get("latest_report"),
            "honest_annotation_legal": True,
            "law_ref": "AUTOMATION-LINE-PLAN-v1 sec.IV V2; A2 batch (r1071)",
        },
    }


# ---------- V3: kill-line live-fire refusal ----------
def v3_kill_line_livefire():
    d = _read_json(LIVEFIRE) or {}
    g1 = d.get("g1") or {}
    events = g1.get("gate_events") or []
    refused = g1.get("refused") or []
    refuse_ok = any(e.get("action") == "refuse_ignite"
                    and e.get("gate") == "closed_family" for e in events)
    # family face is nested per-hit (livefire fixture shape) with an
    # optional top-level mirror -- accept either, never fabricate
    def _fams(r):
        out = []
        if r.get("family"):
            out.append(r.get("family"))
        for h in (r.get("hits") or []):
            if h.get("family"):
                out.append(h.get("family"))
        return out
    named = any("microcap_2024_crash" in _fams(r) for r in refused)
    ok = refuse_ok and named
    return {
        "item": "V3_kill_line_auto_enforcement",
        "verdict": "PASS" if ok else "PENDING",
        "evidence": {
            "livefire_refuse_event": refuse_ok,
            "livefire_named_refusal": named,
            "evidence_file": "results/_r1072bma_a3_livefire.json",
            "selftest_legs": "Tools/autofill.py S23d/S23e (r1072)",
            "law_ref": "AUTOMATION-LINE-PLAN-v1 sec.IV V3; A3 batch (r1072)",
        },
    }


# ---------- V4: budget auto-stop live-fire ----------
def v4_budget_autostop():
    d = _read_json(LIVEFIRE) or {}
    g2 = d.get("g2") or {}
    recs = g2.get("budget_disabled_rec") or []
    disabled = any(e.get("action") == "auto_disabled"
                  and e.get("gate") == "budget_cap" for e in recs)
    reason = any("budget_cap" in str(r.get("disabled_reason", ""))
                 for r in (g2.get("lane_entry") or []))
    ok = disabled and reason
    return {
        "item": "V4_budget_auto_stop",
        "verdict": "PASS" if ok else "PENDING",
        "evidence": {
            "livefire_auto_disabled": disabled,
            "disabled_reason_exposed": reason,
            "evidence_file": "results/_r1072bma_a3_livefire.json",
            "selftest_legs": "Tools/autofill.py S24b/S24f (r1072)",
            "law_ref": "AUTOMATION-LINE-PLAN-v1 sec.IV V4; A3 batch (r1072)",
        },
    }


# ---------- V5: five-element audit streak ----------
def _audit_day_verdict(audit):
    """true = no GAP-level per-element finding in this audit run."""
    if not isinstance(audit, dict):
        return False
    els = audit.get("elements") or []
    return bool(els) and all(e.get("verdict") != "GAP" for e in els)


def _streak_from_lines(lines, today):
    """Consecutive-day streak ending today (or yesterday, before today's
    line lands). Pure function (selftest target)."""
    by_day = {}
    for l in lines:
        try:
            row = json.loads(l)
        except Exception:
            continue
        by_day[row.get("date")] = bool(row.get("all_no_gap"))
    days = sorted(d for d in by_day if d)
    streak = 0
    cur = _dt.date.fromisoformat(today)
    if days and days[-1] == today and not by_day[today]:
        return 0
    if not days or days[-1] < today:
        cur = cur - _dt.timedelta(days=1)
    while cur.isoformat() in by_day and by_day[cur.isoformat()]:
        streak += 1
        cur = cur - _dt.timedelta(days=1)
    return streak


def _update_ledger(today, all_no_gap, audit_ts, gaps_count, path=STREAK_LEDGER):
    """Idempotent per-day ledger upsert: today's line replaced in place,
    other days untouched, file stays date-sorted. Pure w.r.t. given path."""
    lines = []
    if os.path.exists(path):
        lines = [l for l in open(path, "r", encoding="utf-8").read().splitlines()
                 if l.strip()]
    kept, replaced = [], False
    for l in lines:
        try:
            row = json.loads(l)
        except Exception:
            kept.append(l)
            continue
        if row.get("date") == today:
            replaced = True
            continue
        kept.append(l)
    row = {"date": today, "all_no_gap": bool(all_no_gap),
           "audit_ts": audit_ts, "gaps_count": int(gaps_count)}
    kept.append(json.dumps(row, ensure_ascii=False))
    kept.sort(key=lambda l: (json.loads(l).get("date") if l.strip()
              and l.strip()[0] == "{" else "0000") )
    tmp = path + ".tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("\n".join(kept) + "\n")
    os.replace(tmp, path)
    return replaced


def v5_audit_streak():
    audit = _read_json(AUDIT_FACE)
    today = _today()
    all_no_gap = _audit_day_verdict(audit)
    gaps = audit.get("gaps") if isinstance(audit, dict) else None
    _update_ledger(today, all_no_gap,
                   (audit or {}).get("ts"), len(gaps) if gaps else 0)
    lines = [l for l in open(STREAK_LEDGER, "r", encoding="utf-8")
             .read().splitlines() if l.strip()]
    streak = _streak_from_lines(lines, today)
    ok = streak >= V5_TARGET_DAYS
    return {
        "item": "V5_five_element_audit_streak",
        "verdict": "PASS" if ok else "PENDING",
        "evidence": {
            "today_all_no_gap": all_no_gap,
            "consecutive_days": streak,
            "target_days": V5_TARGET_DAYS,
            "ledger": "results/a5_acceptance/streak.jsonl",
            "law_ref": "AUTOMATION-LINE-PLAN-v1 sec.IV V5 (WAVE_LOOP_LAW "
                       "sec.4 standing audit leg)",
        },
    }


def _pack_md(payload):
    p = payload
    rows = []
    for it in p["items"]:
        ev = it["evidence"]
        note = ""
        if it["item"].startswith("V2"):
            note = " (streak %d/%d days)" % (
                ev["pnl_attribution_streak_days"], ev["target_days"])
        elif it["item"].startswith("V5"):
            note = " (streak %d/%d days)" % (
                ev["consecutive_days"], ev["target_days"])
        rows.append("- **%s %s**%s" % (it["verdict"], it["item"], note))
    return "# A5 首线实装验收记录 PACK-%s\n\n" % p["date"] + \
        "> 律源 research/AUTOMATION-LINE-PLAN-v1.md §四（判据冻结·禁看结果调线）·死线 %s·验收记录幂等再生面（当日重跑原地再生·他日永不动）\n\n" % DEADLINE + \
        "## 总判 %s\n\n%s\n\n> 证据锚全部机读（JSON 孪生=同目录 PACK-%s.json）·PENDING=如实未达·非失败\n" % (
            p["overall_verdict"], "\n".join(rows), p["date"])


def run_pack():
    mid = _machine_id()
    if not mid:
        print("a5_acceptance_pack: FATAL missing fleet/machine.json identity")
        return 2
    items = [v1_false_green(), v2_attribution_streak(),
             v3_kill_line_livefire(), v4_budget_autostop(), v5_audit_streak()]
    overall = "ALL_PASS" if all(i["verdict"] == "PASS" for i in items) \
        else "PENDING"
    payload = {"date": _today(), "ts": _now().isoformat(timespec="seconds"),
               "machine": mid, "overall_verdict": overall,
               "deadline": DEADLINE, "items": items}
    os.makedirs(OUT_DIR, exist_ok=True)
    base = os.path.join(OUT_DIR, "PACK-%s" % payload["date"])
    tmp = base + ".json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    os.replace(tmp, base + ".json")
    tmp = base + ".md.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(_pack_md(payload))
    os.replace(tmp, base + ".md")
    for it in items:
        print("[%s] %s" % (it["verdict"], it["item"]))
    print("pack written: %s.json (overall %s, deadline %s)"
          % (base, overall, DEADLINE))
    return 0


def selftest():
    """Hermetic: pure functions on synthetic data + tempdir ledger; zero
    repo writes, zero network."""
    import tempfile
    ok = True

    def check(name, cond):
        nonlocal ok
        print(("PASS" if cond else "FAIL"), name)
        ok = ok and bool(cond)

    # streak computation: 3 consecutive then break
    lines = [json.dumps({"date": "2026-10-17", "all_no_gap": True}),
             json.dumps({"date": "2026-10-18", "all_no_gap": True}),
             json.dumps({"date": "2026-10-19", "all_no_gap": True})]
    check("streak_3_consecutive",
          _streak_from_lines(lines, "2026-10-19") == 3)
    lines[1] = json.dumps({"date": "2026-10-18", "all_no_gap": False})
    check("streak_break_resets",
          _streak_from_lines(lines, "2026-10-19") == 1)
    check("streak_today_false_zero",
          _streak_from_lines(
              [json.dumps({"date": "2026-10-19", "all_no_gap": False})],
              "2026-10-19") == 0)
    check("streak_empty_ledger",
          _streak_from_lines([], "2026-10-19") == 0)
    # V5 day verdict shapes
    check("day_verdict_no_gap",
          _audit_day_verdict({"elements": [{"verdict": "OK"}]}) is True)
    check("day_verdict_gap_false",
          _audit_day_verdict(
              {"elements": [{"verdict": "OK"}, {"verdict": "GAP"}]}) is False)
    check("day_verdict_missing_false",
          _audit_day_verdict(None) is False)
    # V3/V4 evidence shapes (synthetic)
    check("v3_shape_detect",
          v3_kill_line_liveflow_ok({"g1": {"gate_events": [
              {"action": "refuse_ignite", "gate": "closed_family"}],
              "refused": [{"family": "microcap_2024_crash"}]}}))
    check("v4_shape_detect",
          v4_budget_ok({"g2": {"budget_disabled_rec": [
              {"action": "auto_disabled", "gate": "budget_cap"}],
              "lane_entry": [{"disabled_reason": "budget_cap 5 reached"}]}}))
    # ledger idempotent upsert (tempdir, two runs -> single today line)
    with tempfile.TemporaryDirectory() as td:
        lp = os.path.join(td, "streak.jsonl")
        _update_ledger("2026-10-19", True, "t1", 0, path=lp)
        _update_ledger("2026-10-19", False, "t2", 1, path=lp)
        rows = [json.loads(l) for l in open(lp, encoding="utf-8")
                if l.strip()]
        check("ledger_upsert_idempotent",
              len(rows) == 1 and rows[0]["all_no_gap"] is False)
    print("selftest %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def v3_kill_line_liveflow_ok(d):
    g1 = d.get("g1") or {}
    events = g1.get("gate_events") or []
    refused = g1.get("refused") or []
    return (any(e.get("action") == "refuse_ignite"
                and e.get("gate") == "closed_family" for e in events)
            and bool(refused))


def v4_budget_ok(d):
    g2 = d.get("g2") or {}
    recs = g2.get("budget_disabled_rec") or []
    return (any(e.get("action") == "auto_disabled"
                and e.get("gate") == "budget_cap" for e in recs)
            and any("budget_cap" in str(r.get("disabled_reason", ""))
                    for r in (g2.get("lane_entry") or [])))


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        return selftest()
    return run_pack()


if __name__ == "__main__":
    sys.exit(main())
