# -*- coding: utf-8 -*-
"""data_lane_freshness.py -- one board: which forward data lanes are behind.

WHY (r1156): exchange_calendar_audit (r1286) gave ONE panel an independent
reference and a verdict. Every other forward-accumulation lane still decides
"am I late?" from its own bytes, so a lane that stops produces no error at all:
it simply stops writing files and every caller keeps reading yesterday's tail.
The 2026-10-30 measurement is the proof -- popularity (heat) last wrote
2026-10-20, moneyflow stopped 2026-10-19 at a source block, options at
2026-09-30, while every S6 leg returned rc=0 and no page mentioned any of it.
A heat day is not recoverable: the rank list is live and rolling.

So: one registry, one rule (the official trading calendar is the reference, the
lane's own tail is the measurement), one page. The board never fixes a lane and
never invents a number -- a lane with no artifact reads `absent`, not 0.

Design notes:
  - the calendar and the 15:30 expectation boundary are IMPORTED from
    exchange_calendar_audit, never re-derived (r1290 class: two faces, one rule)
  - a lane is described by a declarative entry, not by per-lane code, so adding
    a lane is one dict; `kind` selects the tail extractor
  - `external` lanes carry the verdict of the face that already audits them and
    the board re-judges the same tail anyway; disagreement is printed rather
    than averaged away
  - exit 0 = board computed (even when lanes are behind: this is a descriptive
    face, the attention signal lives in the JSON verdict + dashboard row),
    exit 2 = mechanism failure (no calendar / unreadable registry artifact)
"""
import argparse
import datetime as dt
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from scripts.exchange_calendar_audit import (  # noqa: E402
    CAL_PATH, CLOSE_ACCEPT_TIME, load_calendar, expected_last_day)

try:                                     # whose lane is it (single source, R31)
    from config.lane_io import lane_host as _lane_host, machine_id as _machine_id
except Exception:                        # pragma: no cover - fail-open, disclosed
    _lane_host = None
    _machine_id = lambda: "unknown"      # noqa: E731

OUT_PATH = os.path.join(ROOT, "results", "data_lane_freshness.json")
MD_PATH = os.path.join(ROOT, "docs", "data_lanes", "FRESHNESS.md")
MACHINES_DIR = os.path.join(ROOT, "fleet", "machines")
# A lane can only be certified by a host that is still reporting. The loop runs
# every few minutes, so two hours of silence on the owning machine means nobody
# is collecting, not that the copy on this disk is authoritative.
HOST_DOWN_H = 2.0

DAY8_RE = re.compile(r"^(\d{4})(\d{2})(\d{2})\.json$")
# envelope keys that name the machine whose data the number describes
REPORTER_KEYS = ("machine", "lane_machine", "reporter", "writer")

# ---------------------------------------------------------------- registry
# kind:
#   day_files  `dir` holds one file per trading day named YYYYMMDD.json
#   zt_days    data/zt_pool/collected_days.json ({face: [iso days]})
#   status     one status envelope with a dotted date key
#   external   a lane audited by another face: tail_key is read from it, and
#              its own verdict travels as `cited_verdict` for cross-checking
LANES = [
    {"lane": "heat", "dept": "data", "owner": "bm-a", "writer": "update_heat",
     "kind": "status", "path": "results/heat_update_status.json",
     "key": "latest_snapshot",
     "fallback_day_files": "data/heat/popularity",
     "fatal_loss": "a missed day is permanent: the guba rank is a live rolling "
                   "list with no retrievable history (HEAT_ATTENTION_SPEC §1)"},
    {"lane": "zt_pool", "dept": "data", "owner": "bm-a",
     "writer": "update_zt_pool", "kind": "zt_days",
     "path": "data/zt_pool/collected_days.json",
     "fatal_loss": "pool day slices are terminal at the close; no superset arrives later"},
    {"lane": "lhb", "dept": "data", "owner": "bm-a", "writer": "update_lhb",
     "kind": "status", "path": "results/lhb_update_status.json", "key": "cutoff"},
    {"lane": "futures", "dept": "data", "owner": "bm-a", "writer": "update_futures",
     "kind": "status", "path": "results/futures_update_status.json", "key": "data_cutoff"},
    {"lane": "repo", "dept": "data", "owner": "bm-a", "writer": "update_repo",
     "kind": "status", "path": "results/repo_update_status.json", "key": "data_cutoff"},
    {"lane": "moneyflow", "dept": "data", "owner": "bm-a",
     "writer": "update_moneyflow", "kind": "status",
     "path": "results/moneyflow_update_status.json", "key": "panel.cutoff"},
    {"lane": "astock_daily", "dept": "data", "owner": "bm-b",
     "writer": "update_astock_daily", "kind": "status",
     "path": "results/astock_daily_update_status.json", "key": "panel.cutoff"},
    {"lane": "options", "dept": "data", "owner": "bm-a", "writer": "update_options",
     "kind": "status", "path": "results/options_update_status.json",
     "key": "panel.max_collected",
     # the chain's own stdout says this face is closed: "options face closed per
     # O-20261009-1105 (consumer audit: historical wave-2 batch only, zero
     # forward)". Without this line the board cries wolf on a face that was
     # deliberately stopped -- and a false alarm is what makes an alert useless.
     "retired": "O-20261009-1105 -- the options face is closed; the panel is a "
                "historical wave-2 batch with no forward accumulation"},
    {"lane": "etf_panel", "dept": "data", "owner": "bm-a",
     "writer": "update_etf_daily", "kind": "external",
     "path": "results/data_lag_audit.json", "tail_key": "panel.effective_cutoff",
     "verdict_key": "verdict", "audited_by": "exchange_calendar_audit (E136)"},
    {"lane": "marks", "dept": "data", "owner": "bm-b", "writer": None,
     "kind": "external",
     "path": "results/marks_coverage.json", "tail_key": "last_captured",
     "audited_by": "marks_coverage (the paper marks lane keeps its own hole "
                   "counters; this row reads only its last captured day)"},
]


