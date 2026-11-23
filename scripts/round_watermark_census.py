#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Which face is allowed to tell you what round this machine is on?

Three faces claim to carry the round counter for one machine, and on 2026-11-23
09:1x they read three different numbers while the git log read a fourth:

  git log                 round 1976   (committed 09:07)
  state-bm-c.json         1962 / 1946 / 1952 inside one file (mtime 06:53)
  fleet/machines/bm-c.json round_no 1960, mtime 09:09, but last_seen 03:00
  fleet/state-bm-c.json   1555, frozen since 11-11 (12 days)

The third one is the dangerous shape: the heartbeat had been *redrawn two
minutes earlier* and still carried an inner clock six hours old. A watchdog that
judges liveness by mtime sees a live machine; one that judges by the face's own
clock sees a dead loop; both are reading the same file. This tool exists because
the r1219 rule ("the two faces disagree -> absorb") never fires when the counter
is the thing that is stale, and `scripts/round_open_absorb.py` classifies dirty
*files*, not the counter.

Read-only on every shared face. Its only write is its own artifact
(results/round_watermark_census.json). Verdicts are decided by counts, and a
face that cannot be read is reported as unreadable, never as "0 rounds".

Usage:
  python scripts/round_watermark_census.py run [--json PATH] [--now ISO]
  python scripts/round_watermark_census.py --check
  python scripts/round_watermark_census.py --selftest
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CST = timezone(timedelta(hours=8))
DEFAULT_OUT = os.path.join(ROOT, "results", "round_watermark_census.json")

ROUND_KEYS = ("round_no", "round", "rounds", "last_round")
CLOCK_KEYS = ("clock_read", "ts", "last_seen", "last_round_ts",
              "heartbeat_epoch_utc", "generated")
# a face whose mtime is this fresh but whose own clock is this much older has
# been redrawn without being advanced (r1861 "face moves" family)
FROZEN_GAP_MIN = 60.0
RECENT_MIN = 180.0


def now_cst():
    return datetime.now(CST)


def parse_iso(value):
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            return datetime.fromtimestamp(float(value), CST)
        except (OverflowError, OSError, ValueError):
            return None
    text = str(value).strip()
    if not text:
        return None
    if re.fullmatch(r"\d{10}", text):
        return parse_iso(int(text))
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        stamp = datetime.fromisoformat(text)
    except ValueError:
        return None
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=CST)
    return stamp.astimezone(CST)


def machine_id(root=ROOT):
    try:
        with open(os.path.join(root, "fleet", "machine.json"), encoding="utf-8") as fh:
            return json.load(fh).get("machine_id")
    except (OSError, ValueError):
        return None


