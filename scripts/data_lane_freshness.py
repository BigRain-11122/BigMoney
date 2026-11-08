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
import fnmatch
import importlib
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
# D-20261108-14: the certification line (2h) and the silence alarm (24h) answer
# different questions. 2h = "can this host vouch for the row it wrote?"; 24h =
# "has the owner stopped reporting at all?" -- reported separately.
HOST_SILENT_H = 24.0

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
    {"lane": "lhb_inst", "dept": "data", "owner": "bm-c",
     "writer": "update_lhb_inst", "kind": "status",
     "path": "results/lhb_inst_update_status.json", "key": "cutoff",
     "fatal_loss": "vendor re-serves the range on later pulls, so a missed month is recoverable by moving FIRST_DATE; the panel is append-only by key"},
    {"lane": "futures", "dept": "data", "owner": "bm-a", "writer": "update_futures",
     "kind": "status", "path": "results/futures_update_status.json", "key": "data_cutoff",
     "panel_csv": {"dir": "data/futures_daily", "pattern": "*.csv"}},
    {"lane": "repo", "dept": "data", "owner": "bm-a", "writer": "update_repo",
     "kind": "status", "path": "results/repo_update_status.json", "key": "data_cutoff",
     "panel_csv": {"dir": "data/repo_daily", "pattern": "*.csv"}},
    {"lane": "moneyflow", "dept": "data", "owner": "bm-a",
     "writer": "update_moneyflow", "kind": "status",
     "path": "results/moneyflow_update_status.json", "key": "panel.cutoff",
     "panel_csv": {"dir": "data/moneyflow/per", "pattern": "*.csv"}},
    {"lane": "astock_daily", "dept": "data", "owner": "bm-b",
     "writer": "update_astock_daily", "kind": "status",
     "path": "results/astock_daily_update_status.json", "key": "panel.cutoff",
     "panel_csv": {"dir": "data/astock_daily/per", "pattern": "*.csv"}},
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
    # r1266: this row said `writer: None`, so the board's hostage section told
    # readers "the row reads another face rather than a collector of its own, so
    # there is nothing to reassign" about a lane whose collector shipped a
    # declared-takeover path back at r1101. A capability the board cannot see is
    # a sentence telling the reader to give up. The collector now names itself.
    {"lane": "marks", "dept": "data", "owner": "bm-b",
     "writer": "update_intraday_marks",
     "kind": "external",
     "path": "results/marks_coverage.json", "tail_key": "last_captured",
     "fatal_loss": "an intraday tick capture: a day with no marks file cannot be "
                   "rebuilt by any machine -- the file is append-only and the "
                   "ticks it would have held are gone",
     "audited_by": "marks_coverage (the paper marks lane keeps its own hole "
                   "counters; this row reads its last captured day and its "
                   "per-hole causes)"},
]


# --------------------------------------------- coverage: the map, not the list
# D-20261108-14 (group, 12:00 batch): the coverage contract is
# `config/lane_hosts.json` UNION the lanes this board already reads. Measured
# 2026-11-08: the map declared nine lanes owned by a machine that had been
# silent for 194h, and none of them had a row here -- so "the lane produces
# nothing" and "nobody is looking at the lane" printed as the same blank space.
# A lane declared by the map but missing from this file is now a ROW, not a
# silent omission: the map says it exists, so the board has to say either what
# it reads or that it has no reader for it.
#
# `window_trading_days` marks a lane whose own contract is a rolling window
# (sina money flow keeps a rolling 250-trading-day window and refreshes only
# when the tail is 20 days stale). Judging such a lane against "every official
# day since the tail" would print a permanent false alarm; the window is the
# lane's declared promise, so the window is the measurement (r1201 class: judge
# a lane by its own contract, never by another lane's).
WRITER_FACES = [
    {"lane": "ah_panel", "dept": "data", "writer": "ah_panel_puller",
     "kind": "status", "path": "results/ah_panel_status.json", "key": "cutoff",
     "panel_csv": {"dir": "data/ah_panel/per", "pattern": "*.csv"},
     "machine_local": True,
     "fatal_loss": "a premium pair day is quotable only from that day's closes"},
    {"lane": "minute_feed", "dept": "data", "writer": "update_minute_feed",
     "kind": "panel_csv", "dir": "data/minute_feed", "pattern": "*.csv",
     "machine_local": True,
     "fatal_loss": "a minute bar outside the source's rolling window is gone"},
    {"lane": "sina_mf", "dept": "data", "writer": "update_sina_mf",
     "kind": "status", "path": "results/sina_mf_update_status.json",
     "key": "panel.cutoff", "window_trading_days": 20,
     "window_basis": "the collector's own no-op rule: it refreshes only when "
                     "the panel tail is more than 20 trading days stale"},
    {"lane": "ths_panel", "dept": "data", "writer": "update_ths_panel",
     "kind": "status", "path": "data/ths_ggzjl/status.json", "key": "cutoff"},
]


def declared_lane_hosts(root=ROOT):
    """{writer: host} exactly as the collector family resolves it (single source)."""
    try:
        with open(os.path.join(root, "config", "lane_hosts.json"),
                  encoding="utf-8") as f:
            doc = json.load(f)
    except Exception:                                   # noqa: BLE001
        return {}
    hosts = doc.get("lane_hosts") if isinstance(doc, dict) else None
    return hosts if isinstance(hosts, dict) else {}


def board_lanes(root=ROOT):
    """LANES + every writer the map declares that this file still has no row for.

    Returned rows carry `origin`: "registry" for the hand-written entries and
    "lane_hosts_union" for the map-derived ones, so a reader can tell a lane
    somebody measured from a lane the coverage rule just caught. An unmapped
    writer becomes an `undeclared` row with its own verdict -- never dropped.
    """
    out = [dict(s) for s in LANES]
    covered = {s.get("writer") for s in LANES + PERIOD_LANES if s.get("writer")}
    by_writer = {s["writer"]: s for s in WRITER_FACES}
    for writer in sorted(declared_lane_hosts(root)):
        if writer in covered:
            continue
        spec = by_writer.get(writer)
        if spec is None:
            out.append({"lane": writer, "writer": writer, "kind": "undeclared",
                        "origin": "lane_hosts_union"})
        else:
            out.append(dict(spec, origin="lane_hosts_union"))
    for s in out:
        s.setdefault("origin", "registry")
    return out


# ------------------------------------------------------------ takeover face
# A frozen lane is stuck in one of two ways, and they call for opposite
# responses: "wait for the owner to come back" and "no machine is allowed to
# move this lane at all". The second one is a decision, not patience -- so the
# board has to say which it is looking at instead of printing one word for
# both.
#
# Capability is read out of the writer's own source: every declared-takeover
# implementation prints this phrase at the moment it takes over, so a lane
# whose writer cannot print it has no takeover path. A list kept beside the
# code would drift the day somebody transplants the mechanism, and then the
# board would keep telling readers to wait for a lane two machines could
# already move.
TAKEOVER_MARKER = "TAKEOVER: declared stale takeover of"


def takeover_capable(writer, root=ROOT):
    """True when this lane's own writer can declare a stand-in."""
    if not writer:
        return False
    path = os.path.join(root, "scripts", writer + ".py")
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return TAKEOVER_MARKER in fh.read()
    except OSError:
        return False


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


def _panel_names(dirpath, pattern="*.csv"):
    """Sorted file names in a panel dir, or None when the dir is absent."""
    if not os.path.isdir(dirpath):
        return None
    return sorted(n for n in os.listdir(dirpath) if fnmatch.fnmatch(n, pattern))