# ---------------------------------------------------------------- extractors

def _get(doc, dotted):
    cur = doc
    for part in dotted.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def _as_date(value):
    """ISO date/datetime string -> 'YYYY-MM-DD', anything else -> None.

    A lane that stores a timestamp must not be rounded into a "fresh" day, and
    a lane that stores prose must read as absent rather than raising.
    """
    if not isinstance(value, str):
        return None
    s = value.strip()[:10]
    try:
        return dt.date.fromisoformat(s).isoformat()
    except ValueError:
        return None


def tail_day_files(dirpath, pattern=DAY8_RE):
    """Newest YYYYMMDD.json in a directory -> ISO date or None."""
    if not os.path.isdir(dirpath):
        return None, {"files": 0}
    days = []
    for name in os.listdir(dirpath):
        m = pattern.match(name)
        if m:
            days.append(f"{m.group(1)}-{m.group(2)}-{m.group(3)}")
    if not days:
        return None, {"files": 0}
    return max(days), {"files": len(days), "first": min(days)}


def tail_zt_days(path):
    """{face: [days]} -> (newest day across faces, per-face tails)."""
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    faces = {}
    for face, days in doc.items():
        if isinstance(days, list) and days:
            faces[face] = max(_as_date(d) or "" for d in days)
    faces = {k: v for k, v in faces.items() if v}
    return (max(faces.values()) if faces else None), faces


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- judgement

def judge(tail, days, now):
    """(verdict, missing_days, expected). One rule for every lane.

    expected = last official day whose data must exist by `now` (15:30
    boundary, imported from the calendar audit). Anything the lane has not
    reached is missing; the verdict says whether that is publication lag
    (today, or one day) or a stopped feed.
    """
    exp, _past = expected_last_day(days, now)
    if not exp:
        return "unknown", [], None
    if tail is None:
        return "absent", [], exp
    missing = [d for d in days if tail < d <= exp]
    if not missing:
        return "in_sync", [], exp
    today = now.date().isoformat()
    if missing == [exp] and exp == today:
        return "today_pending", missing, exp
    if len(missing) == 1:
        return "behind_1d", missing, exp
    return "stalled", missing, exp


def _host_health(host, now, machines_dir=None):
    """How long ago the lane's host last wrote its heartbeat.

    Measured 2026-10-30: the board printed seven `unverifiable` lanes and named
    no culprit, so a reader could not tell a dead lane from a dead machine. The
    host's own heartbeat answers that. `alive=None` means no usable heartbeat
    file: unknown, never "dead" (an absent file is not evidence of a crash)."""
    out = {"last_seen": None, "age_h": None, "alive": None}
    if not host:
        return out
    p = os.path.join(machines_dir or MACHINES_DIR, f"{host}.json")
    try:
        d = read_json(p)
    except Exception:
        return out
    raw = d.get("clock_read") or d.get("last_seen") or d.get("ts")
    if not isinstance(raw, str) or not raw:
        return out
    try:
        when = dt.datetime.fromisoformat(raw)
    except Exception:
        return out
    if when.tzinfo is not None:
        # heartbeat timestamps carry the machine's own UTC offset; `now` is the
        # same wall clock without one, so borrow the offset instead of guessing
        when = when.replace(tzinfo=None)
    out["last_seen"] = raw
    out["age_h"] = round((now - when).total_seconds() / 3600.0, 2)
    out["alive"] = out["age_h"] <= HOST_DOWN_H
    return out


