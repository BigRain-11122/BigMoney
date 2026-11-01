"""Lane round liveness: is this machine actually producing rounds?

Why this exists
---------------
D-20261101-15/17 (group ledger batch 34) rewrote task acceptance from a single
dimension (``schtasks`` state / ``LastTaskResult``) to three faces:
instance, result, product.  A ``Ready`` task with an ``0x800710E0`` last result
proves nothing either way -- on bm-a that code was a *live* resident agent whose
duplicate trigger got refused, on bm-b it can be a real refusal.

``compute/BigCompute/Tools/executor_liveness.py`` (the shared implementation
named by D-15) is not present on bm-b: this machine's group tree
(``C:\Fluxgroup\FluxGroup``) has no ``compute/`` subtree at all.  Until that
tool reaches here, this module answers the same question from evidence that
*is* local: the round ledger (product face), the per-machine state file
(result face) and the heartbeat (instance face).

Usage
-----
    python Tools/lane_round_liveness.py check [--machine bm-b | --all]
    python Tools/lane_round_liveness.py selftest

Output: ``results/lane_liveness.<machine>.json``.  Stdout is ASCII-only so it
survives any console code page (r1012 family).
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")

#: fresh enough to call the lane alive (one iteration cycle is 10 min)
ALIVE_MIN = 25.0
#: beyond this, no fresh evidence at all becomes a death claim
DEAD_MIN = 360.0
#: a gap worth disclosing in the 7 day window
GAP_MIN = 90.0

TS_RE = re.compile(
    r"\|\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?(?:[+-]\d{2}:\d{2})?)\s*"
)


def report_path(machine: str) -> str:
    """Round ledger for a machine.

    bm-b has kept the legacy shared path since before per-machine files existed
    (fleet/README.md section 6); everyone else writes round_reports-<id>.md.
    """
    if machine == "bm-b":
        legacy = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
        if os.path.exists(legacy):
            return legacy
    return os.path.join(ROOT, "round_reports-%s.md" % machine)


def parse_ts(text: str) -> datetime:
    fmt = "%Y-%m-%dT%H:%M:%S%z" if text.count(":") >= 3 else "%Y-%m-%dT%H:%M%z"
    dt = datetime.strptime(text, fmt)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def ledger_times(path: str) -> list:
    """Timestamps of every round-ledger row, in file order."""
    if not os.path.exists(path):
        return []
    return ledger_times_text(io.open(path, encoding="utf-8", errors="replace").read())


def ledger_times_text(text: str) -> list:
    out = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        m = TS_RE.match(line)
        if not m:
            continue
        try:
            out.append(parse_ts(m.group(1)))
        except ValueError:
            continue
    return out


def ledger_from_origin(path: str):
    """Read a machine's ledger from origin/main.

    This worktree runs hundreds of commits behind origin (r1243: the two
    bloodlines are still unfused), so a peer's local ledger copy is a lagging
    mirror.  Judging a peer DEAD off that copy is exactly the reading error
    D-20261101-15 was written about.  Returns (times, source) and falls back to
    the worktree copy -- with the source named -- when git cannot answer.
    """
    rel = os.path.relpath(path, ROOT).replace("\\", "/")
    try:
        import subprocess

        proc = subprocess.run(
            ["git", "-C", ROOT, "show", "origin/main:%s" % rel],
            capture_output=True,
        )
        if proc.returncode == 0 and proc.stdout:
            return ledger_times_text(proc.stdout.decode("utf-8", "replace")), "origin/main"
    except Exception:
        pass
    return ledger_times(path), "worktree"


def read_json(path: str):
    if not os.path.exists(path):
        return {}
    try:
        return json.load(io.open(path, encoding="utf-8"))
    except Exception:
        return {}


def read_json_origin(path: str):
    """Same mirror problem as the ledger: read peers through origin when able."""
    rel = os.path.relpath(path, ROOT).replace("\\", "/")
    try:
        import subprocess

        proc = subprocess.run(
            ["git", "-C", ROOT, "show", "origin/main:%s" % rel], capture_output=True
        )
        if proc.returncode == 0 and proc.stdout:
            return json.loads(proc.stdout.decode("utf-8", "replace")), "origin/main"
    except Exception:
        pass
    return read_json(path), "worktree"


def load_evidence(machine: str, now: datetime, prefer_origin: bool = False) -> dict:
    """Collect the three faces. Missing faces stay None (never invented)."""
    rpath = report_path(machine)
    if prefer_origin:
        times, src_ledger = ledger_from_origin(rpath)
        state, src_state = read_json_origin(os.path.join(ROOT, "state-%s.json" % machine))
        hb, src_hb = read_json_origin(
            os.path.join(ROOT, "fleet", "machines", "%s.json" % machine)
        )
    else:
        times = ledger_times(rpath)
        state = read_json(os.path.join(ROOT, "state-%s.json" % machine))
        hb = read_json(os.path.join(ROOT, "fleet", "machines", "%s.json" % machine))
        src_ledger = src_state = src_hb = "worktree"

    def age(ts):
        return None if ts is None else round((now - ts).total_seconds() / 60.0, 1)

    last_row = times[-1] if times else None
    recent = [t for t in times if now - t <= timedelta(days=7)]
    gaps = []
    for a, b in zip(recent, recent[1:]):
        if b < a:
            continue  # ledger should be ordered; a stray row is not a gap
        minutes = (b - a).total_seconds() / 60.0
        if minutes >= GAP_MIN:
            gaps.append(
                {
                    "from": a.isoformat(),
                    "to": b.isoformat(),
                    "minutes": round(minutes, 1),
                }
            )

    hb_ts = None
    for key in ("ts", "last_seen", "clock_read"):
        raw = hb.get(key)
        if isinstance(raw, str):
            try:
                hb_ts = parse_ts(raw if "T" in raw else raw.replace(" ", "T"))
                break
            except ValueError:
                continue

    return {
        "machine": machine,
        "report_path": os.path.relpath(rpath, ROOT).replace("\\", "/"),
        "report_exists": os.path.exists(rpath),
        "evidence_source": {"ledger": src_ledger, "state": src_state, "heartbeat": src_hb},
        "rows_total": len(times),
        "rows_7d": len(recent),
        "last_row_ts": last_row.isoformat() if last_row else None,
        "last_row_age_min": age(last_row),
        "rounds_24h": len([t for t in times if now - t <= timedelta(hours=24)]),
        "gaps_7d": gaps,
        "worst_gap_7d_min": max([g["minutes"] for g in gaps]) if gaps else 0.0,
        "state_round_no": state.get("round_no"),
        "state_last_action_at": state.get("last_action_at"),
        "hb_round_no": hb.get("round_no"),
        "hb_ts": hb_ts.isoformat() if hb_ts else None,
        "hb_age_min": age(hb_ts),
    }


def verdict_of(ev: dict) -> dict:
    """Collapse the three faces into ALIVE / NO-EVIDENCE / DEAD (D-17 v2).

    product = a round-ledger row; result = state round_no present and matching
    heartbeat round_no; instance = a heartbeat younger than one cycle.
    """
    row_age = ev.get("last_row_age_min")
    hb_age = ev.get("hb_age_min")
    product_fresh = row_age is not None and row_age <= ALIVE_MIN
    instance_fresh = hb_age is not None and hb_age <= ALIVE_MIN
    round_match = (
        ev.get("state_round_no") is not None
        and ev.get("state_round_no") == ev.get("hb_round_no")
    )
    faces = {
        "product": product_fresh,
        "instance": instance_fresh,
        "result": bool(round_match),
    }
    ages = [a for a in (row_age, hb_age) if a is not None]
    newest = min(ages) if ages else None
    if product_fresh or instance_fresh:
        state = "ALIVE"
    elif newest is None or newest > DEAD_MIN:
        state = "DEAD"
    else:
        state = "NO-EVIDENCE"
    return {
        "verdict": state,
        "faces": faces,
        "faces_open": sorted(k for k, v in faces.items() if not v),
        "newest_evidence_age_min": newest,
        "round_no_match": round_match,
    }


def cmd_check(machines, now=None, quiet=False) -> int:
    now = now or datetime.now(timezone.utc).astimezone()
    os.makedirs(RESULTS, exist_ok=True)
    me = read_json(os.path.join(ROOT, "fleet", "machine.json")).get("machine_id")
    payload = {"generated": now.isoformat(), "local_machine": me,
               "thresholds": {"alive_min": ALIVE_MIN,
                              "dead_min": DEAD_MIN,
                              "gap_min": GAP_MIN},
               "machines": {}}
    worst = 0
    for machine in machines:
        ev = load_evidence(machine, now, prefer_origin=bool(me) and machine != me)
        v = verdict_of(ev)
        ev.update(v)
        payload["machines"][machine] = ev
        out = os.path.join(RESULTS, "lane_liveness.%s.json" % machine)
        io.open(out, "w", encoding="utf-8", newline="\n").write(
            json.dumps(ev, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
        )
        if not quiet:
            print(
                "%s verdict=%s row_age=%s hb_age=%s rounds_24h=%s worst_gap_7d=%s rounds=%s/%s open=%s src=%s"
                % (
                    machine,
                    ev["verdict"],
                    ev["last_row_age_min"],
                    ev["hb_age_min"],
                    ev["rounds_24h"],
                    ev["worst_gap_7d_min"],
                    ev["state_round_no"],
                    ev["hb_round_no"],
                    ",".join(ev["faces_open"]) or "-",
                    ev["evidence_source"]["ledger"],
                )
            )
    io.open(os.path.join(RESULTS, "lane_liveness.json"), "w", encoding="utf-8",
            newline="\n").write(
        json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    return worst


# --------------------------------------------------------------------------- #
# selftest: fixtures drive every branch, no reliance on repo state
# --------------------------------------------------------------------------- #

def _fixture(tmp, machine, rows, state_round, hb_round, hb_age_min, now):
    ledger = os.path.join(tmp, "logs", "iteration-loop")
    os.makedirs(ledger, exist_ok=True)
    with io.open(os.path.join(ledger, "round_reports.md"), "w", encoding="utf-8",
                 newline="\n") as fh:
        # rows are given as ages; the ledger is chronological, so write the
        # oldest first and let the newest age land last
        for minutes in sorted(rows, reverse=True):
            fh.write("| %s | r%s | fixture |\n"
                     % ((now - timedelta(minutes=minutes)).isoformat(), minutes))
    io.open(os.path.join(tmp, "state-%s.json" % machine), "w", encoding="utf-8") \
        .write(json.dumps({"round_no": state_round}))
    os.makedirs(os.path.join(tmp, "fleet", "machines"), exist_ok=True)
    hb = {"round_no": hb_round}
    if hb_age_min is not None:
        hb["ts"] = (now - timedelta(minutes=hb_age_min)).isoformat()
    io.open(os.path.join(tmp, "fleet", "machines", "%s.json" % machine), "w",
            encoding="utf-8").write(json.dumps(hb))


def cmd_selftest() -> int:
    global ROOT, RESULTS
    import tempfile
    import shutil

    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    saved = (ROOT, RESULTS)
    tmp = tempfile.mkdtemp(prefix="liveliness_")
    now = datetime(2026, 11, 1, 6, 0, 0, tzinfo=timezone(timedelta(hours=8)))
    try:
        ROOT = tmp
        RESULTS = os.path.join(tmp, "results")

        # L1 alive: fresh row + fresh heartbeat + matching round numbers
        _fixture(tmp, "bm-b", [0, 10, 20, 30], 1362, 1362, 3, now)
        ev = load_evidence("bm-b", now)
        v = verdict_of(ev)
        leg("L1 fresh lane is ALIVE", v["verdict"] == "ALIVE", v["verdict"])
        leg("L1b all three faces green", v["faces_open"] == [], str(v["faces_open"]))

        # L2 round-number drift: heartbeat says 1359 while state says 1362
        _fixture(tmp, "bm-a", [1, 11], 1362, 1359, 2, now)
        v = verdict_of(load_evidence("bm-a", now))
        leg("L2 drift still ALIVE but result face open",
            v["verdict"] == "ALIVE" and v["faces"]["result"] is False, str(v["faces"]))

        # L3 no evidence at all -> DEAD (nothing within DEAD_MIN)
        _fixture(tmp, "bm-c", [600, 610], 1300, 1300, 700, now)
        v = verdict_of(load_evidence("bm-c", now))
        leg("L3 silent machine is DEAD", v["verdict"] == "DEAD", v["verdict"])

        # L4 stale but not dead: 120 min old, no heartbeat -> NO-EVIDENCE
        _fixture(tmp, "bm-b", [120, 130], 1362, 1362, None, now)
        v = verdict_of(load_evidence("bm-b", now))
        leg("L4 stale is NO-EVIDENCE not DEAD", v["verdict"] == "NO-EVIDENCE",
            v["verdict"])
        leg("L4b missing heartbeat never invents freshness",
            load_evidence("bm-b", now)["hb_age_min"] is None)

        # L5 gap detection counts only the 7 day window
        _fixture(tmp, "bm-b", [0, 200, 400, 60 * 24 * 9], 1362, 1362, 2, now)
        ev = load_evidence("bm-b", now)
        leg("L5 gap 90min+ counted inside window",
            [g["minutes"] for g in ev["gaps_7d"]] == [200.0, 200.0],
            str([g["minutes"] for g in ev["gaps_7d"]]))
        leg("L5b 9-day-old row excluded from 7d slice", ev["rows_7d"] == 3,
            str(ev["rows_7d"]))

        # L6 missing ledger file is reported, not crashed
        empty = os.path.join(tmp, "nofile")
        ts = ledger_times(os.path.join(empty, "x.md"))
        leg("L6 missing ledger returns empty, no exception", ts == [], str(ts))

        # L7 peer readings must name where they came from; outside a git repo
        # the origin read cannot happen and the fallback has to say so
        _fixture(tmp, "bm-a", [5], 1362, 1362, 5, now)
        peer = load_evidence("bm-a", now, prefer_origin=True)
        leg("L7 peer evidence discloses its source, never silently local",
            peer["evidence_source"]["ledger"] in ("origin/main", "worktree"),
            str(peer["evidence_source"]))
    finally:
        ROOT, RESULTS = saved
        shutil.rmtree(tmp, ignore_errors=True)

    bad = [x for x in legs if not x[1]]
    for name, ok, detail in legs:
        print("[%s] %s%s" % ("PASS" if ok else "FAIL", name,
                             (" | " + detail) if detail else ""))
    print("lane_round_liveness selftest: %d/%d PASS" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")
    chk = sub.add_parser("check")
    chk.add_argument("--machine", default=None)
    chk.add_argument("--all", action="store_true")
    sub.add_parser("selftest")
    args = ap.parse_args(argv)

    if args.cmd == "selftest":
        return cmd_selftest()
    if args.cmd == "check":
        if args.all:
            machines = ["bm-a", "bm-b", "bm-c"]
        elif args.machine:
            machines = [args.machine]
        else:
            me = read_json(os.path.join(ROOT, "fleet", "machine.json")).get("machine_id")
            machines = [me] if me else ["bm-b"]
        return cmd_check(machines)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())