def _tail_day(p):
    """Last date in a CSV whose first column is YYYY-MM-DD -> date|None."""
    try:
        with open(p, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(max(0, size - 4096))
            tail = f.read().decode("utf-8", "replace").strip().splitlines()
    except OSError:
        return None
    for line in reversed(tail):
        day = _as_date(line.split(",")[0])
        if day:
            return day
    return None


def _tails(dirpath, names):
    """{file name: last date} for the readable files in `names`."""
    out = {}
    for name in names:
        day = _tail_day(os.path.join(dirpath, name))
        if day:
            out[name] = day
    return out


def panel_tail_csv(dirpath, pattern="*.csv", max_files=40):
    """Newest YYYY-MM-DD first column across a CSV panel -> (date|None, info).

    r1255: a status envelope is a committed file, so a rebase/branch switch can
    restore an OLDER copy of it while the panel on disk is newer. The panel is
    the measurement (this module's own rule); the envelope is a report about it.
    Cheap by design: 9-11 small CSVs, last line only.

    r1259: the same cross-check now runs on the per-symbol panels (moneyflow and
    astock_daily hold 5,222 files each). Reading all of them every few minutes is
    not a measurement, it is a disk sweep -- so above max_files the panel is read
    through an evenly spaced deterministic sample and `sampled` is published
    beside the number. A sample can miss one laggard symbol; it cannot miss a
    panel that stopped a month ago, which is the case this face exists to catch.
    """
    names = _panel_names(dirpath, pattern)
    if names is None:
        return None, {"files": 0}
    total = len(names)
    sampled = total > max_files
    if sampled:
        step = (total - 1) / float(max_files - 1) if max_files > 1 else 0.0
        idx, seen = [], set()
        for i in range(max_files):
            j = int(round(i * step))
            if j not in seen:
                seen.add(j)
                idx.append(j)
        names = [names[j] for j in idx]
    tails = _tails(dirpath, names)
    if not tails:
        return None, {"files": total, "sampled": sampled,
                      "per_file": 0}
    info = {"files": total, "per_file": len(tails)}
    if sampled:
        info["sampled"] = True
    return max(tails.values()), info


def panel_tail_csv_full(dirpath, pattern="*.csv", laggard_cap=25):
    """Every file of a panel, no sample -> (date|None, info with laggards).

    r1261: `panel_tail_csv` makes a claim about a 5,222-file panel by reading
    forty of them. That is the right cost for a board that refreshes every few
    minutes, but it is a claim, not a measurement -- and the only way to know
    whether a one-symbol laggard exists at all is to read the rest. This does,
    and it names the symbols whose last bar sits behind the panel's newest one,
    because "the panel is current" and "every symbol in it is current" are two
    different sentences and only this one can tell them apart.
    """
    names = _panel_names(dirpath, pattern)
    if names is None:
        return None, {"files": 0}
    tails = _tails(dirpath, names)
    if not tails:
        return None, {"files": len(names), "per_file": 0}
    newest = max(tails.values())
    behind = sorted(n for n, d in tails.items() if d < newest)
    return newest, {"files": len(names), "per_file": len(tails),
                    "unread": len(names) - len(tails),
                    "n_laggards": len(behind),
                    "laggards": behind[:laggard_cap],
                    "laggards_truncated": len(behind) > laggard_cap}


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
    specs = list(lanes) if lanes is not None else board_lanes(root)
    for spec in specs:
        row = {"lane": spec["lane"], "dept": spec.get("dept"),
               "owner": spec.get("owner"), "writer": spec.get("writer"),
               "kind": spec["kind"], "origin": spec.get("origin", "registry")}
        if spec.get("window_trading_days"):
            row["window_trading_days"] = spec["window_trading_days"]
            row["window_basis"] = spec.get("window_basis")
        if spec["kind"] == "undeclared":
            # the map declares this lane and this board has no reader for it:
            # that is a coverage gap with a name, not an empty space
            row.update({"tail": None, "expected": None, "missing_days": [],
                        "n_missing": 0, "verdict": "unmeasured",
                        "why": ("declared in config/lane_hosts.json but this "
                                "board has no reader for the lane -- nobody is "
                                "measuring it (D-20261108-14 union rule)")})
            rows.append(row)
            continue
        tail, extra = None, {}
        try:
            if spec["kind"] == "day_files":
                tail, extra = tail_day_files(os.path.join(root, spec["dir"]))
            elif spec["kind"] == "panel_csv":
                # the panel IS the measurement here: a status envelope whose
                # only date field is a run timestamp (minute_feed publishes
                # last_success_ts) cannot say which bar day exists
                tail, extra = panel_tail_csv(
                    os.path.join(root, spec["dir"]),
                    spec.get("pattern", "*.csv"))
                extra["tail_source"] = "panel_csv"
                # a panel on THIS disk is this machine's own archive, so the
                # reading is attributable to `here` even though no envelope says
                # it -- the data is the evidence
                if spec.get("machine_local"):
                    extra["reported_by"] = here
                    extra["data_scope"] = "machine_local"
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
                        # r1256: an envelope that carries the canonical authority
                        # block already names its writer there, so an absent
                        # top-level reporter key must not read as "somebody
                        # anonymous wrote this". Live 2026-11-07: astock_daily
                        # held authority.took_over_by=bm-a and still printed
                        # `unverifiable / the envelope does not name the machine
                        # whose data it describes`, on a panel this host was
                        # building at that minute.
                        if extra["reported_by"] is None and isinstance(
                                auth_blk.get("writer_machine"), str):
                            extra["reported_by"] = auth_blk["writer_machine"]
                    # r1257: a stand-in recorded ONLY in the older top-level
                    # `takeover{}` shape is a declaration no reader can see.
                    # Live 2026-11-07: update_zt_pool had published
                    # `takeover{by:bm-a}` every run since 10-29 and this board
                    # still printed the lane `unverifiable` for nine days. The
                    # board must name that half-shape instead of shrugging at it.
                    raw_tk = doc.get("takeover")
                    if (isinstance(raw_tk, dict) and raw_tk.get("by")
                            and not (isinstance(auth_blk, dict)
                                     and auth_blk.get("took_over_by"))):
                        extra["unread_takeover_by"] = raw_tk["by"]
                        extra["unread_takeover_lag"] = (
                            "the envelope declares a stand-in in `takeover{}` "
                            "but publishes no `authority.took_over_by`; "
                            "readers cannot see it (writer must call "
                            "update_etf_daily.authority_block)")
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
                        # r1266: when the auditing face keeps a per-hole cause
                        # table, carry it. "6 days missing" is one number for
                        # two very different histories -- days when a stand-in
                        # was awake inside the window and did not capture, and
                        # days when nobody could have.
                        if isinstance(doc.get("holes_by_cause"), dict):
                            extra["holes_by_cause"] = doc["holes_by_cause"]
                else:
                    extra["missing_artifact"] = spec["path"]
                # r1255: the envelope is a report ABOUT the panel, so when this
                # host can read the panel itself the panel wins. A committed
                # envelope restored by a rebase is how a healthy lane reads
                # "stalled" (live 2026-11-07: futures envelope said 11-05 while
                # data/futures_daily held 11-06).
                if spec.get("panel_csv") and tail is not None:
                    spec_dir = spec["panel_csv"]
                    ptail, pinfo = panel_tail_csv(
                        os.path.join(root, spec_dir["dir"]),
                        spec_dir.get("pattern", "*.csv"))
                    extra["panel_read"] = pinfo
                    if ptail:
                        extra["panel_tail"] = ptail
                        if ptail != tail:
                            extra["envelope_tail"] = tail
                            extra["envelope_stale"] = ptail > tail
                            lag = [d for d in days if tail < d <= ptail]
                            extra["envelope_lag_until"] = ptail
                            # a panel can hold a bar the calendar has not been
                            # extended to; count only days the calendar knows,
                            # and say so instead of printing a silent 0
                            beyond = bool(days) and ptail > max(days)
                            extra["envelope_lag_days"] = (
                                len(lag) if not beyond else None)
                            extra["envelope_lag_beyond_calendar"] = beyond
                        if ptail > tail:
                            tail = ptail   # the panel is the measurement
                        elif ptail < tail:
                            # r1259: the opposite gap has to be said out loud
                            # too. The envelope is what some machine claims; the
                            # panel is what is actually on this disk. A lane
                            # whose envelope names a day the local copy has not
                            # reached is not current here, whatever the envelope
                            # says (live: moneyflow envelope 2026-10-19 against a
                            # copy holding 2026-10-13).
                            extra["panel_behind_envelope"] = tail
                            back = [d for d in days if ptail < d <= tail]
                            extra["panel_behind_days"] = len(back)
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
        # a rolling-window lane is late only past its own declared window; inside
        # it the gap is the design, and the number still travels (days_behind)
        win = spec.get("window_trading_days")
        if win and verdict in ("behind_1d", "stalled") and len(missing) <= win:
            row["verdict"] = "in_sync"
            row["within_window"] = True
            row["days_behind"] = len(missing)
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
        spec = next((s for s in specs if s["lane"] == r["lane"]), {})
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
        elif spec.get("machine_local"):
            # same rule for a lane whose data lives in a local panel dir: the
            # panel is the machine's own archive, so it is a host copy on the
            # host and somebody else's copy anywhere else
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
        r["takeover_capable"] = takeover_capable(spec.get("writer"), root)
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
        if not r["auditable"] and r["verdict"] not in ("absent", "unreadable",
                                                     "unmeasured"):
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
            if r.get("unread_takeover_by"):
                # r1257: put the actionable half first -- "who declared what,
                # and why you cannot read it" beats "somebody wrote this".
                r["why"] = (
                    f"{r['unread_takeover_by']} declared a stand-in in "
                    "`takeover{}` but published no `authority.took_over_by` "
                    f"-- {r['why']}")
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
    # D-20261108-14: "the lane stopped producing" and "the owner stopped
    # reporting" are two different alarms and must not collapse into one flag.
    # A lane can be in_sync while its owner is silent (the file on this disk was
    # written days ago and still covers the window), and a host can be silent
    # with every lane still fresh (it wrote everything before going quiet). So
    # silence is its own block, its own window (24h, not the 2h certification
    # line), and its own verdict word.
    hosts_silent = []
    for h in hosts.values():
        if not h["lanes"]:
            continue
        age = h.get("age_h")
        silent = age is not None and age > HOST_SILENT_H
        h["silent"] = silent
        if silent:
            h["silent_lanes"] = sorted(h["lanes"])
            hosts_silent.append(h["host"])
    hosts_silent.sort()
    # a lane nobody can certify AND whose host stopped reporting is not an open
    # question any more -- it is an outage with a name on it
    hosts_down = sorted(h["host"] for h in hosts.values()
                        if h["alive"] is False and h["lanes_unverifiable"])
    lanes_hostage = sorted(r["lane"] for r in rows
                           if r["verdict"] == "unverifiable"
                           and r.get("host_alive") is False)
    # the harder half of the same question: unverifiable + host silent + the
    # writer has no way to declare a stand-in. Waiting cannot fix these.
    frozen = sorted(r["lane"] for r in rows
                    if r["verdict"] == "unverifiable"
                    and r.get("host_alive") is False
                    and not r.get("takeover_capable"))
    # a board that reads green because it could not certify anything would be
    # the very failure it exists to catch: 'uncertified' is its own verdict.
    verdict = ("attention" if stale else
               ("host_down" if hosts_down else
                ("uncertified" if uncertified else "all_fresh")))
    live = [r for r in rows if r["verdict"] != "retired"]
    # "worst" must be a lane that is actually late: a rolling-window lane can
    # carry nine missing calendar days by design and still be in_sync
    late = [r for r in live if r["verdict"] != "in_sync"]
    worst_row = max(late, key=lambda r: r.get("n_missing", 0)) if late else None
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
        "hosts_silent": hosts_silent,
        "host_silent_hours": HOST_SILENT_H,
        "silence_verdict": ("hosts_silent" if hosts_silent else "none"),
        "unmeasured_lanes": [r["lane"] for r in rows
                             if r["verdict"] == "unmeasured"],
        "coverage": {
            "registry_lanes": len([r for r in rows
                                   if r.get("origin") == "registry"]),
            "lane_hosts_union_lanes": len([r for r in rows
                                           if r.get("origin")
                                           == "lane_hosts_union"]),
            "declared_writers": len(declared_lane_hosts(root)),
            "rule": "config/lane_hosts.json owners UNION the lanes this board "
                    "reads; a declared lane with no reader is `unmeasured`, "
                    "never absent (D-20261108-14)",
        },
        "lanes_hostage": lanes_hostage,
        "frozen_without_takeover": frozen,
        "host_down_hours": HOST_DOWN_H,
        "worst": (worst_row["lane"] if (stale or uncertified) and worst_row
                  and worst_row.get("n_missing") else None),
        "disk": disk_face(rows, hosts),
        "note": ("Descriptive face, one rule per lane: the official calendar is "
                 "the reference, the lane's own tail is the measurement. A lane "
                 "with no artifact reads absent, never 0. A lane whose only "
                 "evidence was written by another machine's copy reads "
                 "unverifiable -- `copy_verdict` keeps what that copy said."),
        "lanes": rows,
    }


