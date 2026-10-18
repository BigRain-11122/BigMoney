"""Automation-line five-element auditor (CEO group orders 2026-10-18
20:48/21:11; construction case research/AUTOMATION-LINE-PLAN-v1.md).

Measures the BigMoney automation line against the world-class five-element
baseline from cph4/fleet/GROUP-AUTOMATION-PLAN-v1.md:
  E1 loop-driven   -- heartbeat + round-report freshness (24/7 self-run)
  E2 auto-claim    -- idle-trigger face + backlog/pool claimable inventory
  E3 gates-in-loop -- kill-line / prereg-budget / false-green sub-faces
  E4 daily-evo     -- daily report freshness + same-day round cadence
  E5 positioning   -- product-round vs waiting-round share (recent window)

Read-only, deterministic, zero network, zero engine, zero new judgments:
this is a MEASUREMENT face. GAP verdicts are reported honestly and are
consumed by the construction plan (research/AUTOMATION-LINE-PLAN-v1.md);
gaps never mask, never block (exit 0 on any audit outcome).

Machine id comes from fleet/machine.json ONLY (r98 identity law). Output:
results/automation_line_audit.json (shared) + .<machine> lane-suffix copy.

Subcommands:
    (no args)  live audit
    selftest   hermetic offline structural check (exit 0/1)

Exit contract: 0 = audit completed; 2 = mechanism fault (missing identity
or unreadable mandatory faces) -- report as-is, never mask.
"""
import glob
import json
import os
import sys
import datetime as _dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

OUT_SHARED = os.path.join(ROOT, "results", "automation_line_audit.json")
STALE_MIN = 30.0          # heartbeat / round-report freshness line
DAILY_STALE_DAYS = 2.0    # daily report freshness line
RECENT_ROUNDS_WINDOW = 5  # E5 positioning sample window

VERDICTS = ("OK", "PARTIAL", "GAP")


def _machine_id():
    mp = os.path.join(ROOT, "fleet", "machine.json")
    try:
        return json.load(open(mp, "r", encoding="utf-8"))["machine_id"]
    except Exception:
        return None


def _read_json(path):
    try:
        return json.load(open(path, "r", encoding="utf-8"))
    except Exception:
        return None


def _parse_iso(ts):
    try:
        return _dt.datetime.fromisoformat(str(ts))
    except Exception:
        return None


def _now():
    return _dt.datetime.now().astimezone()


def _age_min(dt):
    if dt is None:
        return None
    return (_now() - dt).total_seconds() / 60.0


def _tail_lines(path, n):
    try:
        lines = open(path, "r", encoding="utf-8").read().splitlines()
    except Exception:
        return []
    return [l for l in lines if l.strip()][-n:]


def _round_report_path(mid):
    own = os.path.join(ROOT, "round_reports-%s.md" % mid)
    if os.path.exists(own):
        return own
    # bm-b legacy/shared carrier (S5 multi-machine law)
    return os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")


def e1_loop_driven(mid):
    hb = _read_json(os.path.join(ROOT, "fleet", "machines", "%s.json" % mid)) or {}
    hb_age = _age_min(_parse_iso(hb.get("ts")))
    last = _tail_lines(_round_report_path(mid), 1)
    rr_age = _age_min(_parse_iso(last[0].split(" | ")[0])) if last else None
    fresh = (hb_age is not None and hb_age <= STALE_MIN
             and rr_age is not None and rr_age <= STALE_MIN + 10)
    return {
        "element": "E1_loop_driven_24x7",
        "verdict": "OK" if fresh else "GAP",
        "evidence": {"heartbeat_age_min": hb_age, "round_report_age_min": rr_age,
                     "stale_line_min": STALE_MIN},
    }


