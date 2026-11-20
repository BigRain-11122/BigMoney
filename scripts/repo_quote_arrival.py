"""When does a repo quote session actually land on this repo's disk?

r1877. The CEO page priced its cash half off a repo quote two sessions behind the bar it
priced (`spot 2026-11-17` on a `2026-11-19` page), and the only honest question left is
whose clock that is. The page writes at ~22:30 the same evening; the repo panel is written
by `update_repo` on this fleet's own schedule. Neither face records *arrival* -- a csv row
says which session it describes, never when it appeared.

Git does record it. Every commit that touches `data/repo_daily/GC001.csv` leaves behind the
panel tail as of that commit, so the first commit whose tail reaches session D dates D's
arrival. This face reads that history and answers three questions the page cannot:

  1. how many calendar days after the session does its quote reach the panel (median/p90)
  2. are sessions batched -- does one commit carry several sessions at once
  3. given the page's write hour, what is the freshest session it could ever have priced

It is a measurement, not a judgement: no gate fires, no threshold is set. The number is
read off the git history; `--check` re-derives it byte for byte.

    python scripts/repo_quote_arrival.py run      # write results/repo_quote_arrival.json
    python scripts/repo_quote_arrival.py --check   # recompute, compare with what is on disk
    python scripts/repo_quote_arrival.py --selftest
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = "data/repo_daily/GC001.csv"
OUT = os.path.join(ROOT, "results", "repo_quote_arrival.json")
PAGE_DIR = os.path.join(ROOT, "docs", "live_usage")

# r1880: a commit carrying this many first sightings at once is a history load (the
# 2026-09-27 import landed 3,737 sessions from 2011), not a delivery.  Mixed together
# the "median arrival" reads 2,783 days -- a number about the importer, not about
# whether tonight's page could have priced a fresher session.
BULK_IMPORT_SESSIONS = 20
# How many of the most recent dated pages are re-judged against the arrival history.
PAGE_WINDOW = 30


def _git(*args: str) -> str:
    p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), (p.stderr or "").strip()[:200]))
    return p.stdout


def _dated_rows(blob: str) -> set:
    """Every session a csv blob dates (a csv dates its own rows; the tail alone lies)."""
    out = set()
    for line in blob.splitlines():
        parts = line.strip().split(",")
        if parts and len(parts[0]) == 10 and parts[0][4] == "-" and parts[0][7] == "-":
            try:
                out.add(dt.date.fromisoformat(parts[0]))
            except ValueError:
                continue
    return out


def _tail_session(blob: str):
    """Last dated row of a csv blob (None = no dated row)."""
    rows = _dated_rows(blob)
    return max(rows) if rows else None


def arrivals(rel: str = REL) -> list:
    """[(commit_sha, arrived_at, dates)] in commit order (oldest first)."""
    log = _git("log", "--reverse", "--format=%H|%aI", "--", rel)
    out = []
    for line in log.splitlines():
        if not line.strip():
            continue
        sha, when = line.split("|", 1)
        try:
            stamp = dt.datetime.fromisoformat(when)
        except ValueError:
            continue
        dates = _dated_rows(_git("show", "%s:%s" % (sha, rel)))
        if dates:
            out.append((sha, stamp, dates))
    return out


def measure(rows: list, baseline=frozenset()) -> dict:
    """First sighting of each session + per-commit batch sizes.

    `rows` is [(sha, arrived_at, set_of_dates)]: one commit can carry several sessions at
    once (2026-11-20 landed both 11-18 and 11-19 in a single commit), so a commit's
    contribution is the date SET difference -- reading only the tail would call that one
    session and quietly understate both the batch and the lag.
    """
    first = {}
    batches = []
    seen = set(baseline)
    for sha, stamp, dates in rows:
        added = sorted(dates - seen)
        for sess in added:
            first[sess] = {"sha": sha, "at": stamp, "session": sess}
        if added:
            batches.append({"sha": sha, "at": stamp.isoformat(), "n_sessions": len(added),
                            "sessions": [s.isoformat() for s in added]})
        seen |= set(dates)

    bulk_shas = {b["sha"] for b in batches if b["n_sessions"] >= BULK_IMPORT_SESSIONS}

    lags_d = []
    for sess, rec in sorted(first.items()):
        at = rec["at"]
        # arrival is judged in the commit's own clock against the session's close date
        d = (at.date() - sess).days
        rec["lag_days"] = d
        rec["bulk"] = rec["sha"] in bulk_shas
        lags_d.append(d)

    # Steady state = deliveries.  A history load is excluded from the headline number
    # because its lag measures when somebody finally imported 2011, not the collector.
    steady = [r["lag_days"] for r in first.values() if not r["bulk"]]

    def _stats(vals):
        vals = sorted(vals)
        m = len(vals)
        if not m:
            return {"n": 0, "median": None, "p90": None, "max": None, "min": None,
                    "share_next_day_or_later": None}

        def _pct(p):
            i = min(m - 1, max(0, int(round(p / 100.0 * (m - 1)))))
            return vals[i]

        return {"n": m, "median": _pct(50), "p90": _pct(90), "max": vals[-1], "min": vals[0],
                "share_next_day_or_later": round(sum(1 for d in vals if d >= 1) / float(m), 4)}

    batch_sizes = [b["n_sessions"] for b in batches]
    return {
        "sessions_seen": len(lags_d),
        "first_session": min(first).isoformat() if first else None,
        "last_session": max(first).isoformat() if first else None,
        "lag_days": _stats(steady),
        "lag_days_all_history": _stats(lags_d),
        "bulk_imports": [{"sha": b["sha"][:8], "at": b["at"], "n_sessions": b["n_sessions"]}
                         for b in batches if b["sha"] in bulk_shas],
        "share_next_day_or_later": _stats(steady)["share_next_day_or_later"],
        "batched_commits": sum(1 for b in batch_sizes if b > 1),
        "max_batch": max(batch_sizes) if batch_sizes else 0,
        "per_session": {s.isoformat(): {"lag_days": r["lag_days"],
                                        "arrived": r["at"].isoformat(),
                                        "bulk": r["bulk"]}
                        for s, r in sorted(first.items())},
        "batches": batches,
    }


def _local_naive(stamp: dt.datetime) -> dt.datetime:
    """Both clocks are this machine's wall clock; git writes an offset, pages do not."""
    if stamp.tzinfo is not None:
        return stamp.astimezone().replace(tzinfo=None)
    return stamp