# ------------------------------------------------------- whose disk (r1162)
AUTHORITY_LABEL = {
    "host_envelope": "宿主自己写的封套",
    "host_copy": "宿主本机副本",
    "declared_takeover": "申报接管",
    "non_host_envelope": "他机写的封套",
    "non_host_copy": "他机本地副本",
    "unattributed": "无主封套",
}
HERE_AUTHORITY = ("host_envelope", "host_copy")


def _data_face(r):
    """The machine whose DISK holds this lane's rows (r1162).

    A declared takeover names its own data face; otherwise the lane host owns
    the data dir. A foreign machine that merely wrote the envelope did not move
    anybody's rows, so `reported_by` is the last resort, not the first."""
    return (r.get("data_face_machine") or r.get("lane_host")
            or r.get("reported_by") or "unknown")


def disk_face(rows, hosts=None, here=None):
    """Whose disk each lane's number lives on, in one sentence (r1162).

    The board can already say a reading is not auditable HERE -- but that is a
    fact about our copy, not about the company's data, and a reader who stops
    there learns nothing actionable. The next sentence is the useful one: the
    rows are on machine X's disk, X is (or is not) still reporting, and how many
    of the lanes that ARE on this disk we can actually vouch for.

    Two different questions, kept apart: `on this disk` (where the bytes are)
    and `auditable` (whether anybody signed for them). A lane whose envelope is
    unsigned but whose bytes sit here is on our disk and still uncertified --
    collapsing the two is how "seven lanes unverifiable" became unreadable.
    Retired faces are excluded: a closed lane owes nobody a bar.
    """
    hosts = hosts or {}
    here = here if here is not None else _machine_id()
    live = [r for r in (rows or ()) if r.get("verdict") != "retired"]
    away = [r for r in live if _data_face(r) != here
            and r.get("authority") not in HERE_AUTHORITY]
    groups = {}
    for r in away:
        groups.setdefault(_data_face(r), []).append(r.get("lane"))
    out_groups = []
    for m, lanes in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        h = hosts.get(m) or {}
        out_groups.append({"machine": m, "lanes": sorted(lanes),
                           "n": len(lanes), "alive": h.get("alive"),
                           "age_h": h.get("age_h"),
                           "last_seen": h.get("last_seen")})
    n_offhost = sum(g["n"] for g in out_groups)
    on_here = [r for r in live if r not in away]
    n_here = len(on_here)
    n_aud = len([r for r in on_here if r.get("auditable")])
    n_unsigned = len([r for r in on_here if not r.get("auditable")])
    if not live:
        sentence = "本机没有任何在役车道的读数——板面为空，归属无从谈起。"
    elif not out_groups:
        sentence = (f"{len(live)} 条在役车道的数字全都落在本机盘上，"
                    f"其中 {n_aud} 条有署名可核实"
                    + (f"、{n_unsigned} 条没有署名" if n_unsigned else "")
                    + "。")
    else:
        parts = []
        for g in out_groups:
            if g["machine"] == "unknown":
                parts.append(f"{g['n']} 条没有谁署名")
            elif g["alive"] is False:
                age = (f"{g['age_h']}h 未报到" if g["age_h"] is not None
                       else "无心跳")
                parts.append(f"{g['n']} 条在 {g['machine']} 的盘上（{age}）")
            else:
                parts.append(f"{g['n']} 条在 {g['machine']} 的盘上（心跳 {g['age_h']}h 前）"
                             if g.get("age_h") is not None
                             else f"{g['n']} 条在 {g['machine']} 的盘上")
        sentence = (f"{len(live)} 条在役车道里有 {n_offhost} 条的数字不在本机盘上："
                    + "、".join(parts)
                    + f"；留在本机盘上的 {n_here} 条里 {n_aud} 条可核实"
                    + (f"，{n_unsigned} 条连署名都没有" if n_unsigned else "")
                    + "。")
    # r1380: "本机" is a fact about the observer, and this file is rewritten by
    # whichever machine ran the chain. Two boards an hour apart can say "6 off
    # this disk" and "9 off this disk" and both be right; a reader with only the
    # sentence cannot tell which disk was meant, and a gate that compared the two
    # read a host difference as a contradiction. So the observer says its name.
    if here and here != "unknown":
        sentence = f"以本机 {here} 的盘为基准：{sentence}"
    return {"here": here, "observer": here,
            "n_lanes": len(live), "n_offhost": n_offhost,
            "n_here": n_here, "n_auditable_here": n_aud,
            "n_unsigned_here": n_unsigned, "groups": out_groups,
            "offhost_lanes": sorted(r["lane"] for r in away),
            "sentence": sentence,
            "labels": {r["lane"]: AUTHORITY_LABEL.get(r.get("authority"),
                                                    r.get("authority"))
                       for r in live}}


def read_certification(path=None):
    """The last full-scan certification, or None if it has never been run.

    The board's per-symbol rows are read through a sample, so the holder count
    of the newest bar can only come from the full scan. Returning None (rather
    than an empty truth) keeps a missing certification readable as "unknown"
    instead of being folded into "every symbol holds it".
    """
    try:
        with open(path or CERT_PATH, encoding="utf-8") as fh:
            d = json.load(fh)
    except (OSError, ValueError):
        return None
    rows = {r.get("lane"): r for r in (d.get("lanes") or []) if r.get("lane")}
    return {"as_of": d.get("as_of"), "rows": rows, "verdict": d.get("verdict")}


def _holder_sentence(row, cert_row, cert_as_of):
    """One row's holder facts, or the honest reason they are not printed."""
    if not cert_row:
        return " (holder share unknown -- run `certify`)"
    share = cert_row.get("tail_holder_share")
    holders = cert_row.get("tail_holders")
    files = cert_row.get("files")
    full_tail = cert_row.get("full_tail")
    board_tail = row.get("panel_tail") or row.get("tail")
    if full_tail and board_tail and str(full_tail) < str(board_tail):
        # The scan that counted holders read an older tail than this board row:
        # its counts describe a different panel state and must not be quoted.
        return (f" (certification is older than this scan: full scan read "
                f"{full_tail}, this row reads {board_tail})")
    txt = ""
    if holders is not None and files:
        pct = f"{share * 100:.2f}%" if share is not None else "?"
        txt += f"; the full scan holds it in {holders:,} of {files:,} symbols ({pct})"
    if cert_row.get("thin_tail"):
        txt += (" -- **thin tail**: that is a handful of symbols' bar, not the "
                "panel's state")
    if cert_as_of:
        txt += f" (certified {cert_as_of})"
    return txt


# --------------------------------------------------- statutory-clock lanes (r1265)
# The rest of this board answers "which official TRADING day should exist". These
# lanes answer a different question -- "which REPORT PERIOD is the statute asking
# for" -- so they cannot be judged by judge() at all. They used to be absent from
# the board, which is why a missed quarterly deadline stayed invisible: r1263 had
# to run the collector by hand to discover the 2026Q3 gap.
PERIOD_LANES = [
    {"lane": "fund_statements", "writer": "update_fund_statements",
     "unit": "statutory report period (quarter-end + statutory deadline)",
     "loss_mode": "a period is only late, never lost: EM returns the whole "
                  "history per period, so a late fill is still complete"},
]


def audit_period_lanes(now, lanes=None, root=ROOT, machines_dir=None):
    """Judge statutory-clock lanes against their own clock, never the calendar.

    The expected period set and the panel reading are imported from the lane's
    own writer (single source), so the board cannot drift from the collector:
    the writer owns the statute table and the panel-bytes derivation.
    """
    rows = []
    for spec in (lanes if lanes is not None else PERIOD_LANES):
        writer = spec.get("writer")
        row = {"lane": spec["lane"], "kind": "period_status",
               "writer": writer, "unit": spec.get("unit"),
               "loss_mode": spec.get("loss_mode")}
        try:
            mod = importlib.import_module(writer)
        except Exception as ex:                       # noqa: BLE001
            row.update({"verdict": "unreadable",
                        "why": f"writer {writer} not importable: "
                               f"{type(ex).__name__}: {str(ex)[:120]}"})
            rows.append(row)
            continue
        try:
            facts = mod.panel_period_facts(now)
        except Exception as ex:                       # noqa: BLE001
            row.update({"verdict": "unreadable",
                        "why": f"panel_period_facts failed: "
                               f"{type(ex).__name__}: {str(ex)[:120]}"})
            rows.append(row)
            continue
        row.update(facts)
        missing = facts.get("missing_periods") or []
        row["verdict"] = ("period_missing" if missing
                          else ("in_sync" if facts.get("n_present")
                                else "absent"))
        if missing:
            row["why"] = (f"the statute demanded {facts['expected_latest']} from "
                          f"{facts['expected_deadline']}; the panel on this disk "
                          f"stops at {facts.get('cutoff')} "
                          f"({len(missing)} period(s) missing)")
        host = None
        if _lane_host is not None and writer:
            try:
                host = _lane_host(writer, None)
            except Exception:
                host = None
        row["lane_host"] = host or spec.get("owner")
        hh = _host_health(row["lane_host"], now, machines_dir)
        row["host_last_seen"] = hh["last_seen"]
        row["host_age_h"] = hh["age_h"]
        row["host_alive"] = hh["alive"]
        row["takeover_capable"] = takeover_capable(writer, root)
        if missing and row["host_alive"] is False and not row["takeover_capable"]:
            # the r1258 split, applied to a clock the board could not previously
            # measure at all: waiting is not a plan when nobody may act
            row["frozen_without_takeover"] = True
        rows.append(row)
    return rows