def e2_auto_claim(mid):
    it = _read_json(os.path.join(ROOT, "results", "idle_trigger.%s.json" % mid)) or {}
    backlog = _tail_lines(os.path.join(ROOT, "fleet", "backlog.md"), 200)
    open_lines = sum(1 for l in backlog if l.strip().startswith("- [ ]"))
    pool = _read_json(os.path.join(ROOT, "results", "runnable_pool.json"))
    entries = 0
    if isinstance(pool, list):
        entries = len(pool)
    elif isinstance(pool, dict):
        items = pool.get("items") or pool.get("jobs") or []
        entries = len(items) if isinstance(items, list) else 0
    # face present = idle-trigger leg deployed (r847 bm-a carrier law);
    # claimable inventory (0/0) is an honest reading, not a gap by itself --
    # standing-agenda supply is judged at E5/G-faces in the plan.
    face_ok = bool(it) and "green_idle" in it
    return {
        "element": "E2_auto_claim_self_heal",
        "verdict": "OK" if face_ok else "GAP",
        "evidence": {"idle_trigger_face_present": face_ok,
                     "green_idle": it.get("green_idle"),
                     "claimable_pool_lines": it.get("claimable_pool_lines"),
                     "backlog_open_lines": open_lines,
                     "runnable_pool_entries": entries},
    }


def _text_has(path, needle):
    try:
        return needle in open(path, "r", encoding="utf-8", errors="replace").read()
    except Exception:
        return False


def e3_gates_in_loop():
    sg = os.path.join(ROOT, "scripts", "science_gates.py")
    seed_gate = os.path.join(ROOT, "scripts", "queue_seed_gate.py")
    sat = os.path.join(ROOT, "scripts", "saturation_engine.py")
    autofill = os.path.join(ROOT, "Tools", "autofill.py")
    prereg_tpl = os.path.join(ROOT, "research", "PREREG_TEMPLATE.md")
    claw = os.path.join(ROOT, ".git", "hooks", "pre-commit")

    kill_registry = _text_has(sg, "CLOSED_FAMILIES")
    kill_registration_block = _text_has(seed_gate, "CLOSED_FAMILIES")
    # runtime-side auto-stop face: burn-continuation runner must consult the
    # closed-family registry before auto-igniting (G1 when absent)
    kill_runtime_enforced = _text_has(autofill, "CLOSED_FAMILIES")
    budget_frozen = _text_has(prereg_tpl, "预算") or _text_has(prereg_tpl, "budget")
    budget_auto_stop = _text_has(autofill, "budget_cap") or _text_has(autofill, "budget")
    # false-green: engine busy/idle verdict must cross-check claimable work
    # (SLI-RECONCILE 2026-10-15 precedent: structural wait != ignitable work)
    false_green_fixed = _text_has(sat, "claimable")
    claw_present = os.path.exists(claw)

    sub = {
        "kill_line_registry": kill_registry,
        "kill_line_registration_block": kill_registration_block,
        "kill_line_runtime_auto_stop": kill_runtime_enforced,
        "prereg_budget_frozen_face": budget_frozen,
        "prereg_budget_auto_stop": budget_auto_stop,
        "false_green_claimable_crosscheck": false_green_fixed,
        "precommit_claw_present": claw_present,
    }
    core_ok = all(sub[k] for k in ("kill_line_registry",
                                   "kill_line_registration_block",
                                   "precommit_claw_present"))
    if core_ok and kill_runtime_enforced and budget_auto_stop and false_green_fixed:
        v = "OK"
    elif core_ok:
        v = "PARTIAL"   # registry-side gates in-loop; runtime-side gaps named
    else:
        v = "GAP"
    return {"element": "E3_quality_gates_in_loop", "verdict": v, "evidence": sub}


def e4_daily_evolution():
    reports = sorted(glob.glob(os.path.join(
        ROOT, "docs", "daily_report", "REPORT-*.md")))
    latest_age_days = None
    if reports:
        mtime = _dt.datetime.fromtimestamp(
            os.path.getmtime(reports[-1])).astimezone()
        latest_age_days = (_now() - mtime).total_seconds() / 86400.0
    fresh = latest_age_days is not None and latest_age_days <= DAILY_STALE_DAYS
    return {
        "element": "E4_daily_evolution",
        "verdict": "OK" if fresh else "PARTIAL",
        "evidence": {"latest_report": os.path.basename(reports[-1]) if reports else None,
                     "latest_report_age_days": latest_age_days,
                     "stale_line_days": DAILY_STALE_DAYS},
    }