def frontier_at(per_session: dict, when: dt.datetime):
    """The freshest session a reader at `when` could have priced.

    Nothing is "late" until it has landed: a page that prices the last session on disk
    is at its frontier, even when the market has traded two more sessions since.
    """
    when = _local_naive(when)
    best = None
    for sess, rec in per_session.items():
        at = _local_naive(dt.datetime.fromisoformat(rec["arrived"]))
        if at <= when:
            day = dt.date.fromisoformat(sess) if isinstance(sess, str) else sess
            if best is None or day > best:
                best = day
    return best


def page_prices():
    """[(page_name, written_at, priced_session)] for dated pages, oldest first.

    The page itself records both halves: the envelope clock it was rendered on and the
    session its cash band says it quoted.  A page with no cash band is skipped -- "no
    band" is not "priced nothing".
    """
    out = []
    if not os.path.isdir(PAGE_DIR):
        return out
    for name in sorted(os.listdir(PAGE_DIR)):
        if not (name.startswith("LIVE-") and name.endswith(".json")) or "latest" in name:
            continue
        try:
            with open(os.path.join(PAGE_DIR, name), encoding="utf-8") as fh:
                d = json.load(fh)
        except (OSError, ValueError):
            continue
        stamp = d.get("generated") or d.get("ts")
        spot = (((d.get("etf_order") or {}).get("cash_leg") or {})
                .get("bands") or {}).get("spot") or {}
        sess = spot.get("as_of")
        if not stamp or not sess:
            continue
        try:
            written = dt.datetime.fromisoformat(stamp)
        except ValueError:
            continue
        out.append((name, written, dt.date.fromisoformat(sess)))
    return out