def render_period_md(rows):
    if not rows:
        return ""
    out = ("\n## Lanes whose clock is the statute, not the trading calendar\n\n"
           "A quarterly report period cannot be judged by an official trading "
           "day: the unit is the period and the deadline is statutory.\n\n"
           "| lane | host | panel cutoff | statute demands | missing | verdict "
           "| takeover path |\n|---|---|---|---|---|---|---|\n")
    for r in rows:
        out += (f"| `{r['lane']}` | {r.get('lane_host') or '--'} | "
                f"{r.get('cutoff') or '--'} | "
                f"{r.get('expected_latest') or '--'} "
                f"(due {r.get('expected_deadline') or '--'}) | "
                f"{len(r.get('missing_periods') or [])} | {r.get('verdict')} | "
                f"{'yes' if r.get('takeover_capable') else 'no'} |\n")
    for r in rows:
        if r.get("why"):
            out += f"\n- `{r['lane']}`: {r['why']}"
            if r.get("host_age_h") is not None:
                out += (f" -- host `{r.get('lane_host')}` silent "
                        f"{r['host_age_h']}h")
            if r.get("frozen_without_takeover"):
                out += (" -- **and the writer cannot declare a stand-in**, so "
                        "waiting for the host cannot fix this")
            out += "\n"
    return out + "\n"


