#!/usr/bin/env python
# queue_seed_gate.py -- P2 tech queue T19: closed-family machine check gate for
# P2/P3 queue-row seeds (registration-time lint + full-queue scan).
# Live-fire law: E6 stale-seed root cause -- queue rows registered (r804 bm-c
# build face, 2026-10-09) without checking science_gates.CLOSED_FAMILIES; the
# E6 row (microcap closed family) was consumed r949 bm-a as a pure collision
# adjudication (zero scan work). Reopen law = O-20260925-1105 (new evidence =
# new prereg, or the entry's own reopen channel; microcap = CEO one-liner
# only). Registry single-source = science_gates.py CLOSED_FAMILIES
# (research/CLOSED_FAMILIES.md mirrors the human face). Scope = the registry
# keys + their identity word-faces ONLY; queue-internal family closures (e.g.
# r947 sentiment thermo double-negative) stay digest-law, not this gate.
# Design (false-positive control): HARD collision = word-face hit in the WORK
# column of a LIVE row (status open/unknown); pointer-column-only hits are
# NOTES not blocks -- meta rows ABOUT a closure legitimately cite its digest
# (the T19 row itself carries e6-microcap-closed-adjudication.md in pointer).
# DONE/CLOSED rows are historical adjudicated faces and are never re-flagged.
# Commands:
#   scan                  scan both queue files' live rows -> results/queue_seed_gate.json
#   check "<seed text>" [--reopen "<evidence>"]   registration-time single-seed lint
#   selftest              hermetic pure-function legs (double-run byte-identical)
# Exit codes: 0 = clean / lawful reopen declared (notes allowed); 3 =
# CLOSED_FAMILY_COLLISION on a live row or rejected seed; 2 = mechanism fault.
# Any machine may run; zero writes outside the results/ evidence file.
# ASCII source law (r823).
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)  # r817 law: module-top path insert (knowledge ns-pkg)
from science_gates import CLOSED_FAMILIES  # single-source registry (T19 row)

QUEUE_FILES = ["state/queue/tech.md", "state/queue/explore.md"]

# Identity word-faces per registry key, derived from each entry's
# verdict/evidence text. Conservative identity markers only (bare generic
# words like "futures"/"sentiment" are NOT faces -- E8 calendar-spread work is
# a different mechanism from the closed CTA trend family and must pass).
FAMILY_WORD_FACES = {
    "cta_futures_p1": ["cta", "期货趋势", "趋势跟踪"],
    "cn_combo_five_family": ["rev-tilt", "div-lowvol-rot", "regime-policy",
                             "core-satellite", "ddctl"],
    "wild_route_s1": ["wild_route", "wild route"],
    "factor_blend": ["factor_blend", "因子融合", "因子混合"],
    "t28_spm_first": ["spm", "稳定盈利", "t-28"],
    "microcap_2024_crash": ["微盘", "小市值", "microcap", "small-cap", "小盘股"],
    "lowamp_daily_xs": ["低振幅", "lowamp", "low-amp", "low_amplitude"],
    "lowamp_deep_xs": ["低振幅", "lowamp", "low-amp", "low_amplitude"],
    "g2_slot_mon_p2_xs": ["g2_slot_mon", "月度转换"],
}

ROW_RE = re.compile(r"^\|\s*([A-Za-z]+\d+)\s*\|")


def parse_rows(text):
    """Queue md table -> rows {id, work, pointer, status}. Pure function.

    Status detection mirrors the T-18 probe (regex over the whole line) so
    column drift never misclassifies done/closed rows as live.
    """
    rows = []
    for ln in (text or "").splitlines():
        ln = ln.rstrip("\r")
        if not ROW_RE.match(ln):
            continue
        cells = [c.strip() for c in ln.split("|")[1:-1]]
        rid = cells[0]
        work = cells[1] if len(cells) > 2 else ""
        pointer = cells[2] if len(cells) > 3 else ""
        low = ln.lower()
        if re.search(r"\|\s*(done|closed)\s*\|", low):
            st = "done" if re.search(r"\|\s*done\s*\|", low) else "closed"
        elif "| open" in low:
            st = "open"
        else:
            st = "unknown"
        rows.append({"id": rid, "work": work, "pointer": pointer, "status": st})
    return rows


def match_faces(text):
    """Case-insensitive substring face match. Pure function.

    CJK faces match by substring by design (word boundaries are an ASCII
    concept); the E6 live-fire catch was exactly this class (微盘/小市值).
    """
    out = []
    if not text:
        return out
    hay = text.lower()
    for fam, faces in sorted(FAMILY_WORD_FACES.items()):
        for face in faces:
            if face.lower() in hay:
                out.append({"family": fam, "face": face})
    return out


