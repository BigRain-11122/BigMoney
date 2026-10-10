#!/usr/bin/env python
# queue_head_collision_probe.py -- P2 tech queue T18: advisory cross-machine queue-head
# collision probe (S3 self-drive guard). Live-fire law: E3 dual-consume r823 bm-b / r947 bm-a;
# E4 dual-consume r825 bm-b / r948 bm-a; E6 pre-empted r826 bm-b via bm-a declared intent
# (three events inside 24h, 2026-10-10). Read-only advisory: fetch -> read origin blobs
# (other machines' heartbeat intent fields + origin queue faces) -> verdict per queue file.
# Consumers: AI sessions before claiming a P2/P3 head (wired in Tools/iteration_prompt.txt S3).
# Exit codes: 0 = probe ok (verdict is advisory data); 2 = mechanism failure.
# Any machine may run; zero writes outside results/ evidence file. ASCII source law (r823).
import datetime
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE_WINDOW_MIN = 120     # in-flight weight: heartbeat this fresh + current_task match
INTENT_STALE_MIN = 240    # declared-intent weight: next-field declarations up to this age
QUEUE_FILES = ["state/queue/tech.md", "state/queue/explore.md"]
INTENT_FIELDS = ["current_task", "task", "next", "now_active"]


def _sh(args, timeout=60):
    try:
        r = subprocess.run(args, capture_output=True, timeout=timeout, cwd=ROOT)
        return r.returncode, r.stdout
    except subprocess.TimeoutExpired:
        return 124, b""


def _origin_show(path):
    rc, b = _sh(["git", "show", "origin/main:" + path], timeout=45)
    if rc != 0 or not b:
        return None
    return b.decode("utf-8", "replace")


def _machine_id():
    p = os.path.join(ROOT, "fleet", "machine.json")
    try:
        return json.load(io.open(p, encoding="utf-8"))["machine_id"]
    except Exception:
        return None


ROW_RE = re.compile(r"^\|\s*([A-Za-z][A-Za-z0-9]*\d+)\s*\|")


def parse_heads(text):
    # queue md table -> ordered rows; head = first row not done/closed. Pure function.
    rows = []
    for ln in (text or "").splitlines():
        ln = ln.rstrip("\r")
        m = ROW_RE.match(ln)
        if not m:
            continue
        rid = m.group(1)
        low = ln.lower()
        if re.search(r"\|\s*(done|closed)\s*\|", low):
            st = "done" if "done" in low else "closed"
        elif "| open" in low:
            st = "open"
        else:
            st = "unknown"
        rows.append((rid, st))
    live = [(r, s) for r, s in rows if s not in ("done", "closed")]
    return {"rows": rows, "head": live[0][0] if live else None,
            "open_rows": [r for r, s in live if s == "open"]}


def match_head(head_id, text):
    # word-boundary on alnum both sides: E6 matches "E6 head"/"(E6)" but not E60/E6x;
    # T18 does not match "T-180" forms.
    if not head_id or not text:
        return False
    return re.search(r"(?<![A-Za-z0-9])" + re.escape(head_id) + r"(?![A-Za-z0-9])", text) is not None


def _age_min(ts, now=None):
    try:
        t = datetime.datetime.fromisoformat(str(ts))
        ref = now if now is not None else datetime.datetime.now(datetime.timezone.utc).astimezone()
        if t.tzinfo is None and ref.tzinfo is not None:
            t = t.replace(tzinfo=ref.tzinfo)
        elif ref.tzinfo is None and t.tzinfo is not None:
            ref = ref.replace(tzinfo=t.tzinfo)
        return max(0.0, (ref - t).total_seconds() / 60.0)
    except Exception:
        return None


def classify_machine(mid, hb, head_ids, now=None):
    # classify one other machine's heartbeat against the head ids. Pure function.
    out = {"machine": mid, "last_seen": hb.get("last_seen"), "matches": []}
    age = _age_min(hb.get("last_seen"), now)
    out["age_min"] = round(age, 1) if age is not None else None
    blob = " ".join(str(hb.get(f) or "") for f in INTENT_FIELDS)
    for hid in head_ids:
        if not hid:
            continue
        where = None
        if match_head(hid, " ".join(str(hb.get(f) or "") for f in ("current_task", "task"))):
            where = "in_flight"
        elif match_head(hid, " ".join(str(hb.get(f) or "") for f in ("next", "now_active"))):
            where = "declared_intent"
        if not where:
            continue
        if age is None:
            where = "unknown_freshness"
        elif where == "in_flight" and age > LIVE_WINDOW_MIN:
            where = "stale_in_flight"
        elif where == "declared_intent" and age > INTENT_STALE_MIN:
            where = "stale_declaration"
        out["matches"].append({"head": hid, "type": where})
    return out


def aggregate(flags):
    if any(f["type"] == "in_flight" for f in flags):
        return "COLLISION_RISK"
    if any(f["type"] == "declared_intent" for f in flags):
        return "DECLARED_INTENT_RISK"
    if any(f.get("type") == "stale_local" for f in flags):
        return "STALE_LOCAL_QUEUE"
    return "CLEAR"