def render_md(report, cert="auto"):
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
    # r1266: a hole count hides which holes were somebody's decision. The
    # auditing face already sorts every past hole by cause; print the split so a
    # reader stops waiting for a stand-in to fill days that are simply gone.
    bycause = [r for r in report["lanes"]
               if isinstance(r.get("holes_by_cause"), dict)
               and r["holes_by_cause"]]
    if bycause:
        tailnote += ("\n## Who was awake on the days that are missing\n\n"
                     "Each missing day below is classified by its own collector. "
                     "`takeover_possible` means another machine was awake inside "
                     "the capture window and nobody declared a stand-in: that day "
                     "was movable *at the time*. Every other cause means no "
                     "machine was sampling. Either way the day is behind us -- a "
                     "takeover declared today starts capturing today.\n\n")
        for r in bycause:
            parts = ", ".join(f"{k} {v}" for k, v in
                              sorted(r["holes_by_cause"].items()))
            # The collector's ledger covers the whole lane history; this row's
            # `missing` only counts days after the lane's last captured day.
            # Printing one number over the other's breakdown would be a count
            # that does not match its parts, so both are named.
            holes_total = sum(int(v) for v in r["holes_by_cause"].values()
                              if isinstance(v, int))
            tail_gap = (f"{r.get('n_missing')} missing day(s) after the lane's "
                        f"last captured day")
            if holes_total == r.get("n_missing"):
                scope = tail_gap
            else:
                scope = (f"{tail_gap}, out of {holes_total} hole(s) recorded "
                         f"since the lane started")
            tailnote += f"- `{r['lane']}`: {scope} ({parts})\n"
    why = [r for r in report["lanes"] if r.get("why")]
    disk = report.get("disk") or {}
    disks = ""
    if disk.get("sentence"):
        disks = ("\n## Whose disk these numbers are on\n\n"
                 f"{disk['sentence']}\n\n")
        for g in disk.get("groups") or []:
            disks += (f"- `{g['machine']}`: {', '.join(g.get('lanes') or [])}"
                      f"{'' if g.get('alive') is not False else ' (host down)'}\n")
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
    if report.get("hosts_silent"):
        # D-20261108-14: its own section -- a silent owner is not the same alarm
        # as a lane that stopped, and merging the two hid nine lanes for 194h
        tailnote += ("\n## Owners that stopped reporting\n\n"
                     "A different question from the section above: these "
                     "machines have written no heartbeat for more than "
                     f"{report.get('host_silent_hours')}h, so the lanes they own "
                     "are being judged from whatever was last committed. A lane "
                     "here can still read `in_sync` -- the number is old, the "
                     "owner is gone, and nobody would notice the day the file "
                     "stops being written.\n\n")
        for host in report["hosts_silent"]:
            h = (report.get("hosts") or {}).get(host) or {}
            age = h.get("age_h")
            tailnote += (f"- `{host}`: last seen {h.get('last_seen')}"
                         + (f" ({age}h ago)" if age is not None else "")
                         + f" -- owns {', '.join(h.get('silent_lanes') or [])}\n")
    unm = report.get("unmeasured_lanes") or []
    if unm:
        tailnote += ("\n## Lanes the coverage rule caught, with no reader\n\n"
                     "`config/lane_hosts.json` declares these lanes; this board "
                     "has no extractor for them, so nothing is measuring them. "
                     "They are listed instead of omitted -- a lane nobody reads "
                     "and a lane that produces nothing must not look the same.\n\n")
        for name in unm:
            tailnote += f"- `{name}`: declared by the map, unmeasured here\n"
    frozen = report.get("frozen_without_takeover") or []
    if frozen:
        tailnote += ("\n## Lanes nobody can pick up while the host is away\n\n"
                     "These are not waiting on patience. The host is silent and "
                     "the collector has no declared-takeover path, so **no "
                     "machine is allowed to move them** -- the last written "
                     "envelope stays the newest number the company has, and "
                     "each day that passes is gone for good where the face is "
                     "forward-accumulation only. Unblocking one is a decision "
                     "(reassign the lane, or give its collector the same "
                     "stale-takeover rule the other eight lanes already have), "
                     "not a retry.\n\n")
        for name in frozen:
            row = next((r for r in report["lanes"] if r["lane"] == name), {})
            w = row.get("writer")
            tailnote += (f"- `{name}`: "
                         + (f"writer `{w}` has no `{TAKEOVER_MARKER}` path\n"
                            if w else
                            "the row reads another face rather than a collector "
                            "of its own, so there is nothing to reassign\n"))
    if why:
        tailnote += ("\n## Why some lanes cannot be certified here\n\n"
                     "A status envelope is committed by whichever machine ran the "
                     "leg, and every machine also keeps its own gitignored copy of "
                     "the data. Neither names its writer, so a tail that reads "
                     "late can be a dead lane or a stale copy of a live one.\n\n")
        for r in why:
            tailnote += f"- `{r['lane']}`: {r['why']}\n"
    stale_env = [r for r in report["lanes"] if r.get("envelope_stale")]
    if stale_env:
        tailnote += ("\n## Envelopes older than the panel they describe\n\n"
                     "A status envelope is a committed file, so a branch switch or "
                     "a rebase can restore an older copy of it. Where this host can "
                     "read the panel itself the panel is the measurement: the "
                     "staleness is printed here instead of being read as a stall.\n\n")
        for r in stale_env:
            lag = r.get("envelope_lag_days")
            tailnote += (f"- `{r['lane']}`: envelope says {r['envelope_tail']}, "
                         f"panel holds {r['panel_tail']}"
                         + (f" ({lag} official days behind)" if lag is not None
                            else " (past the calendar, day count N/A)")
                         + "\n")
    sampled = [r for r in report["lanes"]
               if (r.get("panel_read") or {}).get("sampled")]
    behind = [r for r in report["lanes"] if r.get("panel_behind_envelope")]
    if behind:
        tailnote += ("\n## Copies that hold less than their envelope claims\n\n"
                     "The envelope is what some machine says it collected; the "
                     "panel is what is on this disk. Where the copy is behind "
                     "its own envelope the row cannot be read as current here, "
                     "even though the lane itself may be alive elsewhere.\n\n")
        for r in behind:
            n = r.get("panel_behind_days")
            tailnote += (f"- `{r['lane']}`: envelope says "
                         f"{r['panel_behind_envelope']}, this copy holds "
                         f"{r.get('panel_tail')}"
                         + (f" ({n} official days behind)" if n else "")
                         + "\n")
    if sampled:
        tailnote += ("\n## Tails read from a sample\n\n"
                     "The per-symbol panels hold thousands of files, so their "
                     "tail is read through an evenly spaced sample rather than a "
                     "full sweep. A sample can miss a single laggard symbol; it "
                     "cannot miss a panel that stopped weeks ago. Each row below "
                     "says how many symbols were read out of how many.\n\n")
        cert_rows = {}
        cert_as_of = None
        if cert == "auto":
            cert = read_certification()
        if isinstance(cert, dict):
            cert_rows = cert.get("rows") or {}
            cert_as_of = cert.get("as_of")
        for r in sampled:
            pr = r["panel_read"]
            tailnote += (f"- `{r['lane']}`: {pr.get('per_file')} of "
                         f"{pr.get('files')} symbols read, tail "
                         f"{r.get('panel_tail') or r.get('tail')}"
                         + _holder_sentence(r, cert_rows.get(r["lane"]),
                                            cert_as_of)
                         + "\n")
        # r1261: the sample is certified against a full scan, and that scan also
        # says how many symbols hold the newest bar -- a tail held by two files
        # is one symbol's bar, not the panel's.
        tailnote += ("\nFull-scan certification of exactly these rows: "
                     "`scripts/data_lane_freshness.py certify` -> "
                     "`docs/data_lanes/TAIL_CERTIFICATION.md` "
                     "(it re-reads every file and names the symbols that sit "
                     "behind the newest bar).\n")
    return (head + disks + cols + body + tailnote
            + render_period_md(report.get("period_lanes")))


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

        # L19 (r1256) the canonical authority block IS an attribution: an
        # envelope that names its writer only there must not read as "somebody
        # anonymous wrote this". Live 2026-11-07: update_astock_daily declared
        # its takeover and the board still refused to certify a panel this very
        # host was building.
        json.dump({"latest_snapshot": "2026-10-20",
                   "authority": {"lane_owner": "bm-b", "writer_machine": "bm-a",
                                 "data_face_machine": "bm-a",
                                 "declared_takeover": True,
                                 "took_over_by": "bm-a"}},
                  open(os.path.join(td, "h.json"), "w"))
        r3 = audit(days, now, root=td, machines_dir=os.path.join(td, "m"),
                   lanes=spec)["lanes"][0]
        assert r3["reported_by"] == "bm-a", r3
        assert r3["authority"] == "declared_takeover", r3
        assert r3["verdict"] != "unverifiable", r3
        print("[PASS] L19 an authority block attributes the writer, so a "
              "declared stand-in is not read as an anonymous foreign write",
              flush=True)

        # L20 (r1257) the older half-shape must be named, not shrugged at: a
        # takeover in `takeover{}` with no `authority.took_over_by` is a
        # declaration no reader can see. Live 2026-11-07: update_zt_pool had
        # published it every run since 10-29 and this board printed the lane
        # `unverifiable` for nine days without saying why.
        json.dump({"machine": "bm-a", "latest_snapshot": "2026-10-20",
                   "takeover": {"owner": "bm-b", "by": "bm-a",
                                "reason": "owner bm-b silent 191.3h >= 120min",
                                "ts": "2026-11-07T11:57:00"}},
                  open(os.path.join(td, "h.json"), "w"))
        r4 = audit(days, now, root=td, machines_dir=os.path.join(td, "m"),
                   lanes=spec)["lanes"][0]
        assert r4["verdict"] == "unverifiable", r4
        assert r4.get("unread_takeover_by") == "bm-a", r4
        assert "takeover{}" in (r4.get("why") or ""), r4
        assert r4["why"].startswith("bm-a declared a stand-in"), r4["why"]
        print("[PASS] L20 a stand-in declared in the old shape is named as "
              "unreadable, not left as an anonymous write", flush=True)

    # L14 whose disk: a lane this machine cannot certify is not a gap on this
    # machine -- it is somebody else's disk, and the sentence must name it
    # (r1162: r1159 named the dead host, but the two human faces still only
    # printed "cannot certify here", which is a fact about our copy)
    rows = [
        {"lane": "heat", "verdict": "unverifiable", "authority": "non_host_copy",
         "lane_host": "bm-b"},
        {"lane": "repo", "verdict": "unverifiable",
         "authority": "non_host_envelope", "reported_by": "bm-a",
         "lane_host": "bm-b"},
        {"lane": "futures", "verdict": "in_sync", "authority": "host_envelope",
         "reported_by": "bm-a", "lane_host": "bm-a", "auditable": True},
        {"lane": "options", "verdict": "retired", "authority": "unattributed"},
    ]
    d = disk_face(rows, {"bm-b": {"alive": False, "age_h": 11.8,
                                  "last_seen": "2026-10-29T18:18:13+08:00"}},
                  here="bm-a")
    assert d["n_lanes"] == 3 and d["n_offhost"] == 2 and d["n_here"] == 1, d
    assert [g["machine"] for g in d["groups"]] == ["bm-b"], d
    assert d["groups"][0]["n"] == 2 and d["groups"][0]["alive"] is False, d
    assert "bm-b" in d["sentence"] and "11.8h" in d["sentence"], d["sentence"]
    assert "本机盘上的 1 条里 1 条可核实" in d["sentence"], d["sentence"]
    assert "options" not in d["offhost_lanes"], d          # retired owes nothing
    print("[PASS] L14 a lane on somebody else's disk is named, per machine, "
          "and a retired face is not a gap", flush=True)

    # L15 the honest poles: all-ours, ours-but-unsigned, and empty. An unsigned
    # envelope whose bytes sit here is ON this disk and still uncertified -- the
    # two questions must not collapse into one (live case: etf_panel)
    d2 = disk_face([{"lane": "lhb", "verdict": "in_sync",
                     "authority": "host_envelope", "reported_by": "bm-a",
                     "auditable": True}], here="bm-a")
    assert d2["n_offhost"] == 0 and d2["groups"] == [], d2
    assert "全都落在本机盘上" in d2["sentence"], d2["sentence"]
    assert "1 条有署名可核实" in d2["sentence"], d2["sentence"]
    d2b = disk_face([{"lane": "etf_panel", "verdict": "unverifiable",
                      "authority": "unattributed", "lane_host": "bm-a",
                      "auditable": False}], here="bm-a")
    assert d2b["n_offhost"] == 0 and d2b["n_here"] == 1, d2b
    assert "1 条连署名都没有" in d2b["sentence"] or "没有署名" in d2b["sentence"], \
        d2b["sentence"]
    d3 = disk_face([])
    assert d3["n_lanes"] == 0 and "无从谈起" in d3["sentence"], d3
    print("[PASS] L15 all-ours and empty boards read honestly, not as a "
          "zero-row gap", flush=True)

    # L16 (r1380) the sentence must name the OBSERVER. One shared file, rewritten
    # by whichever machine ran the chain, and "本机" means a different disk on each
    # of them -- an unnamed sentence is a sentence about nobody, and the same rows
    # read from two hosts must not produce two identical sentences.
    _rows = [{"lane": "heat", "verdict": "unverifiable",
              "authority": "non_host_copy", "lane_host": "bm-b"}]
    _hc = {"bm-b": {"alive": True, "age_h": 0.4}}
    a_side = disk_face(_rows, _hc, here="bm-a")
    c_side = disk_face(_rows, _hc, here="bm-c")
    assert a_side["n_offhost"] == c_side["n_offhost"] == 1, (a_side, c_side)
    assert "bm-a" in a_side["sentence"] and "bm-c" in c_side["sentence"], \
        (a_side["sentence"], c_side["sentence"])
    assert a_side["sentence"] != c_side["sentence"], "observer is not named"
    assert a_side["observer"] == "bm-a", a_side
    # an unknown observer is not a name: it must not print "本机 unknown"
    _u = disk_face(_rows, _hc, here="unknown")
    assert "unknown" not in _u["sentence"], _u["sentence"]
    print("[PASS] L16 the disk sentence names its observer, so the same rows "
          "read from two hosts are attributable, not contradictory", flush=True)

    # L17 (r1255) the envelope is a report about the panel, never a substitute
    # for it: an OLDER committed envelope (restored by a rebase) must not make a
    # lane that already holds newer bars read as stalled.
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "m"))
        os.makedirs(os.path.join(td, "px"))
        json.dump({"heartbeat_epoch_utc": int(dt.datetime.now().timestamp())},
                  open(os.path.join(td, "m", "bm-a.json"), "w"))
        json.dump({"machine": "bm-a", "data_cutoff": "2026-10-30"},
                  open(os.path.join(td, "s.json"), "w"))
        for name, day in (("IF.csv", "2026-11-06"), ("AU.csv", "2026-11-06")):
            with open(os.path.join(td, "px", name), "w") as f:
                f.write("2026-10-30,1,2,3,4\n" + day + ",9,9,9,9\n")
        spec = [{"lane": "futures", "kind": "status", "path": "s.json",
                 "key": "data_cutoff", "owner": "bm-a",
                 "panel_csv": {"dir": "px", "pattern": "*.csv"}}]
        r = audit(days, now, root=td, machines_dir=os.path.join(td, "m"),
                  lanes=spec)["lanes"][0]
        assert r["tail"] == "2026-11-06", r          # the panel wins
        assert r["verdict"] == "in_sync", r
        assert r["envelope_stale"] is True, r
        assert r["envelope_tail"] == "2026-10-30", r
        assert r["envelope_lag_days"] is None and \
            r["envelope_lag_beyond_calendar"] is True, r
        assert r["panel_tail"] == "2026-11-06", r

        # L18 the opposite direction is NOT a licence to borrow: a panel that
        # lags its own envelope must not heal the verdict.
        json.dump({"machine": "bm-a", "data_cutoff": "2026-11-06"},
                  open(os.path.join(td, "s.json"), "w"))
        for name in ("IF.csv", "AU.csv"):
            with open(os.path.join(td, "px", name), "w") as f:
                f.write("2026-10-20,1,2,3,4\n")
        r2 = audit(days, now, root=td, machines_dir=os.path.join(td, "m"),
                   lanes=spec)["lanes"][0]
        assert r2["tail"] == "2026-11-06", r2         # envelope still governs
        assert r2["envelope_stale"] is False, r2
        # r1259: and the gap is named rather than left to the reader
        assert r2["panel_behind_envelope"] == "2026-11-06", r2
        assert r2["panel_behind_days"] >= 1, r2
        assert r2["verdict"] in ("in_sync", "today_pending"), r2
    print("[PASS] L17/L18 an older envelope cannot stall a lane that holds "
          "newer bars, and a lagging panel cannot heal a lagging envelope",
          flush=True)

    # L22 the per-symbol panels (5,222 files each) are read through a
    # deterministic sample, and that sample has to reach the END of the
    # alphabet -- a first-N read would call a panel current whether the tail
    # symbols had stopped or not, which is the failure this cross-check is for.
    with tempfile.TemporaryDirectory() as td:
        pdir = os.path.join(td, "per")
        os.makedirs(pdir)
        for i in range(200):
            day = "2026-11-06" if i == 199 else "2026-10-20"
            with open(os.path.join(pdir, "%06d.csv" % i), "w") as fh:
                fh.write("date,close\n%s,1.0\n" % day)
        t22, i22 = panel_tail_csv(pdir)
        assert t22 == "2026-11-06", (t22, i22)   # the last symbol, not the first 40
        assert i22.get("sampled") is True and i22["files"] == 200, i22
        assert i22["per_file"] == 40, i22        # one sampled file per slot
        # a real panel with 9 symbols is NOT sampled: the count is exact
        for i in range(200, 209):
            with open(os.path.join(pdir, "%06d.csv" % i), "w") as fh:
                fh.write("date,close\n2026-11-06,1.0\n")
        t9, i9 = panel_tail_csv(pdir, max_files=40)
        assert i9["files"] == 209 and i9["per_file"] == 40, i9
        with tempfile.TemporaryDirectory() as td2:
            os.makedirs(os.path.join(td2, "per"))
            for i in range(5):
                with open(os.path.join(td2, "per", "%06d.csv" % i), "w") as fh:
                    fh.write("date,close\n2026-11-03,1.0\n")
            _, i5 = panel_tail_csv(os.path.join(td2, "per"))
            assert i5 == {"files": 5, "per_file": 5}, i5   # no `sampled` when exact
    print("[PASS] L22 a 5,222-file panel is read by an evenly spaced sample "
          "that reaches the last symbol, and the sample is disclosed", flush=True)

    # L21 a lane whose host is silent splits in two: the ones a healthy machine
    # may declare a stand-in for, and the ones nobody is allowed to move at all.
    # Capability is read from the writer's own source, so transplanting the
    # takeover rule into that writer flips the reading without anyone editing a
    # list next to it.
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "m"))
        os.makedirs(os.path.join(td, "scripts"))
        json.dump({"clock_read": "2026-10-29T04:18:13+08:00"},
                  open(os.path.join(td, "m", "bm-b.json"), "w"))
        for lane, writer, body in (
                ("plain_lane", "w_plain", "print('no-op')\n"),
                ("take_lane", "w_take",
                 f"print('{TAKEOVER_MARKER} bm-b heat lane')\n")):
            with open(os.path.join(td, "scripts", writer + ".py"), "w") as fh:
                fh.write(body)
            json.dump({"machine": "bm-a", "panel": {"cut": "2026-10-20"}},
                      open(os.path.join(td, lane + ".json"), "w"))
        spec = [{"lane": ln, "kind": "status", "path": ln + ".json",
                 "key": "panel.cut", "owner": "bm-b", "writer": w}
                for ln, w in (("plain_lane", "w_plain"), ("take_lane", "w_take"))]
        rep = audit(days, now, root=td, machines_dir=os.path.join(td, "m"),
                    lanes=spec)
        _o = {r["lane"]: r for r in rep["lanes"]}
        assert _o["plain_lane"]["verdict"] == "unverifiable", _o["plain_lane"]
        assert _o["plain_lane"]["host_alive"] is False, _o["plain_lane"]
        assert _o["plain_lane"]["takeover_capable"] is False, _o["plain_lane"]
        assert _o["take_lane"]["takeover_capable"] is True, _o["take_lane"]
        assert rep["frozen_without_takeover"] == ["plain_lane"], \
            rep["frozen_without_takeover"]
        md = render_md(rep)
        assert "Lanes nobody can pick up" in md, md
        _sect = md.split("Lanes nobody can pick up")[1].split("\n## ")[0]
        assert "`plain_lane`" in _sect, _sect
        assert "`w_take`" not in _sect, _sect
        # transplant the rule -> the same lane stops being a decision
        with open(os.path.join(td, "scripts", "w_plain.py"), "a") as fh:
            fh.write(f"print('{TAKEOVER_MARKER} bm-b plain lane')\n")
        rep2 = audit(days, now, root=td, machines_dir=os.path.join(td, "m"),
                     lanes=spec)
        assert rep2["frozen_without_takeover"] == [], \
            rep2["frozen_without_takeover"]
    print("[PASS] L21 a silent host's frozen lanes are split by whether the "
          "writer can declare a stand-in, read out of that writer", flush=True)

    # L23 the forty-file sample is a claim about a 5,222-file panel; the full
    # read is the measurement. The fixture puts the newest bar on an interior
    # symbol the sample never opens, so the two disagree -- and the certification
    # has to say so, name the lane, and count the symbols sitting behind it.
    with tempfile.TemporaryDirectory() as td:
        pdir = os.path.join(td, "per")
        os.makedirs(pdir)
        for i in range(300):
            day = "2026-11-06" if i == 150 else "2026-10-20"
            with open(os.path.join(pdir, "%06d.csv" % i), "w") as fh:
                fh.write("date,close\n%s,1.0\n" % day)
        samp23, _ = panel_tail_csv(pdir)
        full23, fin23 = panel_tail_csv_full(pdir)
        assert samp23 == _as_date("2026-10-20"), samp23   # the sample never opens 150
        assert full23 == _as_date("2026-11-06"), full23    # the full read does
        assert fin23["n_laggards"] == 299, fin23
        assert fin23["files"] == 300 and fin23["per_file"] == 300, fin23
        spec23 = [{"lane": "cert_lane", "panel_csv": {"dir": "per",
                                                      "pattern": "*.csv"}}]
        rows23, verdict23 = certify_rows(spec23, root=td)
        assert verdict23 == "sample_understated", (verdict23, rows23)
        assert rows23[0]["agree"] is False, rows23
        assert rows23[0]["full_tail"] == "2026-11-06", rows23
        assert rows23[0]["sample_tail"] == "2026-10-20", rows23
        assert rows23[0]["direction"] == "sample_understated", rows23
        # one of 300 symbols holds the newest bar -> the number travels alone
        assert rows23[0]["tail_holders"] == 1 and rows23[0]["thin_tail"] is True, rows23
        # every symbol carries the newest bar -> certified, and nothing is named
        for i in range(300):
            with open(os.path.join(pdir, "%06d.csv" % i), "w") as fh:
                fh.write("date,close\n2026-11-06,1.0\n")
        rows24, verdict24 = certify_rows(spec23, root=td)
        assert verdict24 == "certified", (verdict24, rows24)
        assert rows24[0]["n_laggards"] == 0 and rows24[0]["laggards"] == [], rows24
        assert rows24[0]["thin_tail"] is False, rows24
        assert rows24[0]["tail_holder_share"] == 1.0, rows24
        # three symbols stopped a day early: certified tail, but named laggards
        for i in (7, 88, 299):
            with open(os.path.join(pdir, "%06d.csv" % i), "w") as fh:
                fh.write("date,close\n2026-11-05,1.0\n")
        rows25, verdict25 = certify_rows(spec23, root=td)
        assert verdict25 == "certified", verdict25      # the tail is still 11-06
        assert rows25[0]["n_laggards"] == 3, rows25
        assert rows25[0]["laggards"] == ["000007.csv", "000088.csv", "000299.csv"], rows25
        # 297 of 300 hold the tail -> a laggard list, not a thin tail
        assert rows25[0]["thin_tail"] is False, rows25
    print("[PASS] L23 a panel tail read by sample is certified against a full "
          "scan, and the symbols sitting behind the newest bar are named", flush=True)

    # L24 the human row has to carry the holder count, or the board keeps
    # quoting "the panel's tail" for a bar two symbols hold. Three branches:
    # a matching certification is quoted; a missing one is printed as unknown
    # (never as "all symbols"); an older certification is refused against a
    # newer board tail instead of lending it numbers it never measured.
    rep24 = {"as_of": "2026-11-07T14:00:00", "verdict": "host_down",
             "counts": {"in_sync": 0}, "n_lanes": 1, "n_auditable": 0,
             "worst": None,
             "lanes": [{"lane": "per_lane", "lane_host": "bm-b",
                        "tail": "2026-10-19", "panel_tail": "2026-10-19",
                        "panel_read": {"files": 5222, "per_file": 40,
                                       "sampled": True},
                        "verdict": "unverifiable", "authority": None}],
             "expected_last_official_day": "2026-11-06",
             "calendar_days": 100, "close_accept_time": "15:30"}
    md24 = render_md(rep24, cert={
        "as_of": "2026-11-07T13:47:58",
        "rows": {"per_lane": {"lane": "per_lane", "full_tail": "2026-10-19",
                              "tail_holders": 2, "tail_holder_share": 0.0004,
                              "files": 5222, "thin_tail": True}}})
    sect24 = md24.split("Tails read from a sample")[1]
    assert "2 of 5,222 symbols (0.04%)" in sect24, sect24
    assert "thin tail" in sect24, sect24
    md24b = render_md(rep24, cert=None)
    assert "holder share unknown" in md24b, md24b
    md24c = render_md(rep24, cert={
        "as_of": "2026-11-06T10:00:00",
        "rows": {"per_lane": {"lane": "per_lane", "full_tail": "2026-10-13",
                              "tail_holders": 1, "tail_holder_share": 0.0002,
                              "files": 5222, "thin_tail": True}}})
    sect24c = md24c.split("Tails read from a sample")[1].split(
        "Full-scan certification")[0]
    assert "certification is older than this scan" in sect24c, sect24c
    assert "thin tail" not in sect24c, sect24c
    print("[PASS] L24 the human row quotes the full scan's holder count, says "
          "unknown when it was never certified, and refuses a stale "
          "certification", flush=True)

    # L25 (r1265) a lane whose clock is the statute must be judged on that clock
    # -- the whole board above cannot see it, which is how the 2026Q3 deadline
    # passed unnoticed (r1263 had to run the collector by hand to find it).
    _prow = audit_period_lanes(dt.datetime(2026, 11, 7, 12, 0))[0]
    assert _prow["lane"] == "fund_statements", _prow
    assert _prow["expected_latest"] == "20260930", _prow
    assert _prow["expected_deadline"] == "2026-10-31", _prow
    assert _prow["verdict"] in ("period_missing", "in_sync"), _prow["verdict"]
    # the verdict has to follow the missing list, in both directions
    assert (_prow["verdict"] == "period_missing") == bool(
        _prow.get("missing_periods")), _prow
    # and this round's fix is visible to the same reader the board uses
    assert _prow["takeover_capable"] is True, _prow
    _pmd = render_period_md([_prow])
    assert "fund_statements" in _pmd and "takeover path" in _pmd, _pmd
    # a lane with a missing period whose host is silent AND whose writer cannot
    # declare a stand-in is a decision, not a wait (r1258 split, new clock)
    _froz = dict(_prow, takeover_capable=False, host_alive=False)
    assert _froz.get("takeover_capable") is False
    print("[PASS] L25 a statutory-clock lane is judged on the statute, and its "
          "takeover path is read off the writer", flush=True)

    # L26 a lane whose row did not name its collector reads as "nothing to
    # reassign" -- a sentence that tells the reader to give up on a lane two
    # machines could already move. Live 2026-11-07: `marks` had `writer: None`
    # while update_intraday_marks had shipped the takeover rule at r1101, so the
    # board printed that give-up sentence about the only intraday evidence face.
    # The fixture asserts both halves: an undeclared collector reads frozen with
    # the give-up wording, and declaring it flips the reading and the sentence.
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "m"))
        os.makedirs(os.path.join(td, "scripts"))
        json.dump({"clock_read": "2026-10-29T04:18:13+08:00"},
                  open(os.path.join(td, "m", "bm-b.json"), "w"))
        with open(os.path.join(td, "scripts", "w_coll.py"), "w") as fh:
            fh.write(f"print('{TAKEOVER_MARKER} bm-b marks lane')\n")
        json.dump({"last_captured": "2026-10-20"},
                  open(os.path.join(td, "cov.json"), "w"))
        undeclared = [{"lane": "marksx", "kind": "external", "path": "cov.json",
                       "tail_key": "last_captured", "owner": "bm-b",
                       "writer": None}]
        rep26a = audit(days, now, root=td, machines_dir=os.path.join(td, "m"),
                       lanes=undeclared)
        assert rep26a["frozen_without_takeover"] == ["marksx"], rep26a
        md26a = render_md(rep26a)
        _s26a = md26a.split("Lanes nobody can pick up")[1].split("\n## ")[0]
        assert "nothing to reassign" in _s26a, _s26a
        declared = [dict(undeclared[0], writer="w_coll")]
        rep26b = audit(days, now, root=td, machines_dir=os.path.join(td, "m"),
                       lanes=declared)
        assert rep26b["lanes"][0]["takeover_capable"] is True, rep26b["lanes"][0]
        assert rep26b["frozen_without_takeover"] == [], rep26b
        _md26b = render_md(rep26b)
        assert "Lanes nobody can pick up" not in _md26b, _md26b
        # declaring a writer whose collector has no path still names the reason
        with open(os.path.join(td, "scripts", "w_dumb.py"), "w") as fh:
            fh.write("print('no-op')\n")
        rep26c = audit(days, now, root=td, machines_dir=os.path.join(td, "m"),
                       lanes=[dict(undeclared[0], writer="w_dumb")])
        _s26c = (render_md(rep26c).split("Lanes nobody can pick up")[1]
                 .split("\n## ")[0])
        assert "`w_dumb` has no" in _s26c and "nothing to reassign" not in _s26c, _s26c
    print("[PASS] L26 an undeclared collector is not the same as a collector "
          "with no takeover path -- and only the second is a decision", flush=True)

    # L27 a hole count hides who could have acted. The auditing face already
    # classifies every past hole by cause; the board has to carry that split to
    # the human page, or "6 days missing" keeps reading as "6 days a stand-in
    # will soon fill". Both halves are asserted: the split is printed, and the
    # sentence says a takeover starts today rather than backfilling.
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "m"))
        json.dump({"machine": "bm-b", "last_captured": "2026-10-20",
                   "holes_by_cause": {"host_down": 2, "takeover_possible": 2,
                                      "host_offhours": 1}},
                  open(os.path.join(td, "cov.json"), "w"))
        spec27 = [{"lane": "hole_lane", "kind": "external", "path": "cov.json",
                   "tail_key": "last_captured", "owner": "bm-b", "writer": None}]
        rep27 = audit(days, now, root=td, machines_dir=os.path.join(td, "m"),
                      lanes=spec27)
        _r27 = rep27["lanes"][0]
        assert _r27["holes_by_cause"]["takeover_possible"] == 2, _r27
        md27 = render_md(rep27)
        assert "Who was awake on the days that are missing" in md27, md27
        _s27 = md27.split("Who was awake on the days that are missing")[1]
        assert "takeover_possible 2" in _s27, _s27
        assert f"{_r27['n_missing']} missing day(s)" in _s27, _s27
        assert "starts capturing today" in _s27, _s27
        # the collector's ledger covers the lane's whole history while this row
        # counts only days after the last capture: the two numbers must both be
        # named, or the line reads as a count that contradicts its own breakdown
        assert "out of 5 hole(s) recorded since the lane started" in _s27, _s27
        # when the two agree, the extra clause is not printed
        json.dump({"last_captured": "2026-10-20",
                   "holes_by_cause": {"host_down": _r27["n_missing"]}},
                  open(os.path.join(td, "same.json"), "w"))
        rep27c = audit(days, now, root=td, machines_dir=os.path.join(td, "m"),
                       lanes=[dict(spec27[0], path="same.json")])
        _s27c = (render_md(rep27c)
                 .split("Who was awake on the days that are missing")[1])
        assert "out of" not in _s27c, _s27c
        # a lane whose auditing face keeps no cause table does not get a section
        json.dump({"machine": "bm-b", "last_captured": "2026-10-20"},
                  open(os.path.join(td, "nocause.json"), "w"))
        rep27b = audit(days, now, root=td, machines_dir=os.path.join(td, "m"),
                       lanes=[dict(spec27[0], path="nocause.json")])
        assert "Who was awake" not in render_md(rep27b), rep27b
    print("[PASS] L27 a missing day is printed with who could have captured it, "
          "and a takeover is not sold as backfill", flush=True)

    # L28 (D-20261108-14) the coverage contract is the MAP, not the hand list.
    # Measured 2026-11-08: nine lanes were declared in config/lane_hosts.json
    # under a machine silent for 194h and none of them had a row here, so "the
    # lane produces nothing" and "nobody is looking" printed as the same blank.
    # Both halves are asserted: a mapped writer this file can read becomes a
    # row with its own tail, and a mapped writer it cannot read becomes an
    # `unmeasured` row -- never a silent omission and never `absent`.
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "config"))
        os.makedirs(os.path.join(td, "results"))
        os.makedirs(os.path.join(td, "m"))
        json.dump({"lane_hosts": {"update_sina_mf": "bm-c",
                                  "update_heat": "bm-c",
                                  "some_unmapped_puller": "bm-b"}},
                  open(os.path.join(td, "config", "lane_hosts.json"), "w"))
        json.dump({"machine": "bm-c", "panel": {"cutoff": "2026-10-20"}},
                  open(os.path.join(td, "results",
                                    "sina_mf_update_status.json"), "w"))
        _b28 = {s["lane"]: s for s in board_lanes(td)}
        assert _b28["some_unmapped_puller"]["kind"] == "undeclared", _b28.keys()
        assert _b28["sina_mf"]["kind"] == "status", _b28["sina_mf"]
        # update_heat already has a registry row: the union must not duplicate it
        assert [s["lane"] for s in board_lanes(td)].count("heat") == 1, _b28
        _union = [s for s in board_lanes(td)
                  if s.get("origin") == "lane_hosts_union"]
        assert {s["lane"] for s in _union} == {"sina_mf",
                                               "some_unmapped_puller"}, _union
        rep28 = audit(days, now, root=td,
                      machines_dir=os.path.join(td, "m"), lanes=_union)
        _o28 = {r["lane"]: r for r in rep28["lanes"]}
        assert _o28["sina_mf"]["verdict"] == "in_sync", _o28["sina_mf"]
        assert _o28["sina_mf"]["days_behind"] == 7, _o28["sina_mf"]
        assert _o28["some_unmapped_puller"]["verdict"] == "unmeasured", _o28
        assert rep28["unmeasured_lanes"] == ["some_unmapped_puller"], rep28
        assert rep28["counts"].get("absent", 0) == 0, rep28["counts"]
        assert rep28["coverage"]["lane_hosts_union_lanes"] == 2, rep28["coverage"]
        assert "Lanes the coverage rule caught" in render_md(rep28)
    print("[PASS] L28 a lane the map declares but this file cannot read is "
          "`unmeasured`, and a readable one joins the board instead of hiding",
          flush=True)

    # L29 a rolling-window lane is late only past its own window. Judging it by
    # "every official day since the tail" would print a permanent false alarm on
    # a lane whose contract is a 20-trading-day window -- and a false alarm is
    # how an alert becomes noise (r1201 class).
    with tempfile.TemporaryDirectory() as td:
        json.dump({"machine": "bm-c", "panel": {"cutoff": "2026-10-20"}},
                  open(os.path.join(td, "p.json"), "w"))
        _base = {"kind": "status", "path": "p.json", "key": "panel.cutoff",
                 "writer": "update_sina_mf", "owner": "bm-c"}
        spec29 = [dict(_base, lane="w_window", window_trading_days=20),
                  dict(_base, lane="w_plain")]
        rep29 = audit(days, now, root=td, lanes=spec29)
        _o29 = {r["lane"]: r for r in rep29["lanes"]}
        assert _o29["w_window"]["verdict"] == "in_sync", _o29["w_window"]
        assert _o29["w_window"]["days_behind"] == 7, _o29["w_window"]
        assert _o29["w_window"]["n_missing"] == 7, _o29["w_window"]
        assert _o29["w_plain"]["verdict"] == "stalled", _o29["w_plain"]
        # the window lane carries nine calendar days of gap and still may not be
        # published as the worst lane: it is inside its own contract
        assert rep29["worst"] == "w_plain", rep29["worst"]
    print("[PASS] L29 a rolling-window lane is judged by its window and never "
          "quoted as the worst lane", flush=True)

    # L30 (D-20261108-14) "the lane stopped" and "the owner stopped reporting"
    # are two alarms. A lane whose file was written before the host went quiet
    # can still cover the window -- the number is in_sync and the machine is
    # gone, and nothing would notice the day the file stops being written.
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "m"))
        json.dump({"machine": "bm-b", "cutoff": "2026-10-29"},
                  open(os.path.join(td, "f.json"), "w"))
        spec30 = [{"lane": "fresh_lane", "kind": "status", "path": "f.json",
                   "key": "cutoff", "owner": "bm-b", "writer": None}]
        json.dump({"clock_read": "2026-10-28T10:00:00+08:00"},
                  open(os.path.join(td, "m", "bm-b.json"), "w"))
        rep30 = audit(days, now, root=td,
                      machines_dir=os.path.join(td, "m"), lanes=spec30)
        assert rep30["lanes"][0]["verdict"] == "in_sync", rep30["lanes"][0]
        assert rep30["verdict"] == "all_fresh", rep30["verdict"]
        assert rep30["hosts_silent"] == ["bm-b"], rep30["hosts_silent"]
        assert rep30["silence_verdict"] == "hosts_silent", rep30
        assert rep30["hosts"]["bm-b"]["silent_lanes"] == ["fresh_lane"], rep30
        _md30 = render_md(rep30)
        assert "Owners that stopped reporting" in _md30, _md30
        assert "`bm-b`" in _md30.split("Owners that stopped reporting")[1], _md30
        # a host inside the 24h window is not silent, and the section disappears
        json.dump({"clock_read": "2026-10-29T17:00:00+08:00"},
                  open(os.path.join(td, "m", "bm-b.json"), "w"))
        rep30b = audit(days, now, root=td,
                       machines_dir=os.path.join(td, "m"), lanes=spec30)
        assert rep30b["hosts_silent"] == [], rep30b["hosts_silent"]
        assert rep30b["silence_verdict"] == "none", rep30b
        assert "Owners that stopped reporting" not in render_md(rep30b), rep30b
    print("[PASS] L30 a silent owner is its own alarm -- a fresh-looking lane "
          "does not clear it, and 3h of silence does not raise it", flush=True)

    print("selftest: 28/28 PASS", flush=True)
    return 0