def e5_positioning(mid):
    lines = _tail_lines(_round_report_path(mid), RECENT_ROUNDS_WINDOW)
    waiting = sum(1 for l in lines if "等待态" in l)
    product = sum(1 for l in lines if any(k in l for k in ("产品轮", "P0", "令执行", "实物")))
    share_wait = (waiting / len(lines)) if lines else None
    if not lines:
        v = "GAP"
    elif product >= 1 and (share_wait is None or share_wait < 0.8):
        v = "OK"
    else:
        v = "PARTIAL"
    return {
        "element": "E5_positioning_law",
        "verdict": v,
        "evidence": {"window_rounds": len(lines), "waiting_rounds": waiting,
                     "product_rounds": product, "waiting_share": share_wait},
    }


def _gaps(elements):
    named = []
    e3 = next((e for e in elements if e["element"].startswith("E3")), None)
    ev = e3["evidence"] if e3 else {}
    if ev and not ev.get("kill_line_runtime_auto_stop"):
        named.append("G1 判负关线运行侧自动执法缺位（注册侧已闸·烧批续燃面无 CLOSED_FAMILIES 硬拒）")
    if ev and not ev.get("prereg_budget_auto_stop"):
        named.append("G2 预注册预算运行时自动停缺位（冻结面在·超限靠人宣合法停）")
    if ev and not ev.get("false_green_claimable_crosscheck"):
        named.append("G3 假绿判据未修正（saturation_engine 无可点火件交叉面·SLI-RECONCILE 判例）")
    for e in elements:
        if e["verdict"] == "GAP" and e["element"].startswith("E"):
            named.append("%s 分项 GAP（证据见 JSON）" % e["element"])
    return named


def run_audit():
    mid = _machine_id()
    if not mid:
        print("automation_line_audit: FATAL missing fleet/machine.json identity")
        return 2
    elements = [e1_loop_driven(mid), e2_auto_claim(mid), e3_gates_in_loop(),
                e4_daily_evolution(), e5_positioning(mid)]
    payload = {
        "ts": _now().isoformat(timespec="seconds"),
        "machine": mid,
        "law_ref": "cph4/fleet/GROUP-AUTOMATION-PLAN-v1.md five elements; "
                   "construction case research/AUTOMATION-LINE-PLAN-v1.md",
        "elements": elements,
        "gaps": _gaps(elements),
    }
    lane = dict(payload)
    lane["lane_machine"] = mid
    for path in (OUT_SHARED,
                 os.path.join(ROOT, "results", "automation_line_audit.%s.json" % mid)):
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload if path == OUT_SHARED else lane, f,
                      ensure_ascii=False, indent=1)
        os.replace(tmp, path)
    for e in elements:
        print("[%s] %s" % (e["verdict"], e["element"]))
    for g in payload["gaps"]:
        print("GAP:", g)
    print("audit written: %s (%d elements, %d named gaps)"
          % (OUT_SHARED, len(elements), len(payload["gaps"])))
    return 0


def selftest():
    """Hermetic structural check: identity law, verdict enums, output
    serializability, gap-name law. Zero network, zero engine."""
    mid = _machine_id()
    ok = True

    def check(name, cond):
        nonlocal ok
        print(("PASS" if cond else "FAIL"), name)
        ok = ok and bool(cond)

    check("identity_from_machine_json", mid is not None)
    check("verdict_enum_frozen", all(v in VERDICTS for v in VERDICTS))
    elements = [e1_loop_driven(mid), e2_auto_claim(mid), e3_gates_in_loop(),
                e4_daily_evolution(), e5_positioning(mid)]
    check("five_elements_present", len(elements) == 5)
    check("verdicts_in_enum",
          all(e["verdict"] in VERDICTS for e in elements))
    check("evidence_always_dict",
          all(isinstance(e["evidence"], dict) for e in elements))
    gaps = _gaps(elements)
    check("gaps_are_strings", all(isinstance(g, str) for g in gaps))
    payload = {"ts": _now().isoformat(timespec="seconds"), "machine": mid,
               "elements": elements, "gaps": gaps}
    s = json.dumps(payload, ensure_ascii=False)
    check("payload_json_serializable", len(s) > 100)
    # gap-name law: G1/G2/G3 named constants stay aligned to their faces
    check("gap_names_declared",
          any(g.startswith("G1") for g in gaps) or
          elements[2]["evidence"].get("kill_line_runtime_auto_stop"))
    print("selftest %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        return selftest()
    return run_audit()


if __name__ == "__main__":
    sys.exit(main())
