"""Data-lane freshness board -- union coverage plus a separate owner-silence alarm.

Why this exists (OB-20261108-120628-589 leg 1, from D-20261108-02): nine collectors are assigned to
bm-b in ``config/lane_hosts.json`` while the freshness measures that existed here (the data/daily
coverage census and the exchange-calendar audit) know nothing about lanes at all.  The cost of that
gap is concrete and asymmetric: a lane nobody measures looks exactly like a lane that has no data,
so "no data" and "nobody is looking" are the same reading.  This module is the standing measure:

  * COVERAGE -- the observed set is the UNION of every lane named in ``config/lane_hosts.json`` and
    every collector lane declared in ``LANE_SPECS`` below.  A lane that is assigned but has no data
    face here is published as ``no_evidence``, never silently dropped from the denominator.
  * TWO ALARMS, NEVER ONE FLAG -- ``lane_starved`` is a statement about a data face (missing, or
    older than its peers by more than LAG_DAYS); ``owner_silent`` is a statement about a machine
    (its heartbeat is older than OWNER_SILENT_HOURS and lane_hosts.json gives it lanes).  Silence is
    not starvation: a silent owner whose lanes are fresh is a governance reading, and a fresh owner
    whose lane is starved is a broken lane.  Merging them hides whichever one happens second.
  * REFERENCE = THE PEERS, NOT THE WALL CLOCK -- every lane's lag is published twice: against the
    newest content date across all lanes (``lag_vs_face_max``, used for the starvation verdict) and
    against today (``behind_today_days``, context only).  A machine-wide gap must be published as
    one gap, not as sixteen starved lanes.
  * EVIDENCE TIER IS NAMED -- ``content_date`` (a date read out of the data), ``declared_cutoff``
    (a sidecar the collector writes) or ``mtime_only`` (a checkout artefact -- E453: in a git clone
    every mtime is the checkout time, so mtime is never evidence about the data).  Nothing is
    graded without saying which of the three it came from.

Read-only, zero network, zero engine, zero judgement about strategy: it counts dates already on
disk and reads heartbeats that other processes wrote.  Writes only results/data_lane_freshness.json.

Usage:
  python scripts/data_lane_freshness.py run
  python scripts/data_lane_freshness.py check
  python scripts/data_lane_freshness.py selftest
"""
from __future__ import annotations

import glob
import io
import json
import os
import re
import sys
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from panel_coverage_report import last_bar_date  # noqa: E402  (reuse, do not re-derive)

OUT_JSON = os.path.join(ROOT, "results", "data_lane_freshness.json")
LANE_HOSTS = os.path.join(ROOT, "config", "lane_hosts.json")
MACHINES = os.path.join(ROOT, "fleet", "machines")

LAG_DAYS = 3
OWNER_SILENT_HOURS = 24
MAX_FILES = 3000

# lane stem -> (data face relative to the repo root, glob, evidence mode)
# mode: "last_bar" reads a date out of the last data row; "last_stamp" takes the first 10 characters
# of the last row's first field (a minute feed stamps its rows with a datetime); "filename_date"
# reads the date out of the file names (one file per day); "declared_cutoff" reads a sidecar the
# collector writes; "mtime_only" is a checkout artefact and is published as such.
LANE_SPECS = {
    "update_daily": ("data/daily", "*.csv", "last_bar"),
    "update_etf_daily": ("data/daily", "*.csv", "last_bar"),
    "update_futures": ("data/futures_daily", "*.csv", "last_bar"),
    "update_astock_daily": ("data/astock_daily/per", "*.csv", "last_bar"),
    "update_minute_feed": ("data/minute_feed", "*.csv", "last_stamp"),
    "update_lhb": ("Money02/data/lhb", "*.parquet", "mtime_only"),
    "update_moneyflow": ("data/moneyflow/per", "*.csv", "last_bar"),
    "update_heat": ("data/heat/popularity", "*.json", "filename_date"),
    "ah_panel_puller": ("data/ah_panel/per", "*.csv", "last_bar"),
    "update_fund_statements": ("data/fund_statement_export", "*.parquet", "declared_cutoff"),
    "update_fundamental": ("data/fundamental", "eligibility.csv", "mtime_only"),
    "update_options": ("data/options/daily", "*.csv", "last_bar"),
    "update_repo": ("data/repo_daily", "*.csv", "last_bar"),
    "update_sina_mf": ("data/sina_mf/per", "*.csv", "last_bar"),
    "update_ths_panel": ("data/ths_ggzjl/daily", "*.csv", "filename_date"),
    "update_zt_pool": ("data/zt_pool", "*.parquet", "declared_cutoff"),
}