CERT_PATH = os.path.join(ROOT, "results", "data_lane_tail_certification.json")
CERT_MD_PATH = os.path.join(ROOT, "docs", "data_lanes", "TAIL_CERTIFICATION.md")
# Below this share of a panel, the newest bar is one symbol's bar quoted as the
# panel's: name it instead of letting the number travel alone.
THIN_TAIL_SHARE = 0.10


def certify_rows(lanes=None, root=ROOT, laggard_cap=25):
    """(rows, verdict) -- read every declared panel in full, then ask the sample.

    Two questions per lane, and they are not the same question:
      * did the forty-file sample pick the same tail the full read picks? (`agree`)
      * is the panel's newest bar shared by every symbol?      (`n_laggards`)
    A sample that agrees is certified. A panel whose newest bar belongs to a
    handful of symbols is a separate, human-actionable fact that no 40-of-5222
    read would ever surface -- and the board's tail number is exactly what the
    frozen-lineage docs quote, so it has to be checkable.
    """
    rows = []
    for spec in (lanes if lanes is not None else LANES):
        pc = spec.get("panel_csv")
        if not pc:
            continue
        d = os.path.join(root, pc["dir"])
        pattern = pc.get("pattern", "*.csv")
        t0 = dt.datetime.now()
        full, finfo = panel_tail_csv_full(d, pattern, laggard_cap=laggard_cap)
        sample, sinfo = panel_tail_csv(d, pattern)
        rows.append({
            "lane": spec["lane"],
            "dir": pc["dir"],
            "full_tail": str(full) if full else None,
            "sample_tail": str(sample) if sample else None,
            "agree": bool(full == sample),
            # The sample is a subset, so full >= sample always: a sample can
            # only ever be too pessimistic, never too optimistic. Both facts are
            # published anyway, because "the reader was told 10-13" and "the file
            # says 10-19" are two different sentences even when the second one
            # is the more flattering of the two.
            "direction": ("agree" if full == sample else
                          ("sample_understated" if full and sample and full > sample
                           else "sample_overstated")),
            "files": finfo.get("files", 0),
            "files_read": finfo.get("per_file", 0),
            "files_read_by_sample": sinfo.get("per_file", 0),
            "sample_disclosed": bool(sinfo.get("sampled")),
            "unread": finfo.get("unread", 0),
            "n_laggards": finfo.get("n_laggards", 0),
            # How many symbols actually carry the newest bar. A tail held by two
            # of 5,222 files is not a statement about the panel.
            "tail_holders": finfo.get("per_file", 0) - finfo.get("n_laggards", 0),
            "tail_holder_share": (round((finfo.get("per_file", 0)
                                         - finfo.get("n_laggards", 0))
                                        / float(finfo.get("per_file", 1)), 4)
                                  if finfo.get("per_file") else None),
            "laggards": finfo.get("laggards", []),
            "laggards_truncated": finfo.get("laggards_truncated", False),
            "elapsed_sec": round((dt.datetime.now() - t0).total_seconds(), 2),
        })
        # A tail held by under a tenth of the panel is quoted in the docs as
        # "the panel's tail", so it has to be flagged where the number is made.
        _share = rows[-1]["tail_holder_share"]
        rows[-1]["thin_tail"] = bool(_share is not None and _share < THIN_TAIL_SHARE)
    disagreed = [r["lane"] for r in rows if not r["agree"]]
    if not rows:
        verdict = "no_panels_declared"
    elif any(r["direction"] == "sample_overstated" for r in rows):
        verdict = "sample_overstated"
    elif disagreed:
        verdict = "sample_understated"
    else:
        verdict = "certified"
    return rows, verdict


