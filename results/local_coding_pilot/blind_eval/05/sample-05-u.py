"""inbox_aging.py — fleet inbox directed-message aging / unprocessed scanner.

Task 05 of the T-70 local-coding pilot (frozen prompt
results/local_coding_pilot/tasks/05/prompt.md, commit b626f6ca).

Scans MSG-*.md files sitting unprocessed in fleet/inbox/, ages each against
its filename timestamp, classifies a per-message ETA from recipient-machine
heartbeat liveness, and prints a one-line summary plus per-message rows.

Exit codes: 0 ok (incl. empty inbox) | 1 stalled1h>=1 warning | 2 usage/missing dir.
"""

import glob
import json
import os
import re
import sys
from datetime import datetime

NAME_RE = re.compile(r"^MSG-(\d{8})-(\d{4})-(ALL|bm-[a-z0-9]+)-(.+)\.md$")
FRESH_MIN = 20.0
STALL_H = 1.0


def _aware(dt):
    """naive -> tz-aware in system local timezone (aware passes through)."""
    return dt if dt.tzinfo is not None else dt.astimezone()


def _now_local():
    return _aware(datetime.now())


def parse_name(filename):
    """(filed_at aware or None, recipient) — regex miss returns None (name_fail)."""
    m = NAME_RE.match(filename)
    if not m:
        return None
    try:
        filed = datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M")
    except ValueError:
        # digits matched the shape but the calendar/time is impossible
        return (None, m.group(3))
    return (_aware(filed), m.group(3))


def _parse_ls(raw):
    if not isinstance(raw, str) or not raw:
        return None
    try:
        return _aware(datetime.fromisoformat(raw))
    except ValueError:
        return None


def load_heartbeats(machines_dir):
    """{machine_id: last_seen ISO string or None}; unreadable files skipped."""
    hbs = {}
    for path in sorted(glob.glob(os.path.join(machines_dir, "*.json"))):
        try:
            with open(path, encoding="utf-8-sig") as f:
                j = json.load(f)
        except (OSError, ValueError):
            continue
        if not isinstance(j, dict):
            continue
        mid = j.get("machine_id") or os.path.splitext(os.path.basename(path))[0]
        if not isinstance(mid, str) or not mid:
            continue
        hbs[mid] = j.get("last_seen")
    return hbs


def recipient_liveness_min(recipient, heartbeats, now):
    """Minutes since recipient's last heartbeat; None = unknown."""
    if recipient == "ALL":
        stamps = [s for s in (_parse_ls(v) for v in heartbeats.values()) if s]
        if not stamps:
            return None
        return (now - max(stamps)).total_seconds() / 60.0
    if recipient not in heartbeats:
        return None
    stamp = _parse_ls(heartbeats[recipient])
    if stamp is None:
        return None
    return (now - stamp).total_seconds() / 60.0


def scan_entries(filenames, heartbeats, now):
    """Core: list of MSG-*.md filenames + {machine_id: last_seen str or None}
    + frozen tz-aware now -> (rows, summary). Pure, no IO."""
    rows = []
    name_fail = 0
    for fn in filenames:
        parsed = parse_name(fn)
        if parsed is None:
            name_fail += 1
            continue
        filed, recipient = parsed
        if filed is None:
            age_h = -1.0
        else:
            age_h = (now - filed).total_seconds() / 3600.0
        if age_h < 0:
            eta = "clock_anomaly"
        else:
            live = recipient_liveness_min(recipient, heartbeats, now)
            eta = ("due_next_pull" if live is not None and live <= FRESH_MIN
                   else "stranded")
        rows.append({
            "filename": fn,
            "recipient": recipient,
            "age_h": age_h,
            "eta": eta,
        })
    valid_ages = [r["age_h"] for r in rows if r["age_h"] >= 0]
    summary = {
        "total": len(filenames),
        "name_fail": name_fail,
        "unprocessed": len(rows),
        "stalled1h": sum(1 for r in rows if r["age_h"] > STALL_H),
        "stranded": sum(1 for r in rows if r["eta"] == "stranded"),
        "max_age_h": max(valid_ages) if valid_ages else -1.0,
    }
    rows.sort(key=lambda r: (-r["age_h"], r["filename"]))
    return rows, summary


def _fmt_h(v):
    return f"{v:.1f}"


def render(rows, summary):
    lines = [
        "INBOX total={total} name_fail={name_fail} unprocessed={unprocessed} "
        "stalled1h={stalled1h} stranded={stranded} max_age_h={max_age_h}".format(
            **{**summary, "max_age_h": _fmt_h(summary["max_age_h"])})
    ]
    for r in rows:
        lines.append("MSG {filename} to={recipient} age_h={age} eta={eta}".format(
            filename=r["filename"], recipient=r["recipient"],
            age=_fmt_h(r["age_h"]), eta=r["eta"]))
    return lines


def live(inbox_dir, machines_dir):
    if not os.path.isdir(inbox_dir):
        print(f"inbox dir not found: {inbox_dir}", file=sys.stderr)
        return 2
    filenames = sorted(
        os.path.basename(p)
        for p in glob.glob(os.path.join(inbox_dir, "MSG-*.md"))
        if os.path.isfile(p))
    heartbeats = load_heartbeats(machines_dir)
    rows, summary = scan_entries(filenames, heartbeats, _now_local())
    for line in render(rows, summary):
        print(line)
    return 1 if summary["stalled1h"] >= 1 else 0