EVIDENCE_VOCAB = ("content_date", "declared_cutoff", "mtime_only", "no_evidence")
CUTOFF_KEYS = ("cutoff", "evidence_cutoff", "complete_through", "last_bar", "collected_days")

V_OK = "no_lane_is_starved_and_no_owner_is_silent"
V_STARVED = "at_least_one_lane_s_data_face_is_missing_or_older_than_its_peers"
V_OWNER = "at_least_one_owner_is_silent_over_the_lanes_it_is_assigned"
V_BOTH = "both_a_starved_lane_and_a_silent_owner_are_published_separately"
VERDICT_VOCAB = (V_OK, V_STARVED, V_OWNER, V_BOTH)


def _now():
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def _rel(path, root=None):
    return os.path.relpath(path, root or ROOT).replace(os.sep, "/")


def _read_json(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")
COMPACT_DATE_RE = re.compile(r"(\d{4})(\d{2})(\d{2})")


def _dates_of(payload):
    """Every ISO date string anywhere in a sidecar payload, sorted.

    A sidecar such as ``collected_days.json`` keeps its dates inside a per-panel list rather than
    under a field called "cutoff", so the scan looks at values as well as at cutoff-named keys -- a
    key-name-only scan reports "no cutoff" for a file that is entirely dates.
    """
    found = []

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if isinstance(value, str) and key in CUTOFF_KEYS and ISO_DATE_RE.match(value):
                    found.append(value[:10])
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
        elif isinstance(node, str) and ISO_DATE_RE.match(node):
            found.append(node[:10])

    walk(payload)
    return sorted(set(found))


def last_stamp(path):
    """First 10 characters of the last data row's first field, when the row carries a datetime."""
    try:
        with io.open(path, "rb") as fh:
            fh.seek(0, os.SEEK_END)
            size = fh.tell()
            fh.seek(max(0, size - 512))
            tail = fh.read().decode("utf-8", "replace")
        for line in reversed(tail.splitlines()):
            head = line.split(",")[0].strip()
            if ISO_DATE_RE.match(head):
                return head[:10]
    except OSError:
        return None
    return None


def filename_date(files):
    """The newest date spelled in a file name (2026-10-27.csv or 20261027.json)."""
    best = None
    for path in files:
        name = os.path.basename(path)
        if ISO_DATE_RE.match(name):
            got = name[:10]
        else:
            found = COMPACT_DATE_RE.search(os.path.splitext(name)[0])
            if not found:
                continue
            got = "%s-%s-%s" % (found.group(1), found.group(2), found.group(3))
        if best is None or got > best:
            best = got
    return best


def evidence(root, stem, spec):
    """What this lane's own data face says, and which tier said it."""
    rel_dir, pattern, mode = spec
    full = os.path.join(root, rel_dir)
    out = {"lane": stem, "face": rel_dir, "pattern": pattern, "mode": mode,
           "evidence_tier": "no_evidence", "date": None, "files": 0, "files_read": 0,
           "sampled": False, "note": None}
    if not os.path.isdir(full):
        out["note"] = "the declared data face does not exist"
        return out
    files = sorted(glob.glob(os.path.join(full, pattern)))
    out["files"] = len(files)
    if not files:
        out["note"] = "the declared data face holds no file matching its pattern"
        return out
    if mode == "last_bar":
        read = files
        if len(files) > MAX_FILES:
            step = len(files) / float(MAX_FILES)
            read = [files[int(i * step)] for i in range(MAX_FILES)]
            out["sampled"] = True
        best = None
        for path in read:
            got = last_bar_date(path)
            if got and (best is None or got > best):
                best = got
        out["files_read"] = len(read)
        if best:
            out["evidence_tier"] = "content_date"
            out["date"] = best
        else:
            out["note"] = "no readable date in the sampled files"
        return out
    if mode == "last_stamp":
        best = None
        for path in files:
            got = last_stamp(path)
            if got and (best is None or got > best):
                best = got
        out["files_read"] = len(files)
        if best:
            out["evidence_tier"] = "content_date"
            out["date"] = best
        else:
            out["note"] = "no row of this data face is stamped with a date"
        return out
    if mode == "filename_date":
        best = filename_date(files)
        out["files_read"] = 0
        if best:
            out["evidence_tier"] = "content_date"
            out["date"] = best
        else:
            out["note"] = "no file name in this data face spells a date"
        return out
    if mode == "declared_cutoff":
        best = None
        sidecars = sorted(glob.glob(os.path.join(full, "*.json")))
        for path in sidecars:
            try:
                payload = _read_json(path)
            except (OSError, ValueError):
                continue
            dates = _dates_of(payload)
            if dates and (best is None or dates[-1] > best):
                best = dates[-1]
        if best:
            out["evidence_tier"] = "declared_cutoff"
            out["date"] = best
        elif files:
            newest = max(os.path.getmtime(p) for p in files)
            out["evidence_tier"] = "mtime_only"
            out["date"] = datetime.fromtimestamp(newest).astimezone().date().isoformat()
            out["note"] = ("the lane publishes no cutoff sidecar; the date is this checkout's "
                           "mtime and is not evidence about the data")
        return out
    newest = max(os.path.getmtime(p) for p in files)
    out["evidence_tier"] = "mtime_only"
    out["date"] = datetime.fromtimestamp(newest).astimezone().date().isoformat()
    return out


def lane_hosts(root):
    """lane stem -> owner machine, or an empty map when the file is absent or unreadable."""
    path = os.path.join(root, "config", "lane_hosts.json")
    try:
        payload = _read_json(path)
    except (OSError, ValueError):
        return {}, "config/lane_hosts.json is absent or unreadable; in-code defaults apply"
    hosts = payload.get("lane_hosts") or {}
    return {str(k): str(v) for k, v in hosts.items()}, None


def owner_silence(root, hosts, now=None):
    """One row per declared owner: how old its heartbeat is, and whether that is silence."""
    now = now or datetime.now().astimezone()
    rows = []
    for owner in sorted(set(hosts.values())):
        lanes = sorted(stem for stem, who in hosts.items() if who == owner)
        path = os.path.join(root, "fleet", "machines", "%s.json" % owner)
        row = {"owner": owner, "lanes_defined": lanes, "heartbeat": None,
               "age_hours": None, "silent": None, "note": None}
        try:
            payload = _read_json(path)
        except (OSError, ValueError):
            row["silent"] = None
            row["note"] = "no readable heartbeat for this owner"
            rows.append(row)
            continue
        stamp = payload.get("last_seen") or payload.get("ts")
        row["heartbeat"] = stamp
        try:
            seen = datetime.fromisoformat(str(stamp))
            if seen.tzinfo is None:
                seen = seen.replace(tzinfo=now.tzinfo)
        except ValueError:
            row["note"] = "the heartbeat stamp does not parse"
            rows.append(row)
            continue
        hours = round((now - seen).total_seconds() / 3600.0, 2)
        row["age_hours"] = hours
        row["silent"] = hours > OWNER_SILENT_HOURS
        rows.append(row)
    return rows


def measure(root=None, now=None):
    root = root or ROOT
    hosts, hosts_note = lane_hosts(root)
    union = sorted(set(hosts) | set(LANE_SPECS))
    lanes = []
    for stem in union:
        spec = LANE_SPECS.get(stem)
        if spec is None:
            lanes.append({"lane": stem, "face": None, "pattern": None, "mode": None,
                          "evidence_tier": "no_evidence", "date": None, "files": 0,
                          "files_read": 0, "sampled": False,
                          "owner": hosts.get(stem),
                          "in_lane_hosts": True, "declared_face_here": False,
                          "note": "assigned in lane_hosts.json but this repo declares no data face "
                                  "for it, so coverage is unknown rather than zero"})
            continue
        row = evidence(root, stem, spec)
        row["owner"] = hosts.get(stem)
        row["in_lane_hosts"] = stem in hosts
        row["declared_face_here"] = True
        lanes.append(row)

    dated = [r for r in lanes if r.get("date") and r["evidence_tier"] != "mtime_only"]
    face_max = max((r["date"] for r in dated), default=None)
    face_max_any = max((r["date"] for r in lanes if r.get("date")), default=None)
    today = (now or datetime.now().astimezone()).date().isoformat()
    for r in lanes:
        if r.get("date") and face_max and r["evidence_tier"] != "mtime_only":
            r["lag_vs_face_max"] = (date(*[int(x) for x in face_max.split("-")])
                                    - date(*[int(x) for x in r["date"].split("-")])).days
        else:
            r["lag_vs_face_max"] = None
        if r.get("date"):
            r["behind_today_days"] = (date(*[int(x) for x in today.split("-")])
                                      - date(*[int(x) for x in r["date"].split("-")])).days
        else:
            r["behind_today_days"] = None
        if r["evidence_tier"] == "mtime_only":
            # E453: in a git clone every mtime is the checkout time, so grading a lane on it would
            # either declare a stale face fresh or a fresh face stale. Third bucket, not a guess.
            r["starved"] = None
            r["undateable_reason"] = ("the face carries no date the data itself supplies; its file "
                                      "mtimes are this checkout's, not the data's")
        else:
            r["undateable_reason"] = None
            r["starved"] = (r["evidence_tier"] == "no_evidence"
                            or (r["lag_vs_face_max"] is not None
                                and r["lag_vs_face_max"] > LAG_DAYS))

    owners = owner_silence(root, hosts, now)
    starved = [r["lane"] for r in lanes if r["starved"] is True]
    undateable = [r["lane"] for r in lanes if r["starved"] is None]
    silent = [r["owner"] for r in owners if r["silent"] is True]
    machine_gap = None
    if face_max:
        machine_gap = (date(*[int(x) for x in today.split("-")])
                       - date(*[int(x) for x in face_max.split("-")])).days
    summary = {
        "union_lanes": len(union),
        "lanes_in_lane_hosts": len(hosts),
        "lanes_declared_besides": len(set(LANE_SPECS) - set(hosts)),
        "lanes_assigned_without_a_data_face": sum(
            1 for r in lanes if not r["declared_face_here"]),
        "lanes_dated_by_the_data": len(dated),
        "lanes_by_evidence_tier": {tier: sum(1 for r in lanes if r["evidence_tier"] == tier)
                                   for tier in EVIDENCE_VOCAB},
        "lanes_starved": len(starved),
        "lanes_starved_ids": starved,
        "lanes_undateable": len(undateable),
        "lanes_undateable_ids": undateable,
        "owners_declared": len(set(hosts.values())),
        "owners_silent": len(silent),
        "owners_silent_ids": silent,
        "alarms_are_separate": True,
        "alarm_note": ("lane_starved is a statement about a data face, owner_silent is a statement "
                       "about a machine, and lanes_undateable is a statement about the evidence: "
                       "neither implies the other and they are never merged into one flag"),
        "reference_date": today,
        "face_max": face_max,
        "face_max_including_checkout_mtimes": face_max_any,
        "machine_gap_days": machine_gap,
        "machine_wide_gap": (machine_gap is not None and machine_gap > LAG_DAYS),
        "lag_days": LAG_DAYS,
        "owner_silent_hours": OWNER_SILENT_HOURS,
        "lane_hosts_note": hosts_note,
    }
    return {
        "schema": "data-lane-freshness/v1",
        "generated": _now(),
        "evidence_cutoff": face_max,
        "population_source": ("config/lane_hosts.json lane stems UNION the LANE_SPECS declared in "
                              "%s; every assigned lane is published whether or not a data face "
                              "exists for it" % os.path.basename(__file__)),
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "lanes": lanes,
        "owners": owners,
        "method_limits": [
            "the union is only as complete as lane_hosts.json and this module's table: a collector "
            "that exists in the S6 chain but is named in neither place is outside the denominator",
            "a lane with no declared face is published as coverage-unknown, not as zero files, so "
            "the union count is larger than the number of lanes this board can actually date",
            "starvation is judged against the peers' newest content date; a machine-wide stop is "
            "published once as machine_wide_gap rather than as one alarm per lane",
            "mtime_only evidence is a checkout artefact (E453): in a git clone every file mtime is "
            "the checkout time, so a lane graded that way is not evidence about its data",
            "the owner-silence leg reads fleet/machines/<owner>.json only; a machine that writes no "
            "heartbeat at all is published as silent=null (unmeasured) rather than silent",
        ],
    }


def _verdict(summary):
    starved = summary["lanes_starved"] > 0
    silent = summary["owners_silent"] > 0
    if starved and silent:
        return V_BOTH
    if starved:
        return V_STARVED
    if silent:
        return V_OWNER
    return V_OK


def write(face, root=None):
    path = os.path.join(root or ROOT, "results", "data_lane_freshness.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True))
        fh.write("\n")
    return _rel(path, root)


def face_problems(face):
    problems = []
    for key in ("schema", "generated", "population_source", "summary", "verdict", "lanes",
                "owners", "method_limits", "verdict_vocab"):
        if key not in face:
            problems.append("missing key %s" % key)
    if problems:
        return problems
    summary, lanes, owners = face["summary"], face["lanes"], face["owners"]
    if summary["union_lanes"] != len(lanes):
        problems.append("union_lanes does not equal the lane rows")
    tiers = {tier: sum(1 for r in lanes if r.get("evidence_tier") == tier)
             for tier in face["verdict_vocab"] and EVIDENCE_VOCAB}
    if tiers != summary["lanes_by_evidence_tier"]:
        problems.append("lanes_by_evidence_tier does not re-derive from the lane rows")
    if summary["lanes_assigned_without_a_data_face"] != sum(
            1 for r in lanes if not r.get("declared_face_here")):
        problems.append("lanes_assigned_without_a_data_face does not re-derive")
    starved = [r["lane"] for r in lanes if r.get("starved") is True]
    if summary["lanes_starved_ids"] != starved:
        problems.append("lanes_starved_ids does not re-derive from the lane rows")
    if summary["lanes_starved"] != len(starved):
        problems.append("lanes_starved does not re-derive")
    undateable = [r["lane"] for r in lanes if r.get("starved") is None]
    if summary["lanes_undateable_ids"] != undateable:
        problems.append("lanes_undateable_ids does not re-derive from the lane rows")
    if summary["lanes_undateable"] != len(undateable):
        problems.append("lanes_undateable does not re-derive")
    silent = [r["owner"] for r in owners if r.get("silent") is True]
    if summary["owners_silent_ids"] != silent:
        problems.append("owners_silent_ids does not re-derive from the owner rows")
    if summary["owners_silent"] != len(silent):
        problems.append("owners_silent does not re-derive")
    for row in lanes:
        if row.get("evidence_tier") not in EVIDENCE_VOCAB:
            problems.append("lane %s carries evidence_tier %r"
                            % (row.get("lane"), row.get("evidence_tier")))
        if row.get("starved") is None:
            if row.get("evidence_tier") != "mtime_only":
                problems.append("lane %s publishes no starvation reading without saying why"
                                % row.get("lane"))
            if not row.get("undateable_reason"):
                problems.append("lane %s is undateable without a reason" % row.get("lane"))
        elif row.get("undateable_reason"):
            problems.append("lane %s carries an undateable reason but is graded" % row.get("lane"))
        if not row.get("declared_face_here") and row.get("evidence_tier") != "no_evidence":
            problems.append("lane %s has no declared face but publishes evidence"
                            % row.get("lane"))
        if row.get("evidence_tier") == "no_evidence" and row.get("date"):
            problems.append("lane %s publishes a date with no evidence" % row.get("lane"))
    if not summary.get("alarms_are_separate"):
        problems.append("the two alarms are merged")
    if face["verdict"] != _verdict(summary):
        problems.append("verdict does not re-derive from the summary")
    if face["verdict"] not in face["verdict_vocab"]:
        problems.append("verdict is outside the vocabulary")
    return problems


def check(root=None):
    path = os.path.join(root or ROOT, "results", "data_lane_freshness.json")
    try:
        face = _read_json(path)
    except (OSError, ValueError) as exc:
        print("check: cannot read %s (%s)" % (_rel(path, root), exc.__class__.__name__))
        return 1
    problems = face_problems(face)
    print("check: problems=%s" % json.dumps(problems, ensure_ascii=False)[:600])
    return 0 if not problems else 1


FIXTURE_LANES = {
    "lane_fresh": ("panels/fresh", "*.csv", "last_bar"),
    "lane_stale": ("panels/stale", "*.csv", "last_bar"),
    "lane_empty": ("panels/empty", "*.csv", "last_bar"),
    "lane_minute": ("feeds/minute", "*.csv", "last_stamp"),
    "lane_named": ("feeds/named", "*.json", "filename_date"),
    "lane_checkout": ("panels/checkout", "*.csv", "mtime_only"),
}


def _write_csv(path, dates):
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("date,open\n")
        for d in dates:
            fh.write("%s,1.0\n" % d)


def selftest():
    failures = []
    import tempfile

    def arm(name, ok, detail=""):
        print(("PASS " if ok else "FAIL ") + name + (" -- " + detail if detail else ""))
        if not ok:
            failures.append(name)

    global LANE_SPECS
    saved = LANE_SPECS
    try:
        with tempfile.TemporaryDirectory() as tmp:
            for name, dates in (("fresh", ["2026-11-06", "2026-11-07"]),
                                ("stale", ["2026-10-20", "2026-10-21"])):
                os.makedirs(os.path.join(tmp, "panels", name))
                _write_csv(os.path.join(tmp, "panels", name, "sh000001.csv"), dates)
            os.makedirs(os.path.join(tmp, "panels", "empty"))
            os.makedirs(os.path.join(tmp, "feeds", "minute"))
            os.makedirs(os.path.join(tmp, "feeds", "named"))
            os.makedirs(os.path.join(tmp, "panels", "checkout"))
            _write_csv(os.path.join(tmp, "panels", "checkout", "sh600000.csv"),
                       ["2026-11-07", "2026-11-07"])
            with io.open(os.path.join(tmp, "feeds", "minute", "510300.csv"), "w",
                         encoding="utf-8", newline="\n") as fh:
                fh.write("day,open\n2026-11-06 09:31:00,1.0\n2026-11-06 15:00:00,1.0\n")
            with io.open(os.path.join(tmp, "feeds", "named", "20261107.json"), "w",
                         encoding="utf-8", newline="\n") as fh:
                fh.write("{}")
            os.makedirs(os.path.join(tmp, "config"))
            os.makedirs(os.path.join(tmp, "fleet", "machines"))
            with io.open(os.path.join(tmp, "config", "lane_hosts.json"), "w",
                         encoding="utf-8", newline="\n") as fh:
                fh.write(json.dumps({"lane_hosts": {"lane_stale": "bm-x",
                                                    "lane_assigned_only": "bm-x"}}))
            with io.open(os.path.join(tmp, "fleet", "machines", "bm-x.json"), "w",
                         encoding="utf-8", newline="\n") as fh:
                fh.write(json.dumps({"last_seen": "2026-11-01T00:00:00+08:00"}))
            LANE_SPECS = FIXTURE_LANES
            now = datetime.fromisoformat("2026-11-07T12:00:00+08:00")
            face = measure(root=tmp, now=now)
            lanes = {r["lane"]: r for r in face["lanes"]}
            arm("the observed set is the union of lane_hosts and the declared faces",
                face["summary"]["union_lanes"] == 7, str(face["summary"]["union_lanes"]))
            arm("a lane assigned in lane_hosts with no declared face is coverage-unknown",
                lanes["lane_assigned_only"]["evidence_tier"] == "no_evidence"
                and lanes["lane_assigned_only"]["declared_face_here"] is False,
                json.dumps(lanes["lane_assigned_only"]["evidence_tier"]))
            arm("a fresh lane is not starved",
                lanes["lane_fresh"]["starved"] is False
                and lanes["lane_fresh"]["evidence_tier"] == "content_date",
                json.dumps({k: lanes["lane_fresh"][k] for k in ("date", "lag_vs_face_max")}))
            arm("a lane behind its peers is starved",
                lanes["lane_stale"]["starved"] is True
                and lanes["lane_stale"]["lag_vs_face_max"] == 17,
                json.dumps({k: lanes["lane_stale"][k] for k in ("date", "lag_vs_face_max")}))
            arm("an empty data face is starved rather than zero-coverage-fresh",
                lanes["lane_empty"]["starved"] is True
                and lanes["lane_empty"]["evidence_tier"] == "no_evidence",
                json.dumps(lanes["lane_empty"]["evidence_tier"]))
            arm("a feed that stamps rows with a datetime is dated from its last row",
                lanes["lane_minute"]["evidence_tier"] == "content_date"
                and lanes["lane_minute"]["date"] == "2026-11-06"
                and lanes["lane_minute"]["starved"] is False,
                json.dumps({k: lanes["lane_minute"][k] for k in ("date", "lag_vs_face_max")}))
            arm("a one-file-per-day face is dated from its file names",
                lanes["lane_named"]["evidence_tier"] == "content_date"
                and lanes["lane_named"]["date"] == "2026-11-07",
                json.dumps(lanes["lane_named"]["date"]))
            arm("a face dated only by its file mtimes is published as undateable, not as fresh",
                lanes["lane_checkout"]["evidence_tier"] == "mtime_only"
                and lanes["lane_checkout"]["starved"] is None
                and face["summary"]["lanes_undateable_ids"] == ["lane_checkout"],
                json.dumps({"tier": lanes["lane_checkout"]["evidence_tier"],
                            "starved": lanes["lane_checkout"]["starved"]}))
            arm("a checkout mtime never becomes the reference date",
                face["summary"]["face_max"] == "2026-11-07"
                and face["summary"]["lanes_dated_by_the_data"] == 4,
                json.dumps({"face_max": face["summary"]["face_max"],
                            "dated": face["summary"]["lanes_dated_by_the_data"]}))
            arm("a silent owner is published on its own arm",
                face["summary"]["owners_silent"] == 1
                and face["summary"]["owners_silent_ids"] == ["bm-x"],
                json.dumps(face["summary"]["owners_silent_ids"]))
            arm("the two alarms are published separately",
                face["summary"]["alarms_are_separate"] is True
                and face["verdict"] == V_BOTH, json.dumps(face["verdict"]))
            arm("the machine-wide gap is published as its own reading",
                face["summary"]["machine_gap_days"] == 0
                and face["summary"]["machine_wide_gap"] is False,
                json.dumps(face["summary"]["machine_gap_days"]))
            arm("a built fixture face passes its own gate", face_problems(face) == [],
                json.dumps(face_problems(face), ensure_ascii=False)[:300])

            doctored = json.loads(json.dumps(face))
            doctored["summary"]["lanes_starved_ids"] = []
            arm("a starvation list that does not re-derive is refused",
                bool(face_problems(doctored)))

            doctored = json.loads(json.dumps(face))
            doctored["summary"]["owners_silent_ids"] = []
            arm("a silence list that does not re-derive is refused",
                bool(face_problems(doctored)))

            doctored = json.loads(json.dumps(face))
            for row in doctored["lanes"]:
                if row["lane"] == "lane_stale":
                    row["starved"] = False
            arm("a starved lane relabelled fresh is refused", bool(face_problems(doctored)))

            doctored = json.loads(json.dumps(face))
            doctored["verdict"] = "a_verdict_this_module_never_publishes"
            arm("a hand-written verdict is refused", bool(face_problems(doctored)))

            # a machine-wide stop must be one gap, not sixteen starved lanes
            for name in ("fresh", "stale"):
                _write_csv(os.path.join(tmp, "panels", name, "sh000001.csv"),
                           ["2026-09-30", "2026-10-01"])
            with io.open(os.path.join(tmp, "feeds", "minute", "510300.csv"), "w",
                         encoding="utf-8", newline="\n") as fh:
                fh.write("day,open\n2026-10-01 15:00:00,1.0\n")
            os.remove(os.path.join(tmp, "feeds", "named", "20261107.json"))
            with io.open(os.path.join(tmp, "feeds", "named", "20261001.json"), "w",
                         encoding="utf-8", newline="\n") as fh:
                fh.write("{}")
            face2 = measure(root=tmp, now=now)
            arm("a machine-wide stop is published as one gap",
                face2["summary"]["machine_wide_gap"] is True
                and not any(r["starved"] is True for r in face2["lanes"]
                            if r.get("evidence_tier") in ("content_date", "declared_cutoff")),
                json.dumps({"gap": face2["summary"]["machine_gap_days"],
                            "starved": face2["summary"]["lanes_starved_ids"]}))

            # an owner with no heartbeat at all must be unmeasured, not silent
            os.remove(os.path.join(tmp, "fleet", "machines", "bm-x.json"))
            face3 = measure(root=tmp, now=now)
            arm("an owner with no heartbeat is unmeasured rather than silent",
                face3["summary"]["owners_silent"] == 0
                and face3["owners"][0]["silent"] is None,
                json.dumps(face3["owners"][0]))
    finally:
        LANE_SPECS = saved

    arm("an unreadable lane_hosts file falls back to the declared faces",
        measure(root=os.path.join(ROOT, "_no_such_dir"))["summary"]["lanes_in_lane_hosts"] == 0)
    print("selftest: %d arms, %d failed" % (19, len(failures)))
    return 0 if not failures else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        face = measure()
        path = write(face)
        s = face["summary"]
        print("run: %s" % path)
        print("run: union_lanes=%s (lane_hosts %s + declared besides %s) dated_by_the_data=%s"
              % (s["union_lanes"], s["lanes_in_lane_hosts"],
                 s["lanes_declared_besides"], s["lanes_dated_by_the_data"]))
        print("run: assigned_without_a_data_face=%s by_tier=%s"
              % (s["lanes_assigned_without_a_data_face"],
                 json.dumps(s["lanes_by_evidence_tier"])))
        print("run: lane_starved=%s %s" % (s["lanes_starved"],
                                           json.dumps(s["lanes_starved_ids"])))
        print("run: lanes_undateable=%s %s" % (s["lanes_undateable"],
                                               json.dumps(s["lanes_undateable_ids"])))
        print("run: owner_silent=%s %s" % (s["owners_silent"],
                                           json.dumps(s["owners_silent_ids"])))
        print("run: face_max=%s machine_gap_days=%s machine_wide_gap=%s"
              % (s["face_max"], s["machine_gap_days"], s["machine_wide_gap"]))
        print("run: verdict=%s" % face["verdict"])
        return 0
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    print("unknown command %r (run|check|selftest)" % (cmd,))
    return 2


if __name__ == "__main__":
    sys.exit(main())