def git_round(root, depth=40):
    """(round, sha, when, subject) of the newest commit whose subject says round N."""
    try:
        proc = subprocess.run(
            ["git", "-C", root, "log", "-%d" % depth, "--format=%H|%cI|%s"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=60,
        )
    except Exception as exc:  # noqa: BLE001 - every failure is reported, not raised
        return {"readable": False, "error": str(exc)}
    if proc.returncode != 0:
        return {"readable": False, "error": (proc.stderr or "").strip()[-300:]}
    for line in proc.stdout.splitlines():
        parts = line.split("|", 2)
        if len(parts) < 3:
            continue
        hit = re.search(r"\bround (\d{2,6})\b", parts[2])
        if hit:
            return {"readable": True, "round": int(hit.group(1)),
                    "sha": parts[0][:10], "at": parts[1],
                    "subject": parts[2][:90]}
    return {"readable": False, "error": 'no "round N" in the last %d subjects' % depth}


def scan_face(root, rel, now):
    """Everything one face says about the round, without trusting any of it."""
    rel = rel.replace("\\", "/")  # one face name on every host
    path = os.path.join(root, rel)
    if not os.path.exists(path):
        return {"path": rel, "exists": False}
    stat = os.stat(path)
    mtime = datetime.fromtimestamp(stat.st_mtime, CST)
    face = {"path": rel, "exists": True, "bytes": stat.st_size,
            "mtime": mtime.isoformat(),
            "mtime_age_min": round((now - mtime).total_seconds() / 60.0, 1)}
    try:
        with open(path, encoding="utf-8") as fh:
            body = json.load(fh)
    except (OSError, ValueError) as exc:
        face["json_error"] = str(exc)
        return face
    rounds = {}
    if isinstance(body, dict):
        for key in ROUND_KEYS:
            val = body.get(key)
            if isinstance(val, int) and not isinstance(val, bool):
                rounds[key] = val
            elif isinstance(val, str) and re.fullmatch(r"\d{2,6}", val.strip()):
                rounds[key] = int(val.strip())
        clocks = {k: str(body.get(k)) for k in CLOCK_KEYS if body.get(k) is not None}
    else:
        clocks = {}
    stamps = [s for s in (parse_iso(v) for v in clocks.values()) if s]
    inner = max(stamps) if stamps else None
    face["rounds"] = rounds
    face["round_values"] = sorted(set(rounds.values()))
    face["clocks"] = clocks
    face["inner_clock"] = inner.isoformat() if inner else None
    face["inner_clock_age_min"] = (round((now - inner).total_seconds() / 60.0, 1)
                                  if inner else None)
    return face


def report_tail_round(root, rel, now, lines=40):
    """Highest r<N> printed in the last lines of a round-report ledger."""
    rel = rel.replace("\\", "/")
    path = os.path.join(root, rel)
    if not os.path.exists(path):
        return {"path": rel, "exists": False}
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            tail = fh.readlines()[-lines:]
    except OSError as exc:
        return {"path": rel, "exists": True, "error": str(exc)}
    found = [int(m) for m in re.findall(r"\br(\d{4})\b", "".join(tail))]
    mtime = datetime.fromtimestamp(os.path.getmtime(path), CST)
    return {"path": rel, "exists": True, "max_round": max(found) if found else None,
            "mtime": mtime.isoformat(),
            "mtime_age_min": round((now - mtime).total_seconds() / 60.0, 1)}


def classify(faces, git, tail, now):
    """Verdict from counts. No face is allowed to decide anything on its own."""
    flags = []
    lags = {}
    for face in faces:
        if not face.get("exists"):
            flags.append("FACE_MISSING:%s" % face["path"])
            continue
        if "json_error" in face:
            flags.append("FACE_UNREADABLE:%s" % face["path"])
            continue
        rounds = face.get("rounds") or {}
        if not rounds:
            flags.append("NO_ROUND_KEY:%s" % face["path"])
            continue
        if len(set(rounds.values())) > 1:
            flags.append("ONE_FILE_HOLDS_%d_ROUNDS:%s" % (
                len(set(rounds.values())), face["path"]))
        own = max(rounds.values())
        if git.get("readable"):
            lags[face["path"]] = git["round"] - own
        inner_age = face.get("inner_clock_age_min")
        mtime_age = face.get("mtime_age_min")
        if (inner_age is not None and mtime_age is not None
                and mtime_age <= RECENT_MIN and inner_age - mtime_age >= FROZEN_GAP_MIN):
            flags.append("REDRAWN_WITH_A_FROZEN_CLOCK:%s(%s min old, mtime %s min)"
                         % (face["path"], inner_age, mtime_age))

    if not git.get("readable"):
        verdict = "GIT_ROUND_UNREADABLE"
    elif not lags:
        verdict = "NO_FACE_CARRIES_A_ROUND"
    elif all(lag == 0 for lag in lags.values()):
        verdict = "ALL_FACES_AGREE_WITH_GIT"
    elif len(set(lags.values())) == 1:
        verdict = "ALL_FACES_LAG_GIT_BY_%d" % list(lags.values())[0]
    else:
        verdict = "FACES_DISAGREE_WITH_GIT_AND_EACH_OTHER"

    if tail and tail.get("max_round") is not None and git.get("readable"):
        if git["round"] - tail["max_round"] > 0:
            flags.append("REPORT_LEDGER_LAGS_GIT_BY_%d" % (git["round"] - tail["max_round"]))

    worst = max(lags.values()) if lags else None
    return {"verdict": verdict, "lags_vs_git": lags, "worst_lag": worst,
            "flags": flags}


def census(root=ROOT, now=None, git=None):
    now = now or now_cst()
    mid = machine_id(root) or "bm-c"
    git = git if git is not None else git_round(root)
    faces = [
        scan_face(root, "state-%s.json" % mid, now),
        scan_face(root, os.path.join("fleet", "machines", "%s.json" % mid), now),
        scan_face(root, os.path.join("fleet", "state-%s.json" % mid), now),
    ]
    tail = report_tail_round(root, os.path.join("fleet", "round_reports-%s.md" % mid), now)
    graded = classify(faces, git, tail, now)
    return {
        "schema": "round-watermark-census/v1",
        "machine_id": mid,
        "probed_at": now.isoformat(timespec="seconds"),
        "git": git,
        "faces": faces,
        "report_ledger": tail,
        **graded,
        "reading": _reading(graded, git, faces),
    }


def _reading(graded, git, faces):
    if graded["verdict"] == "GIT_ROUND_UNREADABLE":
        return "the git round could not be read (%s); no face is graded against it" % (
            git.get("error"))
    if graded["verdict"] == "ALL_FACES_AGREE_WITH_GIT":
        return "every carrier prints round %d, which is what git says" % git["round"]
    parts = []
    for face in faces:
        rounds = face.get("rounds") or {}
        if rounds:
            parts.append("%s says %s (%s min old)" % (
                os.path.basename(face["path"]),
                "/".join(str(v) for v in face["round_values"]),
                face.get("inner_clock_age_min")))
    return "git says round %d; %s -- a stale carrier is not a dead loop, but nothing " \
           "downstream can tell the difference by reading it" % (git["round"], "; ".join(parts))


def _selftest():
    legs = []

    def leg(name, cond, detail=""):
        legs.append((name, bool(cond), detail))

    tmp = tempfile.mkdtemp(prefix="rwc-")
    now = datetime(2026, 11, 23, 9, 10, tzinfo=CST)

    def face(rel, payload, age_min=1.0):
        path = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh)
        stamp = (now - timedelta(minutes=age_min)).timestamp()
        os.utime(path, (stamp, stamp))

    git = {"readable": True, "round": 1976, "sha": "deadbeef", "at": "2026-11-23T09:07",
           "subject": "round 1976: x"}
    # 1 agree
    face("state-bm-c.json", {"round_no": 1976, "last_seen": now.isoformat()})
    face("fleet/machines/bm-c.json", {"round_no": 1976, "last_seen": now.isoformat()})
    face("fleet/state-bm-c.json", {"round_no": 1976, "last_round_ts": now.isoformat()})
    out = census(tmp, now=now, git=git)
    leg("all three carriers on the git round -> agree",
        out["verdict"] == "ALL_FACES_AGREE_WITH_GIT", out["verdict"])

    # 2 uniform lag
    face("state-bm-c.json", {"round_no": 1970, "last_seen": now.isoformat()})
    face("fleet/machines/bm-c.json", {"round_no": 1966, "last_seen": now.isoformat()})
    face("fleet/state-bm-c.json", {"round_no": 1955, "last_round_ts": now.isoformat()})
    out = census(tmp, now=now, git=git)
    leg("three different lags -> disagree, not a single number",
        out["verdict"] == "FACES_DISAGREE_WITH_GIT_AND_EACH_OTHER"
        and out["worst_lag"] == 21, "%s/%s" % (out["verdict"], out["worst_lag"]))

    # 3 one file, three round numbers
    face("state-bm-c.json", {"round_no": 1962, "round": 1946, "rounds": 1952,
                             "last_seen": now.isoformat()})
    out = census(tmp, now=now, git=git)
    leg("one file holding three round numbers is flagged",
        any(f.startswith("ONE_FILE_HOLDS_3_ROUNDS") for f in out["flags"]), out["flags"])

    # 4 redrawn with a frozen clock (the 09:09 heartbeat shape)
    face("fleet/machines/bm-c.json",
         {"round_no": 1960, "last_seen": (now - timedelta(minutes=370)).isoformat(),
          "last_round_ts": "2026-11-20T01:56:49+08:00"}, age_min=2.0)
    out = census(tmp, now=now, git=git)
    leg("mtime 2 min but inner clock 370 min -> redrawn-with-frozen-clock",
        any(f.startswith("REDRAWN_WITH_A_FROZEN_CLOCK:fleet/machines") for f in out["flags"]),
        [f for f in out["flags"] if "REDRAWN" in f])

    # 5 a genuinely old face is not the same thing
    face("fleet/machines/bm-c.json",
         {"round_no": 1960, "last_seen": (now - timedelta(minutes=370)).isoformat()},
         age_min=370.0)
    out = census(tmp, now=now, git=git)
    leg("old mtime + old clock is stale, NOT redrawn-frozen",
        not any(f.startswith("REDRAWN_WITH_A_FROZEN_CLOCK:fleet/machines")
                for f in out["flags"]), out["flags"])

    # 6 missing face is unreadable, never zero
    os.remove(os.path.join(tmp, "fleet/state-bm-c.json"))
    out = census(tmp, now=now, git=git)
    leg("missing face is FACE_MISSING, and still no face reads as round 0",
        any(f.startswith("FACE_MISSING:fleet/state-bm-c.json") for f in out["flags"])
        and all(0 not in (f.get("round_values") or []) for f in out["faces"]),
        out["flags"])

    # 7 unreadable git is graded as such, not as agreement
    out = census(tmp, now=now, git={"readable": False, "error": "boom"})
    leg("git unreadable -> GIT_ROUND_UNREADABLE, zero faces graded",
        out["verdict"] == "GIT_ROUND_UNREADABLE" and out["lags_vs_git"] == {},
        out["verdict"])

    # 8 epoch heartbeat clock is understood, raw string is not a date
    face("fleet/machines/bm-c.json",
         {"round_no": 1974, "heartbeat_epoch_utc": int((now - timedelta(minutes=5)).timestamp()),
          "clock_read": "2026-11-23T09:05:00"}, age_min=5.0)
    out = census(tmp, now=now, git=git)
    hb = [f for f in out["faces"] if f["path"].endswith("machines/bm-c.json")][0]
    leg("epoch clock is parsed as a clock", abs((hb["inner_clock_age_min"] or 999) - 5) < 1.5,
        hb["inner_clock_age_min"])

    # 9 a face that is not JSON is unreadable, not a verdict
    with open(os.path.join(tmp, "state-bm-c.json"), "w", encoding="utf-8") as fh:
        fh.write("{not json")
    out = census(tmp, now=now, git=git)
    leg("broken JSON -> FACE_UNREADABLE",
        any(f.startswith("FACE_UNREADABLE:state-bm-c.json") for f in out["flags"]),
        out["flags"])

    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, detail in legs:
        print("%s %s%s" % ("PASS" if ok else "FAIL", name,
                           "" if ok else "  <- %r" % (detail,)))
    print("%d/%d PASS" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check"])
    ap.add_argument("--json", default=DEFAULT_OUT)
    ap.add_argument("--now", default=None)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    now = parse_iso(args.now) if args.now else now_cst()
    out = census(ROOT, now=now)
    if args.cmd == "run":
        os.makedirs(os.path.dirname(args.json), exist_ok=True)
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    print(json.dumps({"verdict": out["verdict"], "worst_lag": out["worst_lag"],
                      "flags": out["flags"], "reading": out["reading"]},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