def check_seed(text, reopen=None):
    """Registration-time verdict for one prospective seed text. Pure function.

    Mirrors science_gates.closed_family_check statuses: open / rejected /
    reopen_channel_declared (O-20260925-1105 law).
    """
    hits = match_faces(text)
    if not hits:
        return {"status": "open", "hits": []}
    ev = reopen.strip() if isinstance(reopen, str) else ""
    fams = sorted({h["family"] for h in hits})
    rules = {f: CLOSED_FAMILIES[f]["reopen"] for f in fams}
    if ev:
        return {"status": "reopen_channel_declared", "hits": hits,
                "reopen_evidence": ev, "reopen_rules": rules}
    return {"status": "rejected", "hits": hits, "reopen_rules": rules,
            "reason": "seed work-text hits a CLOSED_FAMILIES word-face; declare "
            "the new-evidence delta vs the archived verdict (O-20260925-1105) "
            "or cite the entry's reopen channel before registering"}


def scan_queue_text(text):
    """One queue file -> {live_rows, findings, notes}. Pure function."""
    findings, notes, live = [], [], 0
    for r in parse_rows(text):
        if r["status"] in ("done", "closed"):
            continue
        live += 1
        work_hits = match_faces(r["work"])
        if work_hits:
            findings.append({"id": r["id"], "column": "work", "hits": work_hits,
                             "reopen_rules": {h["family"]:
                                              CLOSED_FAMILIES[h["family"]]["reopen"]
                                              for h in work_hits}})
            continue
        ptr_hits = match_faces(r["pointer"])
        if ptr_hits:
            notes.append({"id": r["id"], "column": "pointer", "hits": ptr_hits,
                          "note": "pointer-only citation of a closed family "
                          "(meta/adjudication reference) -- not a block"})
    return {"live_rows": live, "findings": findings, "notes": notes}


def _machine_id():
    try:
        with io.open(os.path.join(ROOT, "fleet", "machine.json"),
                     encoding="utf-8") as f:
            return json.load(f)["machine_id"]
    except Exception:
        return None


def scan():
    report = {"probe": "queue_seed_gate", "machine_id": _machine_id(),
              "queues": [], "verdict": "CLEAR",
              "advisory": "verdict is data; CLOSED_FAMILY_COLLISION on a live "
              "row = the owning round must adjudicate the row out (or the row "
              "must declare the family reopen channel per O-20260925-1105) "
              "before any work starts; registration-time law = run 'check' on "
              "the seed text BEFORE adding any new P2/P3 row"}
    missing = []
    for qf in QUEUE_FILES:
        p = os.path.join(ROOT, *qf.split("/"))
        if not os.path.exists(p):
            missing.append(qf)
            continue
        txt = io.open(p, encoding="utf-8", errors="replace").read()
        res = scan_queue_text(txt)
        res["queue"] = qf
        report["queues"].append(res)
    if len(missing) == len(QUEUE_FILES):
        print("ERROR: no queue files readable: %s" % ",".join(missing))
        return 2
    if missing:
        report["queues"].append({"queue": missing[0], "error": "file missing"})
    findings = [f for q in report["queues"] for f in q.get("findings", [])]
    if findings:
        report["verdict"] = "CLOSED_FAMILY_COLLISION"
    report["registry_keys"] = sorted(CLOSED_FAMILIES.keys())
    outp = os.path.join(ROOT, "results", "queue_seed_gate.json")
    with io.open(outp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, ensure_ascii=True, indent=1, sort_keys=True)
    print(json.dumps({"verdict": report["verdict"],
                      "queues": [{"queue": q["queue"], "live_rows": q["live_rows"],
                                  "findings": len(q.get("findings", [])),
                                  "notes": len(q.get("notes", []))}
                                 for q in report["queues"]]}, ensure_ascii=True))
    return 3 if findings else 0


def check_cmd(args):
    if not args:
        print("usage: queue_seed_gate.py check \"<seed text>\" [--reopen \"<evidence>\"]")
        return 2
    text = args[0]
    reopen = None
    if "--reopen" in args[1:]:
        i = args.index("--reopen")
        if i + 1 < len(args):
            reopen = args[i + 1]
    res = check_seed(text, reopen)
    print(json.dumps(res, ensure_ascii=True, sort_keys=True))
    if res["status"] == "rejected":
        return 3
    return 0