def probe():
    me = _machine_id()
    fetch_rc, _ = _sh(["git", "fetch", "origin"], timeout=90)
    rc, tipb = _sh(["git", "log", "-1", "--format=%h %ci", "origin/main"], timeout=30)
    report = {"probe": "queue_head_collision_probe", "machine_id": me,
              "fetch_rc": fetch_rc, "origin_main": tipb.decode("utf-8", "replace").strip(),
              "queues": [], "advisory": "verdict is data; COLLISION_RISK/DECLARED_INTENT_RISK "
              "-> yield that head, take next row or another agenda; STALE_LOCAL_QUEUE -> pull "
              "before claiming (local queue face behind origin)"}
    ok = True
    try:
        mdir = os.path.join(ROOT, "fleet", "machines")
        others = sorted(f[:-5] for f in os.listdir(mdir)
                        if f.endswith(".json") and (not me or f[:-5] != me))
    except Exception:
        others, ok = [], False
    for qf in QUEUE_FILES:
        local_txt = None
        p = os.path.join(ROOT, *qf.split("/"))
        if os.path.exists(p):
            local_txt = io.open(p, encoding="utf-8", errors="replace").read()
        local = parse_heads(local_txt)
        origin_txt = _origin_show(qf)
        origin = parse_heads(origin_txt) if origin_txt is not None else None
        entry = {"queue": qf, "local_head": local["head"],
                 "origin_head": origin["head"] if origin else None,
                 "origin_readable": origin is not None, "flags": [], "machine_faces": []}
        if origin is not None and local["head"] and origin["head"] and local["head"] != origin["head"]:
            entry["flags"].append({"type": "stale_local", "detail": "local head %s vs origin head %s"
                                   % (local["head"], origin["head"])})
        for mid in others:
            hb_txt = _origin_show("fleet/machines/%s.json" % mid)
            if not hb_txt:
                continue
            try:
                hb = json.loads(hb_txt)
            except Exception:
                entry["machine_faces"].append({"machine": mid, "error": "heartbeat unparseable"})
                continue
            cm = classify_machine(mid, hb, [local["head"]])
            if cm["matches"]:
                entry["machine_faces"].append(cm)
                for m in cm["matches"]:
                    entry["flags"].append({"type": m["type"], "machine": mid, "head": m["head"]})
        entry["verdict"] = aggregate(entry["flags"])
        report["queues"].append(entry)
    report["verdict"] = aggregate([f for e in report["queues"] for f in e["flags"]])
    outp = os.path.join(ROOT, "results", "queue_head_collision_probe.json")
    with io.open(outp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, ensure_ascii=True, indent=1, sort_keys=True)
    print(json.dumps({"verdict": report["verdict"],
                      "queues": [{"queue": e["queue"], "local_head": e["local_head"],
                                  "origin_head": e["origin_head"], "verdict": e["verdict"]}
                                 for e in report["queues"]]}, ensure_ascii=True))
    if not ok:
        print("WARN: fleet/machines listing failed")
        return 2
    return 0


def selftest():
    # hermetic pure-function legs; double-run byte-identical stdout; zero network zero git.
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    t = parse_heads("| # | x | s |\n|---|---|---|\n| E6 | micro-cap | open |\n| E7 | grid | open |\n")
    leg("head first open row", t["head"] == "E6" and t["open_rows"] == ["E6", "E7"])
    t2 = parse_heads("| E4 | omo | done |\n| E6 | micro | open |\n")
    leg("done rows skipped", t2["head"] == "E6")
    t3 = parse_heads("| E5 | lhb | closed |\n| E6 | micro | open |\n")
    leg("closed rows skipped", t3["head"] == "E6")
    leg("empty table no head", parse_heads("| # | x |\n|---|---|\n")["head"] is None)
    leg("E6 matches intent", match_head("E6", "r949: E6 P3 head (micro-cap scan) 48h cadence"))
    leg("E60 not matched", not match_head("E6", "E60 panel ready"))
    leg("E6x not matched", not match_head("E6", "E6x variant"))
    leg("T18 not in T-180", not match_head("T18", "T-180 wiring done"))
    leg("T18 matched", match_head("T18", "claim T18 same round"))
    leg("AE6 not matched", not match_head("E6", "AE6 face"))
    now = datetime.datetime(2026, 10, 10, 9, 30, 0)
    hb_fresh = {"last_seen": "2026-10-10T09:09:10+08:00",
                "current_task": "E6 survey in flight", "next": ""}
    c1 = classify_machine("bm-a", hb_fresh, ["E6"], now)
    leg("fresh in_flight", c1["matches"] == [{"head": "E6", "type": "in_flight"}])
    hb_next = {"last_seen": "2026-10-10T09:09:10+08:00", "current_task": "W205 seat chain",
               "next": "r949: E6 P3 head next"}
    c2 = classify_machine("bm-a", hb_next, ["E6"], now)
    leg("declared_intent", c2["matches"][0]["type"] == "declared_intent")
    hb_stale = {"last_seen": "2026-10-10T04:00:00+08:00", "current_task": "E6 survey",
                "next": ""}
    c3 = classify_machine("bm-c", hb_stale, ["E6"], now)
    leg("stale in_flight downgraded", c3["matches"][0]["type"] == "stale_in_flight")
    leg("no match clean", classify_machine("bm-c", hb_fresh, ["E12"], now)["matches"] == [])
    leg("collision top severity", aggregate([{"type": "declared_intent"}, {"type": "in_flight"}]) == "COLLISION_RISK")
    leg("intent severity", aggregate([{"type": "declared_intent"}]) == "DECLARED_INTENT_RISK")
    leg("stale local severity", aggregate([{"type": "stale_local"}]) == "STALE_LOCAL_QUEUE")
    leg("clear", aggregate([]) == "CLEAR")
    print("selftest: %d/%d legs PASS" % (sum(1 for _, ok in legs if ok), len(legs)))
    for n, okk in legs:
        if not okk:
            print("  FAIL:", n)
    return 0 if all(ok for _, ok in legs) else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "probe"
    if cmd == "selftest":
        sys.exit(selftest())
    if cmd == "probe":
        sys.exit(probe())
    print("usage: queue_head_collision_probe.py [probe|selftest]")
    sys.exit(2)