def judge_pages(per_session: dict, pages: list) -> dict:
    """Each page's priced session against the frontier its own clock could reach."""
    rows = []
    for name, written, sess in pages[-PAGE_WINDOW:]:
        fr = frontier_at(per_session, written)
        if fr is None:
            rows.append({"page": name, "written": written.isoformat(timespec="seconds"),
                         "priced": sess.isoformat(), "frontier": None,
                         "gap_sessions": None, "verdict": "NO_ARRIVAL_YET"})
            continue
        gap = (fr - sess).days
        rows.append({"page": name, "written": written.isoformat(timespec="seconds"),
                     "priced": sess.isoformat(), "frontier": fr.isoformat(),
                     "gap_days": gap,
                     "verdict": "AT_FRONTIER" if gap <= 0 else "BEHIND_FRONTIER"})
    behind = [r for r in rows if r["verdict"] == "BEHIND_FRONTIER"]
    return {
        "pages_judged": len(rows),
        "pages_behind": len(behind),
        "worst_gap_days": max([r["gap_days"] for r in behind], default=0),
        "verdict": ("NO_PAGES" if not rows else
                    ("PAGE_AT_FRONTIER" if not behind else "PAGE_BEHIND_FRONTIER")),
        "rows": rows,
    }


def build() -> dict:
    rows = arrivals()
    data = measure(rows)
    data["page_vs_frontier"] = judge_pages(data["per_session"], page_prices())
    data["source"] = REL
    data["method"] = ("first commit whose tail reaches a session dates that session's "
                      "arrival; lag_days = commit date - session date, bulk imports "
                      "(>=%d sessions in one commit) excluded from the headline"
                      % BULK_IMPORT_SESSIONS)
    data["evidence_cutoff"] = data.get("last_session")
    data["generated"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    return data


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--selftest", dest="selftest_flag", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest_flag or args.cmd == "selftest":
        return _selftest()

    data = build()
    if args.cmd == "check":
        if not os.path.exists(OUT):
            print("[repo_quote_arrival] STALE -- face missing (nothing on disk to check)")
            return 3
        with open(OUT, encoding="utf-8") as fh:
            old = json.load(fh)
        diff = [k for k in ("sessions_seen", "last_session", "lag_days",
                            "lag_days_all_history", "bulk_imports",
                            "share_next_day_or_later", "per_session", "page_vs_frontier")
                if old.get(k) != data.get(k)]
        if diff:
            print("[repo_quote_arrival] STALE -- %s differ from the file on disk" % ", ".join(diff))
            return 3
        pv = data["page_vs_frontier"]
        print("[repo_quote_arrival] CHECK_OK %d sessions, steady median lag %s day(s) | "
              "pages %d, behind %d (%s)"
              % (data["sessions_seen"], data["lag_days"]["median"], pv["pages_judged"],
                 pv["pages_behind"], pv["verdict"]))
        return 0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    if not args.quiet:
        pv = data["page_vs_frontier"]
        print("[repo_quote_arrival] %d sessions %s..%s | steady median lag %s day(s) "
              "(n=%s), p90 %s, share >=1 day %.1f%% | batched commits %d (max %d)"
              % (data["sessions_seen"], data["first_session"], data["last_session"],
                 data["lag_days"]["median"], data["lag_days"]["n"],
                 data["lag_days"]["p90"],
                 100.0 * (data["share_next_day_or_later"] or 0.0),
                 data["batched_commits"], data["max_batch"]))
        print("[repo_quote_arrival] %s -- %d page(s) judged, %d behind, worst gap %s day(s)"
              % (pv["verdict"], pv["pages_judged"], pv["pages_behind"], pv["worst_gap_days"]))
        for row in pv["rows"][-3:]:
            print("    %s written %s priced %s frontier %s -> %s"
                  % (row["page"], row["written"], row["priced"], row["frontier"],
                     row["verdict"]))
        print("  -> %s" % os.path.relpath(OUT, ROOT))
    return 0


def _selftest() -> int:
    bad = []

    def leg(name, ok, detail=""):
        print(("PASS" if ok else "FAIL") + " " + name + (" | " + detail if detail else ""))
        if not ok:
            bad.append(name)

    # L1: a blob's tail is its last dated row, not its last line (blank tail tolerated)
    blob = "date,open,high,low\n2026-11-18,1.1,1.2,1.0\n2026-11-19,1.2,1.3,1.1\n\n"
    leg("L1 tail session", _tail_session(blob) == dt.date(2026, 11, 19), str(_tail_session(blob)))
    leg("L1b undated blob -> None", _tail_session("date,open\n") is None)

    # L2: a commit that repeats the same dates names no new session
    _one = {dt.date(2026, 11, 19)}
    leg("L2 repeat names nothing new",
        measure([("a" * 40, dt.datetime(2026, 11, 20, 2, 0), _one),
                 ("b" * 40, dt.datetime(2026, 11, 21, 2, 0), _one)])["sessions_seen"] == 1)

    # L3: measure() counts first sightings only, and lag = commit date - session date
    rows = [(("a" * 40), dt.datetime(2026, 11, 18, 2, 0), {dt.date(2026, 11, 17)}),
            (("b" * 40), dt.datetime(2026, 11, 20, 2, 0), {dt.date(2026, 11, 17),
                                                          dt.date(2026, 11, 19)}),
            (("c" * 40), dt.datetime(2026, 11, 21, 2, 0), {dt.date(2026, 11, 19)})]
    m = measure(rows)
    leg("L3 first sighting only", m["sessions_seen"] == 2, str(m["sessions_seen"]))
    leg("L3b lag = commit date - session date",
        m["per_session"]["2026-11-19"]["lag_days"] == 1
        and m["per_session"]["2026-11-17"]["lag_days"] == 1,
        json.dumps(m["per_session"], sort_keys=True))

    # L4: a commit that carries two sessions at once is a batch, and the older one keeps
    # its own (larger) lag -- the exact shape the 2026-11-20 commit had
    rows2 = [(("d" * 40), dt.datetime(2026, 11, 20, 2, 0), {dt.date(2026, 11, 18),
                                                           dt.date(2026, 11, 19)})]
    m2 = measure(rows2)
    leg("L4 a two-session commit is a batch",
        m2["batched_commits"] == 1 and m2["max_batch"] == 2
        and m2["per_session"]["2026-11-18"]["lag_days"] == 2,
        "batch=%s lag18=%s" % (m2["max_batch"], m2["per_session"]["2026-11-18"]["lag_days"]))

    # L5: the share is over sessions seen, and an empty history answers None not 0
    leg("L5 empty history -> None lags", measure([])["lag_days"]["median"] is None)

    # L6: a history load must not become the collector's median.  The 2011 batch lands
    # 3,737 sessions at once; one delivery the next evening lands one session at lag 1.
    bulk = [(("e" * 40), dt.datetime(2026, 9, 27, 14, 40),
             {dt.date(2011, 5, 13) + dt.timedelta(days=i) for i in range(25)})]
    delivery = [(("f" * 40), dt.datetime(2026, 11, 20, 2, 0), {dt.date(2026, 11, 19)})]
    m3 = measure(bulk + delivery)
    leg("L6 bulk import excluded from the headline lag",
        m3["lag_days"]["n"] == 1 and m3["lag_days"]["median"] == 1
        and m3["lag_days_all_history"]["n"] == 26
        and len(m3["bulk_imports"]) == 1,
        "steady n=%s median=%s all n=%s" % (m3["lag_days"]["n"], m3["lag_days"]["median"],
                                            m3["lag_days_all_history"]["n"]))

    # L7: the frontier is the freshest session that has ALREADY landed at that clock --
    # a page written before the 02:22 delivery cannot be behind by pricing the day before
    ps = {"2026-11-17": {"arrived": "2026-11-17T20:23:38+08:00"},
          "2026-11-19": {"arrived": "2026-11-20T02:22:18+08:00"}}
    leg("L7 frontier respects arrival clock",
        frontier_at(ps, dt.datetime(2026, 11, 19, 22, 51)) == dt.date(2026, 11, 17)
        and frontier_at(ps, dt.datetime(2026, 11, 20, 12, 49)) == dt.date(2026, 11, 19))

    # L8: same two pages, judged -- the evening one is AT its frontier, and a page that
    # priced 11-17 on the 11-20 afternoon clock is the one that is behind
    pages = [("LIVE-2026-11-19.json", dt.datetime(2026, 11, 19, 22, 51), dt.date(2026, 11, 17)),
             ("LIVE-2026-11-20.json", dt.datetime(2026, 11, 20, 12, 49), dt.date(2026, 11, 17))]
    j = judge_pages(ps, pages)
    leg("L8 judge: behind only where the clock allows",
        j["verdict"] == "PAGE_BEHIND_FRONTIER" and j["pages_behind"] == 1
        and j["worst_gap_days"] == 2, json.dumps(j["rows"], sort_keys=True))

    print("selftest %d/%d" % (8 - len(bad), 8))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