def audit(days, now, lanes=None, root=ROOT, machines_dir=None):
    rows = []
    here = _machine_id() or "unknown"
    for spec in (lanes if lanes is not None else LANES):
        row = {"lane": spec["lane"], "dept": spec.get("dept"),
               "owner": spec.get("owner"), "kind": spec["kind"]}
        tail, extra = None, {}
        try:
            if spec["kind"] == "day_files":
                tail, extra = tail_day_files(os.path.join(root, spec["dir"]))
            elif spec["kind"] == "zt_days":
                tail, faces = tail_zt_days(os.path.join(root, spec["path"]))
                extra["faces"] = faces   # nested: a face name is not a lane key
            elif spec["kind"] in ("status", "external"):
                path = os.path.join(root, spec["path"])
                if os.path.exists(path):
                    doc = read_json(path)
                    key = spec.get("key") or spec.get("tail_key")
                    tail = _as_date(_get(doc, key))
                    extra["reported_by"] = next(
                        (doc[k] for k in REPORTER_KEYS
                         if isinstance(doc.get(k), str)), None)
                    # declared takeover (T25, r1161): the rows are machine-local,
                    # so a takeover re-declares the writer instead of moving
                    # them -- the envelope carries that declaration.
                    auth_blk = doc.get("authority")
                    if isinstance(auth_blk, dict):
                        extra["data_face_machine"] = auth_blk.get(
                            "data_face_machine")
                        extra["declared_takeover_by"] = auth_blk.get(
                            "took_over_by")
                    if tail is None and spec.get("fallback_day_files"):
                        # the lane publishes no tail yet: read the copy on this
                        # disk, say so, and let the authority layer refuse to
                        # certify it (r1156 first live case: heat)
                        tail, fb = tail_day_files(
                            os.path.join(root, spec["fallback_day_files"]))
                        extra.update(fb)
                        extra["tail_source"] = "local_copy_fallback"
                        extra["reported_by"] = None
                    if spec["kind"] == "external":
                        extra["audited_by"] = spec.get("audited_by")
                        if spec.get("verdict_key"):
                            extra["cited_verdict"] = _get(doc, spec["verdict_key"])
                else:
                    extra["missing_artifact"] = spec["path"]
            else:
                raise ValueError(f"unknown lane kind {spec['kind']!r}")
        except Exception as ex:  # noqa: BLE001
            row.update({"tail": None, "verdict": "unreadable",
                        "error": f"{type(ex).__name__}: {str(ex)[:160]}"})
            row.update(extra)
            rows.append(row)
            continue
        verdict, missing, exp = judge(tail, days, now)
        row.update({"tail": tail, "expected": exp, "missing_days": missing,
                    "n_missing": len(missing), "verdict": verdict})
        row.update(extra)
        if spec.get("fatal_loss"):
            row["loss_mode"] = spec["fatal_loss"]
        if extra.get("cited_verdict") and verdict != "today_pending":
            # two faces, one rule: if the auditing face says in_sync and the
            # board re-judges the same tail as late, print it rather than pick.
            row["face_disagreement"] = (
                extra["cited_verdict"] == "in_sync" and verdict != "in_sync")
        if spec["kind"] in ("day_files", "zt_days"):
            extra["reported_by"] = here
            extra["data_scope"] = "machine_local"
        rows.append(row)

    # ---- authority: whose number is this?
    # A status envelope is committed by whichever machine happened to run the
    # leg, and every machine also keeps its own gitignored copy of the data dir.
    # So "tail = 2026-10-20" can describe a dead lane OR a stale copy of a lane
    # that is alive on its host. Measured 2026-10-30: heat / repo / moneyflow /
    # options are ALL hosted by bm-b (config/lane_io), and this board was
    # reading bm-a's leftover copies as if they were the authority. The board
    # now says which it is instead of publishing a verdict it cannot stand
    # behind: the computed reading survives as `copy_verdict`, the verdict
    # itself becomes `unverifiable` unless a host's own face vouches for it.
    for r in rows:
        spec = next((s for s in (lanes if lanes is not None else LANES)
                     if s["lane"] == r["lane"]), {})
        host = None
        if _lane_host is not None and spec.get("writer"):
            try:
                host = _lane_host(spec["writer"], None)
            except Exception:
                host = None
        host = host or spec.get("owner")
        r["owner"] = r.get("owner") or spec.get("owner")
        rep = r.get("reported_by")
        if r["kind"] in ("day_files", "zt_days"):
            # a day-file dir is always somebody's local copy -- this machine's
            rep = rep or here
            auth = "host_copy" if (host and rep == host) else "non_host_copy"
        elif rep is None:
            auth = "unattributed"
        elif rep == host:
            auth = "host_envelope"
        else:
            auth = "non_host_envelope"
        # A declared takeover (T25, r1161) IS the authority for its rows: the
        # envelope names the taker as the data face, so its own tail is
        # meaningful. An anonymous "somebody else wrote this" stays refused.
        decl = r.get("declared_takeover_by")
        if auth == "non_host_envelope" and decl and decl == rep:
            auth = "declared_takeover"
        r["lane_host"] = host
        if host:
            # one truth: config/lane_hosts.json beats the hardcoded fallback
            # (measured 2026-10-30: heat printed owner bm-a, lane_host bm-b)
            r["owner"] = host
        r["authority"] = auth
        r["auditable"] = auth in ("host_copy", "host_envelope",
                                  "declared_takeover")
        if spec.get("retired"):
            # a closed face is neither fresh nor late: it is retired, and it
            # may not enter the attention count (false alarms kill alerts)
            r["copy_verdict"] = r.get("copy_verdict") or r["verdict"]
            r["verdict"] = "retired"
            r["retired_reason"] = spec["retired"]
            continue
        if not r["auditable"] and r["verdict"] not in ("absent", "unreadable"):
            r["copy_verdict"] = r["verdict"]
            r["verdict"] = "unverifiable"
            r["why"] = (
                "the lane publishes no tail and this reading is this machine's "
                "local copy; it is hosted by " + str(host)
                if r.get("tail_source") == "local_copy_fallback" else
                {
                    "non_host_copy": f"read from this machine's local copy; the "
                                     f"lane is hosted by {host}",
                    "non_host_envelope": f"the envelope was written by {rep}, not "
                                         f"by the lane host {host}",
                    "unattributed": "the envelope does not name the machine whose "
                                    "data it describes",
                }.get(auth, auth))
    rows.sort(key=lambda r: (-r.get("n_missing", 0), r["lane"]))
    counts = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    stale = [r for r in rows if r["verdict"] in ("stalled", "behind_1d",
                                                 "unreadable", "absent")]
    uncertified = [r for r in rows if r["verdict"] == "unverifiable"]
    # ---- who is supposed to vouch for the lanes nobody could certify
    hosts = {}
    for r in rows:
        host = r.get("lane_host")
        hh = _host_health(host, now, machines_dir)
        r["host_last_seen"] = hh["last_seen"]
        r["host_age_h"] = hh["age_h"]
        r["host_alive"] = hh["alive"]
        if not host or r["verdict"] == "retired":
            continue
        h = hosts.setdefault(host, {"host": host, "lanes": [],
                                    "lanes_unverifiable": [], "last_seen": None,
                                    "age_h": None, "alive": None})
        h["lanes"].append(r["lane"])
        if r["verdict"] == "unverifiable":
            h["lanes_unverifiable"].append(r["lane"])
        if hh["last_seen"] is not None:
            h["last_seen"], h["age_h"], h["alive"] = (
                hh["last_seen"], hh["age_h"], hh["alive"])
    # a lane nobody can certify AND whose host stopped reporting is not an open
    # question any more -- it is an outage with a name on it
    hosts_down = sorted(h["host"] for h in hosts.values()
                        if h["alive"] is False and h["lanes_unverifiable"])
    lanes_hostage = sorted(r["lane"] for r in rows
                           if r["verdict"] == "unverifiable"
                           and r.get("host_alive") is False)
    # a board that reads green because it could not certify anything would be
    # the very failure it exists to catch: 'uncertified' is its own verdict.
    verdict = ("attention" if stale else
               ("host_down" if hosts_down else
                ("uncertified" if uncertified else "all_fresh")))
    live = [r for r in rows if r["verdict"] != "retired"]
    worst_row = max(live, key=lambda r: r.get("n_missing", 0)) if live else None
    exp = rows[0].get("expected") if rows else None
    return {
        "schema": "data-lane-freshness/v1",
        "as_of": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "close_accept_time": CLOSE_ACCEPT_TIME.strftime("%H:%M"),
        "calendar_path": os.path.relpath(CAL_PATH, ROOT).replace("\\", "/"),
        "calendar_days": len(days),
        "expected_last_official_day": exp,
        "counts": counts,
        "n_lanes": len(rows),
        "n_auditable": sum(1 for r in rows if r.get("auditable")),
        "unverifiable_lanes": [r["lane"] for r in uncertified],
        "verdict": verdict,
        "hosts": {k: v for k, v in sorted(hosts.items())},
        "hosts_down": hosts_down,
        "lanes_hostage": lanes_hostage,
        "host_down_hours": HOST_DOWN_H,
        "worst": (worst_row["lane"] if (stale or uncertified) and worst_row
                  and worst_row.get("n_missing") else None),
        "note": ("Descriptive face, one rule per lane: the official calendar is "
                 "the reference, the lane's own tail is the measurement. A lane "
                 "with no artifact reads absent, never 0. A lane whose only "
                 "evidence was written by another machine's copy reads "
                 "unverifiable -- `copy_verdict` keeps what that copy said."),
        "lanes": rows,
    }