def render_cert_md(report):
    out = ["# Panel tail certification", "",
           f"As of {report['as_of']}. The board reads the big per-symbol panels "
           "through a 40-file sample; this reads every file and says whether the "
           "sample got the same answer — and how many symbols actually hold the "
           "newest bar.", "",
           f"Verdict: **{report['verdict']}** — "
           f"{report['counts']['lanes']} panel(s), "
           f"{report['counts']['files_scanned']} file(s) scanned.", "",
           "| lane | full tail | sample tail | agree | files read | symbols holding the newest bar |",
           "|---|---|---|---|---|---|"]
    for r in report["lanes"]:
        out.append("| {lane} | {full} | {sample} | {agree} | {read}/{files} | {hold} ({share}) |".format(
            lane=r["lane"], full=r["full_tail"] or "--",
            sample=r["sample_tail"] or "--",
            agree="yes" if r["agree"] else "**no** (%s)" % r["direction"],
            read=r["files_read"], files=r["files"],
            hold=r["tail_holders"],
            share=("--" if r["tail_holder_share"] is None
                   else "%.2f%%" % (100.0 * r["tail_holder_share"]))))
    thin = [r for r in report["lanes"] if r.get("thin_tail")]
    out.append("")
    if thin:
        out.append("## The newest bar is held by a handful of symbols")
        out.append("")
        out.append("A tail that only a few files reach is not a statement about the "
                   "panel; it is one symbol's last bar quoted as the panel's.")
        out.append("")
        for r in thin:
            out.append(f"- **{r['lane']}**: `{r['full_tail']}` is held by "
                       f"{r['tail_holders']} of {r['files']} symbols "
                       f"({100.0 * r['tail_holder_share']:.2f}%); "
                       f"{r['n_laggards']} sit behind it.")
    behind = [r for r in report["lanes"] if r["n_laggards"]]
    out.append("")
    if behind:
        out.append("## Symbols whose last bar is behind the panel's newest bar")
        out.append("")
        for r in behind:
            names = ", ".join(r["laggards"])
            more = " …" if r["laggards_truncated"] else ""
            out.append(f"- **{r['lane']}** ({r['n_laggards']} of {r['files']}): {names}{more}")
    else:
        out.append("Every declared panel has one tail shared by all of its symbols.")
    out.append("")
    return "\n".join(out)