def _selftest():
    ok = 0

    def check(cond, label):
        nonlocal ok
        assert cond, f"FAIL: {label}"
        ok += 1

    now = _aware(datetime(2026, 9, 26, 0, 30, 0))

    # group 1: mixed legal sample — fresh due / stale stranded / bad clock
    hb1 = {"bm-a": "2026-09-26 00:25:00", "bm-b": "2026-09-25 20:00:00"}
    files1 = [
        "MSG-20260926-0000-bm-a-topic-one.md",   # age 0.5h, bm-a fresh 5min
        "MSG-20260925-0000-bm-b-topic-two.md",   # age 24.5h, bm-b stale 260min
        "MSG-20260913-9999-bm-c-badclock.md",    # 99:99 -> parse fail
    ]
    rows, s = scan_entries(files1, hb1, now)
    check(s["total"] == 3 and s["name_fail"] == 0 and s["unprocessed"] == 3,
          "g1 counts")
    check(s["stalled1h"] == 1, "g1 stalled1h")
    check(s["stranded"] == 1, "g1 stranded")
    check(abs(s["max_age_h"] - 24.5) < 1e-9, "g1 max_age precise")
    check(rows[0]["filename"] == "MSG-20260925-0000-bm-b-topic-two.md"
          and rows[0]["eta"] == "stranded", "g1 sort oldest first + stranded")
    check(rows[1]["eta"] == "due_next_pull", "g1 fresh -> due_next_pull")
    check(rows[2]["eta"] == "clock_anomaly" and rows[2]["age_h"] == -1.0,
          "g1 impossible clock -> -1.0 clock_anomaly")

    # group 2: ALL recipient takes freshest machine liveness
    hb2 = {"bm-a": "2026-09-25 10:00:00", "bm-b": "2026-09-26 00:20:00"}
    rows2, s2 = scan_entries(["MSG-20260925-2355-ALL-patrol.md"], hb2, now)
    check(rows2[0]["eta"] == "due_next_pull", "ALL uses freshest heartbeat")
    rows2b, s2b = scan_entries(["MSG-20260925-2355-ALL-patrol.md"], {}, now)
    check(rows2b[0]["eta"] == "stranded", "ALL no heartbeats -> stranded")

    # boundary: name regex violations count as name_fail, no rows
    files3 = ["MSG-20260923-1430.md", "MSG-notadate-1430-bm-a-x.md",
              "msg-20260923-1430-bm-a-x.md"]
    rows3, s3 = scan_entries(files3, {"bm-a": "2026-09-26 00:29:00"}, now)
    check(s3["name_fail"] == 3 and s3["unprocessed"] == 0 and not rows3,
          "name_fail counting")

    # boundary: future timestamp -> honest negative age, not stalled
    rows4, s4 = scan_entries(["MSG-20260926-0200-bm-a-future.md"],
                             {"bm-a": "2026-09-26 00:29:00"}, now)
    check(rows4[0]["eta"] == "clock_anomaly" and abs(rows4[0]["age_h"] + 1.5) < 1e-9
          and s4["stalled1h"] == 0, "future ts -> clock_anomaly not stalled")

    # boundary: recipient without heartbeat file -> unknown -> stranded
    rows5, _ = scan_entries(["MSG-20260926-0000-bm-d-newnode.md"],
                            {"bm-a": "2026-09-26 00:29:00"}, now)
    check(rows5[0]["eta"] == "stranded", "missing heartbeat -> stranded")

    # boundary: heartbeat present but last_seen None/unparseable -> unknown
    rows6, _ = scan_entries(["MSG-20260926-0000-bm-a-x.md"],
                            {"bm-a": None}, now)
    check(rows6[0]["eta"] == "stranded", "last_seen None -> unknown stranded")
    rows6b, _ = scan_entries(["MSG-20260926-0000-bm-a-x.md"],
                             {"bm-a": "not-a-date"}, now)
    check(rows6b[0]["eta"] == "stranded", "unparseable last_seen -> stranded")

    # boundary: sort tie by filename ascending
    rows7, _ = scan_entries(
        ["MSG-20260926-0000-bm-b-zeta.md", "MSG-20260926-0000-bm-a-alpha.md"],
        {"bm-a": "2026-09-26 00:29:00", "bm-b": "2026-09-26 00:29:00"}, now)
    check([r["filename"] for r in rows7] ==
          ["MSG-20260926-0000-bm-a-alpha.md", "MSG-20260926-0000-bm-b-zeta.md"],
          "tie sort by filename asc")

    # boundary: zero valid ages -> max_age_h -1.0 rendered as "-1.0"
    _, s8 = scan_entries(["MSG-20260913-9999-bm-c-x.md"], {}, now)
    lines8 = render(*scan_entries(["MSG-20260913-9999-bm-c-x.md"], {}, now))
    check(s8["max_age_h"] == -1.0 and "max_age_h=-1.0" in lines8[0],
          "zero valid ages -> max_age_h=-1.0")

    # summary line shape
    lines1 = render(rows, s)
    check(lines1[0] == "INBOX total=3 name_fail=0 unprocessed=3 stalled1h=1 "
          "stranded=1 max_age_h=24.5", "summary line exact")
    check(lines1[1] == "MSG MSG-20260925-0000-bm-b-topic-two.md to=bm-b "
          "age_h=24.5 eta=stranded", "row line exact")

    print(f"selftest: {ok} assertions ALL PASS")
    return 0


def main(argv):
    if len(argv) < 2:
        print("usage: inbox_aging.py [selftest | [inbox_dir] [machines_dir]]",
              end="")
        print("  (defaults: fleet/inbox fleet/machines)", end="")
        return 2
    if argv[1] == "selftest":
        return _selftest()
    inbox_dir = argv[1] if len(argv) > 1 else "fleet/inbox"
    machines_dir = argv[2] if len(argv) > 2 else "fleet/machines"
    return live(inbox_dir, machines_dir)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