def render_md(report):
    head = (f"# Data lane freshness -- {report['as_of'][:10]}\n\n"
            f"Official reference: last day that must exist by "
            f"{report['close_accept_time']} = **{report['expected_last_official_day']}** "
            f"({report['calendar_days']} calendar days loaded).\n\n"
            f"Verdict: **{report['verdict']}** -- "
            f"{report['counts'].get('in_sync', 0)}/{report['n_lanes']} lanes in sync, "
            f"{report.get('n_auditable', 0)}/{report['n_lanes']} auditable from this "
            f"machine"
            + (f", worst = `{report['worst']}`" if report["worst"] else "") + ".\n\n")
    cols = ("| lane | host | tail | missing (official days) | verdict | authority |\n"
            "|---|---|---|---|---|---|\n")
    body = ""
    for r in report["lanes"]:
        miss = r.get("missing_days") or []
        miss_s = f"{len(miss)}" + (f": {', '.join(miss[:6])}" +
                                   (" …" if len(miss) > 6 else "") if miss else "")
        verdict = r["verdict"]
        if r.get("copy_verdict"):
            verdict += f" (copy said `{r['copy_verdict']}`)"
        body += (f"| `{r['lane']}` | {r.get('lane_host')} | {r.get('tail') or '--'} | "
                 f"{miss_s} | {verdict} | {r.get('authority')} |\n")
    tailnote = ""
    fatal = [r for r in report["lanes"] if r.get("loss_mode")
             and r.get("copy_verdict", r["verdict"]) in ("stalled", "behind_1d")]
    if fatal:
        tailnote = "\n## Lanes where a missed day cannot be recovered\n\n"
        for r in fatal:
            tailnote += f"- `{r['lane']}`: {r['loss_mode']}\n"
    why = [r for r in report["lanes"] if r.get("why")]
    if report.get("hosts_down"):
        tailnote += ("\n## Hosts that stopped reporting\n\n"
                     "These lanes cannot be certified here and the machine that "
                     "is supposed to collect them has not written a heartbeat "
                     f"for more than {report.get('host_down_hours')}h. Until it "
                     "comes back the numbers below are this machine's stale "
                     "copies, not the company's data.\n\n")
        for host in report["hosts_down"]:
            h = (report.get("hosts") or {}).get(host) or {}
            age = h.get("age_h")
            tailnote += (f"- `{host}`: last seen {h.get('last_seen')}"
                         + (f" ({age}h ago)" if age is not None else "")
                         + f" -- holding back {', '.join(h.get('lanes_unverifiable') or [])}\n")
    if why:
        tailnote += ("\n## Why some lanes cannot be certified here\n\n"
                     "A status envelope is committed by whichever machine ran the "
                     "leg, and every machine also keeps its own gitignored copy of "
                     "the data. Neither names its writer, so a tail that reads "
                     "late can be a dead lane or a stale copy of a live one.\n\n")
        for r in why:
            tailnote += f"- `{r['lane']}`: {r['why']}\n"
    return head + cols + body + tailnote