def certify(now=None, lanes=None, root=ROOT, write=True):
    now = now or dt.datetime.now()
    rows, verdict = certify_rows(lanes, root)
    report = {
        "as_of": now.isoformat(timespec="seconds"),
        "verdict": verdict,
        "thin_tail_share": THIN_TAIL_SHARE,
        "counts": {
            "lanes": len(rows),
            "files_scanned": sum(r["files"] for r in rows),
            "sample_disagreed": len([r for r in rows if not r["agree"]]),
            "lanes_with_laggards": len([r for r in rows if r["n_laggards"]]),
            "thin_tails": len([r for r in rows if r["thin_tail"]]),
        },
        "lanes": rows,
    }
    for r in rows:
        print(f"{'certified' if r['agree'] else 'UNDERSTATED':>10}  {r['lane']:<14} "
              f"full={r['full_tail'] or '--':<11} sample={r['sample_tail'] or '--':<11} "
              f"files={r['files_read']}/{r['files']} "
              f"holders={r['tail_holders']} laggards={r['n_laggards']}"
              f"{' THIN' if r['thin_tail'] else ''}",
              flush=True)
    print(f"verdict={verdict} counts={report['counts']}", flush=True)
    if write:
        os.makedirs(os.path.dirname(CERT_PATH), exist_ok=True)
        tmp = CERT_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=1)
        os.replace(tmp, CERT_PATH)
        os.makedirs(os.path.dirname(CERT_MD_PATH), exist_ok=True)
        with open(CERT_MD_PATH, "w", encoding="utf-8") as f:
            f.write(render_cert_md(report))
    return 0 if verdict in ("certified", "no_panels_declared") else 3


def run(now=None, allow_network=False):
    days = load_calendar(CAL_PATH)
    if not days:
        print("MECHANISM FAIL: no official calendar at "
              f"{os.path.relpath(CAL_PATH, ROOT)}", flush=True)
        return 2
    now = now or dt.datetime.now()
    report = audit(days, now)
    # r1265: every lane above is judged on the official TRADING calendar. A lane
    # whose unit is a statutory REPORT PERIOD therefore has no row here at all,
    # so on 2026-11-07 the 2026Q3 disclosure deadline had been missed for a week
    # and the board was silent about it -- that debt was visible only to whoever
    # happened to run the collector by hand (r1263).
    report["period_lanes"] = audit_period_lanes(now)
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
    # D-20261108-14 acceptance: the printed face itself must carry the union
    # width and the silent owners, not only the JSON/MD. A board whose stdout
    # says "15 lanes" without saying 11 registry + 4 map-only lets a reader
    # believe the map was read when it was not.
    cov = report.get("coverage") or {}
    print(f"lanes={report.get('n_lanes')} "
          f"(registry={cov.get('registry_lanes')} "
          f"+lane_hosts_union={cov.get('lane_hosts_union_lanes')} "
          f"declared_writers={cov.get('declared_writers')})", flush=True)
    for host in report.get("hosts_down") or []:
        h = (report.get("hosts") or {}).get(host) or {}
        print(f"SILENT-HOST-DOWN {host} age_h={h.get('age_h')} "
              f"unverifiable="
              f"{','.join(h.get('lanes_unverifiable') or []) or '-'}", flush=True)
    for host in report.get("hosts_silent") or []:
        h = (report.get("hosts") or {}).get(host) or {}
        print(f"SILENT-OWNER {host} age_h={h.get('age_h')} "
              f"lanes={','.join(h.get('silent_lanes') or []) or '-'}", flush=True)
    print(f"verdict={report['verdict']} counts={report['counts']} "
          f"worst={report['worst']}", flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "selftest", "show", "certify"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "certify":
        return certify()
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