def selftest():
    # hermetic pure-function legs; double-run byte-identical stdout; zero
    # network, zero repo-file reads (science_gates import is offline/deterministic).
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    t = parse_rows("| # | 待办 | 指针 | 状态 |\n|---|---|---|---|\n"
                  "| E8 | 商品期货跨期价差监控面 | scripts/update_futures.py | open |\n"
                  "| E6 | 微盘股因子扫描 | digests/e6.md | closed |\n")
    leg("parse id/work/pointer", t[0]["id"] == "E8"
        and "跨期价差" in t[0]["work"] and "update_futures" in t[0]["pointer"])
    leg("parse status open/closed", t[0]["status"] == "open" and t[1]["status"] == "closed")
    t2 = parse_rows("| T5 | x | y | done |\n| T19 | gate row | p | open |\n")
    leg("done row classified", t2[0]["status"] == "done" and t2[1]["status"] == "open")
    leg("empty text no rows", parse_rows("") == [] and parse_rows(None) == [])
    leg("non-table line skipped", parse_rows("plain prose E8 微盘")[0]["id"] if False else
        parse_rows("plain prose") == [])
    # E6 live-fire: the exact stale-seed work text catches microcap
    e6 = scan_queue_text("| E6 | 微盘股量化因子外源扫描（韭研/雪球/研报三源·小市值效应本土化） "
                         "| 外源扫描 | open |\n")
    leg("E6 seed HARD collision", len(e6["findings"]) == 1
        and e6["findings"][0]["hits"][0]["family"] == "microcap_2024_crash")
    leg("E6 reopen rule carried",
        e6["findings"][0]["reopen_rules"]["microcap_2024_crash"] == "ceo_one_line_reopen")
    # closed row never re-flagged (adjudicated historical face)
    e6c = scan_queue_text("| E6 | 微盘股量化因子外源扫描 | digests/e6.md | closed |\n")
    leg("closed row skipped", e6c["live_rows"] == 0 and e6c["findings"] == [])
    # T19 meta row: microcap only in pointer -> note not finding
    t19 = scan_queue_text("| T19 | queue seed closed-family gate row | "
                          "research/digests/DIGEST-20261010-e6-microcap-closed-adjudication.md "
                          "| open |\n")
    leg("meta row pointer-only = note", t19["findings"] == [] and len(t19["notes"]) == 1)
    # clean live row
    cl = scan_queue_text("| E12 | 逆回购月末利率脉冲策略化 | scripts/update_repo.py | open |\n")
    leg("clean row clear", cl["findings"] == [] and cl["notes"] == [] and cl["live_rows"] == 1)
    # case-insensitive + lowamp dual-key family hits
    h = match_faces("MicroCap scan and LOWAMP factor")
    leg("case-insensitive hits", {x["family"] for x in h} ==
        {"microcap_2024_crash", "lowamp_daily_xs", "lowamp_deep_xs"})
    # E8 calendar-spread is NOT the closed CTA trend family (no bare futures face)
    leg("E8 not flagged", match_faces("商品期货跨期价差监控面 近远月价差序列化") == [])
    # check mode: rejected / reopen_channel_declared / open
    r1 = check_seed("小市值因子本土化研究")
    leg("check rejected", r1["status"] == "rejected")
    r2 = check_seed("小市值因子本土化研究", reopen="CEO one-liner reopen received 2026-10-10")
    leg("check reopen declared", r2["status"] == "reopen_channel_declared")
    r3 = check_seed("AH premium mean reversion deepening")
    leg("check open", r3["status"] == "open")
    # single-source consistency: face table keys == registry keys, non-empty lists
    leg("face table covers registry exactly",
        set(FAMILY_WORD_FACES) == set(CLOSED_FAMILIES)
        and all(v for v in FAMILY_WORD_FACES.values()))
    leg("registry 9 keys", len(CLOSED_FAMILIES) == 9)
    print("selftest: %d/%d legs PASS" % (sum(1 for _, ok in legs if ok), len(legs)))
    for n, okk in legs:
        if not okk:
            print("  FAIL:", n)
    return 0 if all(ok for _, ok in legs) else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    if cmd == "selftest":
        sys.exit(selftest())
    if cmd == "scan":
        sys.exit(scan())
    if cmd == "check":
        sys.exit(check_cmd(sys.argv[2:]))
    print("usage: queue_seed_gate.py [scan|check \"<text>\" [--reopen \"<ev>\"]|selftest]")
    sys.exit(2)