# ---------------------------------------------------------------- selftest

def selftest():
    """Hermetic legs: no network, tmpdir fixtures, calendar is synthetic."""
    import tempfile
    days = ["2026-10-20", "2026-10-21", "2026-10-22", "2026-10-23",
            "2026-10-26", "2026-10-27", "2026-10-28", "2026-10-29"]
    now = dt.datetime(2026, 10, 29, 20, 0)     # after the close on 10-29

    def run_lane(spec, root):
        rep = audit(days, now, lanes=[spec], root=root)
        return rep["lanes"][0]

    # L1 the reference boundary: before 15:30 today is not expected yet
    v_pre, _, exp_pre = judge(None, days, dt.datetime(2026, 10, 29, 9, 0))
    assert exp_pre == "2026-10-28", exp_pre
    print("[PASS] L1 before 15:30 today's bar is not expected", flush=True)

    # L2 day_files: newest file wins, and the count is the file count
    with tempfile.TemporaryDirectory() as td:
        d = os.path.join(td, "heat")
        os.makedirs(d)
        for name in ("20261027.json", "20261020.json", "notes.txt"):
            open(os.path.join(d, name), "w").close()
        row = run_lane({"lane": "heat", "kind": "day_files", "dir": "heat"}, td)
        assert row["tail"] == "2026-10-27", row
        assert row["missing_days"] == ["2026-10-28", "2026-10-29"], row
        # no host is named for this fixture, so the reading survives as
        # copy_verdict and the verdict itself refuses to certify it
        assert row["verdict"] == "unverifiable", row
        assert row["copy_verdict"] == "stalled", row
        print("[PASS] L2 day_files tail + 2 missing official days", flush=True)

    # L3 a lane with no artifact is absent, never zero/in_sync
    with tempfile.TemporaryDirectory() as td:
        row = run_lane({"lane": "x", "kind": "day_files", "dir": "nope"}, td)
        assert row["tail"] is None and row["verdict"] == "absent", row
        row = run_lane({"lane": "y", "kind": "status", "path": "nope.json",
                        "key": "cutoff"}, td)
        assert row["verdict"] == "absent" and row.get("missing_artifact"), row
        print("[PASS] L3 absent lanes read absent (never 0 / never in_sync)",
              flush=True)

    # L4 in_sync, today_pending, behind_1d, stalled are four distinct verdicts
    cases = [("2026-10-29", "in_sync", 0),
             ("2026-10-28", "today_pending", 1),
             ("2026-10-27", "stalled", 2),
             ("2026-10-20", "stalled", 7)]
    for tail, want, n in cases:
        v, miss, _ = judge(tail, days, now)
        assert v == want, (tail, v, want)
        assert len(miss) == n, (tail, miss)
        print(f"[PASS] L4 {tail} -> {want} ({n} missing)", flush=True)

    # L4b behind_1d only exists when the expectation is an OLDER day: a
    # Monday-morning run cannot expect Monday's bar, so one day behind is 10-23
    v, miss, exp = judge("2026-10-22", days, dt.datetime(2026, 10, 26, 10, 0))
    assert (v, miss, exp) == ("behind_1d", ["2026-10-23"], "2026-10-23"), (v, miss, exp)
    print("[PASS] L4b one older day behind -> behind_1d (not today_pending)", flush=True)

    # L5 four minutes past the close today IS expected (the 15:30 line)
    v, miss, exp = judge("2026-10-28", days, dt.datetime(2026, 10, 29, 15, 34))
    assert exp == "2026-10-29" and v == "today_pending" and \
        miss == ["2026-10-29"], (exp, v, miss)
    print("[PASS] L5 15:34 today is expected -> today_pending", flush=True)

    # L6 status lanes read the dotted key and refuse a prose value
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "s.json")
        json.dump({"panel": {"cutoff": "2026-10-28"}, "note": "x"}, open(p, "w"))
        row = run_lane({"lane": "mf", "kind": "status", "path": "s.json",
                        "key": "panel.cutoff"}, td)
        assert row["tail"] == "2026-10-28", row
        assert row["copy_verdict"] == "today_pending", row
        # now the envelope names its writer AND the writer is the lane host
        json.dump({"panel": {"cutoff": "2026-10-28"}, "machine": "bm-a"},
                  open(p, "w"))
        row = run_lane({"lane": "mf", "kind": "status", "path": "s.json",
                        "key": "panel.cutoff", "owner": "bm-a"}, td)
        assert row["authority"] == "host_envelope" and row["auditable"], row
        assert row["verdict"] == "today_pending", row
        print("[PASS] L6b an envelope that names its own host is certifiable",
              flush=True)
        json.dump({"panel": {"cutoff": "panel 2026-10-14 (bars due)"}}, open(p, "w"))
        row = run_lane({"lane": "mf", "kind": "status", "path": "s.json",
                        "key": "panel.cutoff"}, td)
        assert row["tail"] is None and row["verdict"] == "absent", row
        print("[PASS] L6 status lane reads dates, refuses prose", flush=True)

    # L7 zt_days: the tail is the newest across faces, per-face tails kept
    with tempfile.TemporaryDirectory() as td:
        json.dump({"zt": ["2026-10-20", "2026-10-21"],
                   "strong": ["2026-10-22"]},
                  open(os.path.join(td, "cd.json"), "w"))
        row = run_lane({"lane": "zt", "kind": "zt_days", "path": "cd.json"}, td)
        assert row["tail"] == "2026-10-22" and row["n_missing"] == 5, row
        assert row["faces"] == {"zt": "2026-10-21", "strong": "2026-10-22"}, row
        print("[PASS] L7 zt_days tail is newest across faces", flush=True)

    # L8 external lane: cited verdict travels, and disagreement is printed
    with tempfile.TemporaryDirectory() as td:
        json.dump({"panel": {"effective_cutoff": "2026-10-20"},
                   "verdict": "in_sync"}, open(os.path.join(td, "e.json"), "w"))
        row = run_lane({"lane": "etf", "kind": "external", "path": "e.json",
                        "tail_key": "panel.effective_cutoff",
                        "verdict_key": "verdict"}, td)
        assert row["copy_verdict"] == "stalled" and row["cited_verdict"] == "in_sync"
        assert row["face_disagreement"] is True, row
        print("[PASS] L8 external lane flags a disagreeing face", flush=True)

    # L9 one unreadable lane must not take the board down
    with tempfile.TemporaryDirectory() as td:
        open(os.path.join(td, "bad.json"), "w").write("{not json")
        rep = audit(days, now, lanes=[
            {"lane": "bad", "kind": "status", "path": "bad.json", "key": "x"},
            {"lane": "good", "kind": "status", "path": "bad.json", "key": "x"}],
            root=td)
        assert rep["counts"].get("unreadable") == 2, rep["counts"]
        assert rep["verdict"] == "attention"
        print("[PASS] L9 unreadable lanes are reported, not raised", flush=True)

    # L9b a closed face is retired, not late -- and it may not enter `worst`
    with tempfile.TemporaryDirectory() as td:
        json.dump({"panel": {"max_collected": "2026-09-30"}, "machine": "bm-a"},
                  open(os.path.join(td, "o.json"), "w"))
        rep = audit(days, now, root=td, lanes=[
            {"lane": "options", "kind": "status", "path": "o.json",
             "key": "panel.max_collected", "owner": "bm-a",
             "retired": "O-20261009-1105 closed this face"},
            {"lane": "live", "kind": "status", "path": "o.json",
             "key": "panel.max_collected", "owner": "bm-a"}])
        _o = {r["lane"]: r for r in rep["lanes"]}
        assert _o["options"]["verdict"] == "retired", _o["options"]
        assert _o["options"]["copy_verdict"] == "stalled", _o["options"]
        assert rep["worst"] == "live", rep["worst"]
        assert rep["counts"] == {"retired": 1, "stalled": 1}, rep["counts"]
        print("[PASS] L9b a retired face is not counted as a stall", flush=True)

    # L10 the markdown carries every lane and the fatal-loss section
    rep = {"as_of": "2026-10-29T20:00:00", "close_accept_time": "15:30",
           "expected_last_official_day": "2026-10-29", "calendar_days": 8,
           "verdict": "attention", "counts": {"stalled": 1}, "n_lanes": 1,
           "worst": "heat",
           "lanes": [{"lane": "heat", "lane_host": "bm-a", "owner": "bm-a",
                      "tail": "2026-10-20",
                      "missing_days": ["2026-10-21"], "verdict": "stalled",
                      "authority": "host_copy",
                      "loss_mode": "no history upstream"}]}
    md = render_md(rep)
    assert "| `heat` | bm-a | 2026-10-20 |" in md and "cannot be recovered" in md
    print("[PASS] L10 markdown names every lane + loss mode", flush=True)

    # L11 a lane nobody can certify whose host stopped reporting is an outage
    # with a name on it, not an open question (2026-10-30: seven unverifiable
    # lanes and no culprit printed -- the reader could not act on the board)
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "m"))
        json.dump({"clock_read": "2026-10-29T04:18:13+08:00"},
                  open(os.path.join(td, "m", "bm-b.json"), "w"))
        json.dump({"clock_read": "2026-10-29T19:50:00+08:00"},
                  open(os.path.join(td, "m", "bm-c.json"), "w"))
        json.dump({"panel": {"cut": "2026-10-20"}, "machine": "bm-a"},
                  open(os.path.join(td, "mf.json"), "w"))
        json.dump({"panel": {"cut": "2026-10-29"}, "machine": "bm-c"},
                  open(os.path.join(td, "ok.json"), "w"))
        rep = audit(days, now, root=td, machines_dir=os.path.join(td, "m"),
                    lanes=[
                        {"lane": "moneyflow", "kind": "status",
                         "path": "mf.json", "key": "panel.cut", "owner": "bm-b"},
                        {"lane": "marks", "kind": "status", "path": "ok.json",
                         "key": "panel.cut", "owner": "bm-c"}])
        _o = {r["lane"]: r for r in rep["lanes"]}
        assert _o["moneyflow"]["verdict"] == "unverifiable", _o["moneyflow"]
        assert _o["moneyflow"]["host_alive"] is False, _o["moneyflow"]
        assert _o["moneyflow"]["host_age_h"] > HOST_DOWN_H, _o["moneyflow"]
        assert _o["marks"]["host_alive"] is True, _o["marks"]
        assert rep["hosts_down"] == ["bm-b"], rep["hosts_down"]
        assert rep["lanes_hostage"] == ["moneyflow"], rep["lanes_hostage"]
        assert rep["verdict"] == "host_down", rep["verdict"]
        md = render_md(rep)
        assert "`bm-b`" in md and "holding back moneyflow" in md, md
        print("[PASS] L11 a dead host is named and its hostage lanes listed",
              flush=True)

    # L12 an absent heartbeat is unknown, never "dead" (fail-open, no libel)
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "m"))
        json.dump({"panel": {"cut": "2026-10-20"}, "machine": "bm-a"},
                  open(os.path.join(td, "mf.json"), "w"))
        rep = audit(days, now, root=td, machines_dir=os.path.join(td, "m"),
                    lanes=[{"lane": "heat", "kind": "status", "path": "mf.json",
                            "key": "panel.cut", "owner": "bm-b"}])
        r = rep["lanes"][0]
        assert r["verdict"] == "unverifiable" and r["host_alive"] is None, r
        assert rep["hosts_down"] == [] and rep["verdict"] == "uncertified", rep
        print("[PASS] L12 no heartbeat file reads unknown, not dead", flush=True)

    # L13 a DECLARED takeover is the authority; an anonymous foreign writer
    # is not (T25, r1161: the heat rows are machine-local, so the only thing a
    # takeover can move is the declaration -- and that must be honoured)
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "m"))
        json.dump({"heartbeat_epoch_utc": int(dt.datetime.now().timestamp())},
                  open(os.path.join(td, "m", "bm-a.json"), "w"))
        spec = [{"lane": "heat", "kind": "status", "path": "h.json",
                 "key": "latest_snapshot", "owner": "bm-b"}]
        json.dump({"machine": "bm-a", "latest_snapshot": "2026-10-20",
                   "authority": {"lane_owner": "bm-b", "writer_machine": "bm-a",
                                 "data_face_machine": "bm-a",
                                 "declared_takeover": True,
                                 "took_over_by": "bm-a"}},
                  open(os.path.join(td, "h.json"), "w"))
        r = audit(days, now, root=td, machines_dir=os.path.join(td, "m"),
                  lanes=spec)["lanes"][0]
        assert r["authority"] == "declared_takeover", r
        assert r["verdict"] != "unverifiable", r
        assert r["data_face_machine"] == "bm-a", r
        assert r["owner"] == "bm-b" and r["lane_host"] == "bm-b", r
        json.dump({"machine": "bm-a", "latest_snapshot": "2026-10-20"},
                  open(os.path.join(td, "h.json"), "w"))
        r2 = audit(days, now, root=td, machines_dir=os.path.join(td, "m"),
                   lanes=spec)["lanes"][0]
        assert r2["authority"] == "non_host_envelope", r2
        assert r2["verdict"] == "unverifiable", r2
        print("[PASS] L13 a declared takeover is auditable, an undeclared "
              "foreign envelope is not", flush=True)

    print("selftest: 13/13 PASS", flush=True)
    return 0


def run(now=None, allow_network=False):
    days = load_calendar(CAL_PATH)
    if not days:
        print("MECHANISM FAIL: no official calendar at "
              f"{os.path.relpath(CAL_PATH, ROOT)}", flush=True)
        return 2
    now = now or dt.datetime.now()
    report = audit(days, now)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    tmp = OUT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT_PATH)
    os.makedirs(os.path.dirname(MD_PATH), exist_ok=True)
    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write(render_md(report))
    for r in report["lanes"]:
        print(f"{r['verdict']:>14}  {r['lane']:<14} tail={r.get('tail') or '--':<10} "
              f"missing={r.get('n_missing', 0)}", flush=True)
    print(f"verdict={report['verdict']} counts={report['counts']} "
          f"worst={report['worst']}", flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "selftest", "show"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "show":
        if not os.path.exists(OUT_PATH):
            print("no board yet -- run it first", flush=True)
            return 2
        doc = read_json(OUT_PATH)
        print(json.dumps({k: doc[k] for k in
                          ("as_of", "verdict", "counts", "worst", "expected_last_official_day")},
                         ensure_ascii=False, indent=1))
        return 0
    return run()


if __name__ == "__main__":
    sys.exit(main())