"""Roster vs disk, lane by lane.

r1724 fixed one lane by hand: `update_futures.local_data_cutoff()` took the MAX
tail over ten CSV files, so `TS.csv` could sit 50 sessions behind while the gate
answered "covered" -- the file was on disk but absent from the lane's roster
(`VARIETIES`), and nothing in the repo compared the two.

This face asks that question of every lane that owns a closed panel directory:

    declared roster  vs  files on disk

Three answers, and they are not the same answer:

  * `on_disk_not_declared`  -- a file nobody refreshes (the TS class). Action:
    add it to the roster (with a source) or retire the file.
  * `declared_not_on_disk`  -- a roster member with no panel. Action: fetch it
    or drop it from the roster.
  * `declared_frozen`       -- on disk, deliberately archived (v1.0/v1.1 codes
    the collector stopped collecting). NOT a defect; counted out loud so a
    reader can see it was considered rather than missed.

Unknown is not clean. A lane whose roster cannot be read prints
`ROSTER_UNREADABLE` and is excluded from the "all match" summary -- never
counted as green (r98/r1159 family: an unreadable face must not look healthy).

A lane whose panel directory holds a *shared* universe (every ETF in the market
lives in `data/daily`) has no closed roster to compare against: that row prints
`UNPLANNED_CHECK_NOT_APPLICABLE` and only the declared->disk direction is asked.
Guessing a roster there would flag 1,700 files nobody asked about.

This module is a measurement face: no network, no writes outside `results/`,
no thresholds about whether a stale member matters (that is
`data_lane_freshness`'s question, and it already answers it from the same map).

    python scripts/lane_roster_disk_audit.py run
    python scripts/lane_roster_disk_audit.py selftest
"""
from __future__ import annotations

import importlib
import io
import json
import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "lane_roster_disk_audit.json")

# lane -> where its declared member list literally lives, and which directory
# that list is supposed to cover.
#
#   scope "closed"  = the directory is this lane's own; a file outside the
#                     roster is the TS defect.
#   scope "shared"  = a market-wide universe lives here; no unplanned check.
ROSTERS = [
    {
        "lane": "futures", "writer": "update_futures",
        "module": "update_futures", "attr": "VARIETIES", "kind": "list",
        "dir": "data/futures_daily", "pattern": ".csv",
        "scope": "closed",
        "roster_source": "scripts/update_futures.py:55 VARIETIES",
    },
    {
        "lane": "repo", "writer": "update_repo",
        "module": "update_repo", "attr": "TERMS", "kind": "dict_keys",
        "dir": "data/repo_daily", "pattern": ".csv",
        "scope": "closed",
        "roster_source": "scripts/update_repo.py:64 TERMS (term -> tencent symbol)",
    },
    {
        "lane": "minute_feed", "writer": "update_minute_feed",
        "module": "update_minute_feed", "attr": "UNIVERSE", "kind": "tuple_first",
        "frozen_attr": "FROZEN_CODES", "frozen_kind": "set",
        "dir": "data/minute_feed", "pattern": ".csv",
        "scope": "closed",
        "roster_source": "scripts/update_minute_feed.py:118 UNIVERSE + :98 FROZEN_CODES",
    },
    {
        "lane": "zt_pool", "writer": "update_zt_pool",
        "module": "update_zt_pool", "attr": "ENDPOINTS", "kind": "dict_keys",
        "dir": "data/zt_pool", "pattern": ".parquet",
        "scope": "closed",
        "roster_source": "scripts/update_zt_pool.py:73 ENDPOINTS (four pool faces)",
    },
    {
        # The lane's own gate decides who is pullable: eligibility.csv is a
        # superset (B shares 2/9, Beijing 4/8/920 are skipped by design and
        # counted per bucket). Using the raw file as the roster printed 6,312
        # "declared but absent" members that the collector never intends to
        # fetch -- a flag nobody can act on (E318). Reuse the lane's function
        # instead of re-deriving the rule here (no second implementation).
        "lane": "astock_daily", "writer": "update_astock_daily",
        "module": "update_astock_daily", "kind": "universe_codes",
        "dir": "data/astock_daily/per", "pattern": ".csv",
        "scope": "closed",
        # the lane's own per-symbol attempts log: it is the only writer that
        # knows whether an absent member is queued or already quarantined
        "progress": "data/astock_daily/_progress.json",
        "roster_source": "update_astock_daily.universe_codes() over "
                        "data/fundamental/eligibility.csv (lane's own "
                        "market_of() skip rule applied)",
    },
    {
        # The lane publishes its universe as a NUMBER (`panel.universe: 254`),
        # never as names. Two equal numbers therefore cannot tell "the same 254
        # contracts" from "253 kept, 1 retired, 1 added" -- the count agrees and
        # the sets differ (same shape as r1726's "one bar date is not one panel").
        "lane": "options", "writer": "update_options",
        "kind": "status_count",
        "status": "results/options_update_status.json", "status_path": "panel.universe",
        "dir": "data/options/daily", "pattern": ".csv",
        "scope": "closed", "tracked": True,
        "roster_source": "results/options_update_status.json:panel.universe "
                        "(a count; the lane never names its 254 contracts)",
    },
    {
        # Machine-local panel (gitignored) on the lane host, so what this module
        # reads here is THIS machine's copy. The 24 members with no file are the
        # lane's own `quarantined` map in its status face, not silent gaps.
        "lane": "ah_panel", "writer": "ah_panel_puller",
        "module": "ah_panel_puller", "kind": "json_rows_fields",
        "json": "data/ah_panel/_universe_em.json", "field": "h_code",
        "status": "results/ah_panel_status.json", "quarantine_path": "quarantined",
        "laneside_path": "fresh_pairs",
        "dir": "data/ah_panel/per", "pattern": ".csv",
        "scope": "closed", "tracked": False, "owner": "bm-a",
        "roster_source": "data/ah_panel/_universe_em.json:h_code (frozen EM "
                        "mapping, 211 pairs)",
    },
    {
        # One file per trading day, not one per member: the TS question has no
        # form here, and saying "matches" would imply it had been asked.
        "lane": "heat", "writer": "update_heat",
        "kind": None,
        "dir": "data/heat/popularity", "pattern": ".json",
        "scope": "closed", "tracked": False, "owner": "bm-a", "keying": "date",
        "roster_source": "no member roster -- the directory is keyed by day "
                        "(one snapshot per trading day)",
    },
    {
        "lane": "etf_daily", "writer": "update_etf_daily",
        "module": "update_etf_daily", "attr": "MEMBERS", "kind": "list",
        "dir": "data/daily", "pattern": ".csv",
        "scope": "shared",
        "roster_source": "scripts/update_etf_daily.py:71 MEMBERS (five frozen "
                        "members; the directory itself is market-wide)",
    },
]


def display_path(path):
    """Repo-relative when on the same drive, absolute otherwise.

    `os.path.relpath` raises ValueError across drives (repo on K:, fixtures on
    C:) and that has taken three separate selftests down (r1371/r1375/r1594).
    """
    try:
        rel = os.path.relpath(path, ROOT)
    except ValueError:
        return path
    return path if rel.startswith("..") else rel


def _load_module(name):
    if name not in sys.modules:
        scripts = os.path.join(ROOT, "scripts")
        if scripts not in sys.path:
            sys.path.insert(0, scripts)
        importlib.import_module(name)
    return sys.modules[name]


def read_roster(spec):
    """-> (declared set|None, frozen set, note, extra). None = unreadable, never empty."""
    kind = spec.get("kind")
    try:
        if kind == "json_rows_fields":
            # a frozen mapping file is the lane's own declaration of who it
            # covers; the field name differs per lane so the spec carries it
            full = os.path.join(ROOT, *spec["json"].split("/"))
            with io.open(full, "r", encoding="utf-8-sig") as fh:
                doc = json.load(fh)
            rows = doc.get("rows") if isinstance(doc, dict) else None
            if not isinstance(rows, list) or not rows:
                return None, set(), f"{spec['json']} carries no rows", {}
            declared = {str(r.get(spec["field"])) for r in rows
                        if isinstance(r, dict) and r.get(spec["field"])}
            if not declared:
                return None, set(), f"{spec['json']} rows carry no {spec['field']}", {}
            extra = {"roster_rows": len(rows),
                     "roster_declared_total": doc.get("total"),
                     "roster_fetched_at": doc.get("fetched_at")}
            return declared, set(), "", extra
        if kind == "universe_codes":
            mod = _load_module(spec["module"])
            codes, buckets = mod.universe_codes()
            if not codes:
                return None, set(), "universe_codes() returned no codes", {}
            extra = {"skip_buckets": buckets,
                     "skip_note": ("eligibility rows the lane itself skips (B "
                                   "shares 2/9, Beijing 4/8/920); not counted as "
                                   "missing")}
            return {str(c) for c in codes}, set(), "", extra
        mod = _load_module(spec["module"])
        raw = getattr(mod, spec["attr"], None)
        if raw is None:
            return None, set(), f"{spec['module']}.{spec['attr']} not found", {}
        if kind == "dict_keys":
            declared = {str(k) for k in raw.keys()}
        elif kind == "tuple_first":
            declared = {str(t[0]) if isinstance(t, (tuple, list)) else str(t)
                        for t in raw}
        else:
            declared = {str(x) for x in raw}
        frozen = set()
        if spec.get("frozen_attr"):
            fz = getattr(mod, spec["frozen_attr"], None)
            if fz:
                frozen = {str(x) for x in fz}
        return declared, frozen, "", {}
    except Exception as exc:                      # noqa: BLE001 - reported, not swallowed
        return None, set(), f"{type(exc).__name__}: {exc}", {}


def scan_disk(spec, root=ROOT):
    """-> (stems set|None, note). None = directory missing, not "no files"."""
    d = os.path.join(root, *spec["dir"].split("/"))
    if not os.path.isdir(d):
        return None, f"panel directory absent ({spec['dir']})"
    suffix = spec["pattern"]
    stems = set()
    for name in os.listdir(d):
        if not name.lower().endswith(suffix):
            continue
        full = os.path.join(d, name)
        if not os.path.isfile(full):
            continue
        stem = name[: -len(suffix)]
        # the wide ETF panel names its files sh<N>, the five frozen members do not
        if spec["lane"] == "etf_daily" and stem.startswith("sh"):
            stem = stem[2:]
        stems.add(stem)
    return stems, ""


def _read_json_rel(path, root=ROOT):
    """-> (doc|None, note). A missing status face is not an empty one."""
    full = os.path.join(root, *path.split("/"))
    if not os.path.isfile(full):
        return None, f"status face absent ({path})"
    try:
        with io.open(full, "r", encoding="utf-8-sig") as fh:
            return json.load(fh), ""
    except Exception as exc:                  # noqa: BLE001 - reported, not swallowed
        return None, f"status face unreadable ({type(exc).__name__}: {exc})"


def count_only_row(spec, extra, disk, disk_note):
    """A lane that publishes a universe COUNT cannot be checked member by member.

    Returning "matches" here would be the exact defect this module exists to
    catch: `254 == 254` is also what "one retired, one added" looks like.
    """
    row = {
        "lane": spec["lane"], "writer": spec.get("writer"), "dir": spec["dir"],
        "scope": spec["scope"], "roster_source": spec.get("roster_source"),
        "declared_n": None, "disk_n": len(disk) if disk else None,
        "declared_not_on_disk": [], "on_disk_not_declared": [],
        "declared_frozen": [],
    }
    row.update(extra or {})
    if row.get("declared_count") is None or disk is None:
        row["verdict"] = ("ROSTER_UNREADABLE" if row.get("declared_count") is None
                          else "PANEL_UNREADABLE")
        row["why"] = row.get("roster_note") or disk_note
        return row
    row["declared_n"] = row["declared_count"]
    row["counts_agree"] = (row["declared_n"] == row["disk_n"])
    row["verdict"] = "MEMBER_NAMES_NOT_PUBLISHED"
    row["why"] = ("the lane publishes HOW MANY members it covers, never which ones -- "
                  "two equal numbers also describe one contract retired and another "
                  "added, so 'complete' cannot be checked by name here")
    return row


def status_disposition(spec, missing, root=ROOT):
    """Same three-way split as `missing_disposition`, but from the lane's STATUS face.

    A lane that keeps its attempts log inside its status envelope has no separate
    `_progress.json`; the fact "quarantined after N failures" is still written
    down by the lane itself, so read it there rather than inventing a threshold.
    """
    key = spec.get("quarantine_path")
    if not key or not spec.get("status"):
        return None, "this lane publishes no quarantine record"
    doc, note = _read_json_rel(spec["status"], root=root)
    if doc is None:
        return None, note
    q = doc.get(key)
    if not isinstance(q, dict):
        return None, f"status face carries no {key} map"
    quarantined, unexplained = [], []
    for code in sorted(missing):
        (quarantined if str(code) in q else unexplained).append(code)
    return {"source": f"{spec['status']}:{key}", "threshold": None,
            "quarantined": quarantined, "pending": [],
            "unexplained": unexplained}, ""


def judge(spec, declared, frozen, note, disk, disk_note):
    """Pure: (declared, frozen, disk) -> row. No IO, so the selftest can drive it."""
    row = {
        "lane": spec["lane"],
        "writer": spec.get("writer"),
        "dir": spec["dir"],
        "scope": spec["scope"],
        "roster_source": spec.get("roster_source"),
        "declared_n": None,
        "disk_n": None,
        "declared_not_on_disk": [],
        "on_disk_not_declared": [],
        "declared_frozen": [],
    }
    if declared is None or disk is None:
        row["verdict"] = "ROSTER_UNREADABLE" if declared is None else "PANEL_UNREADABLE"
        row["why"] = note or disk_note
        if declared is not None:
            row["declared_n"] = len(declared)
        if disk is not None:
            row["disk_n"] = len(disk)
        return row

    row["declared_n"] = len(declared)
    row["disk_n"] = len(disk)
    row["declared_not_on_disk"] = sorted(declared - disk)
    frozen_on_disk = sorted((frozen or set()) & disk)
    row["declared_frozen"] = frozen_on_disk
    if spec["scope"] == "closed":
        row["on_disk_not_declared"] = sorted(disk - declared - (frozen or set()))
        if row["on_disk_not_declared"]:
            row["verdict"] = "ROSTER_OMITS_DISK"
            row["why"] = ("a file sits on disk that the lane's own roster does not "
                          "name -- nobody refreshes it (the TS class)")
        elif row["declared_not_on_disk"]:
            row["verdict"] = "DECLARED_BUT_ABSENT"
            row["why"] = "a roster member has no panel file"
        else:
            row["verdict"] = "ROSTER_MATCHES_DISK"
            row["why"] = "every roster member has a file and every file is named"
    else:
        row["on_disk_not_declared"] = None
        row["verdict"] = "UNPLANNED_CHECK_NOT_APPLICABLE"
        row["why"] = ("this directory holds a market-wide universe, so an unnamed "
                      "file is not evidence of neglect; only declared->disk is asked")
        if row["declared_not_on_disk"]:
            row["verdict"] = "DECLARED_BUT_ABSENT"
            row["why"] = "a roster member has no panel file"
    return row


def missing_disposition(spec, missing, root=ROOT):
    """Split "roster member with no panel file" by who can fix it.

    A bare list of missing members is the half-red-flag trap (E318): a symbol
    quarantined after three failed refreshes will never come back on its own,
    while a queued symbol arrives at the next refresh -- the two need opposite
    actions. The lane's own attempts log is the only writer of that fact, so
    read it plus the lane's own quarantine threshold (no second implementation).

    Returns (disposition|None, note). None means "cannot say", never "fine".
    """
    path = spec.get("progress")
    if not path:
        return None, "this lane publishes no per-member attempts log"
    full = os.path.join(root, *path.split("/"))
    if not os.path.isfile(full):
        return None, f"attempts log absent ({path})"
    try:
        with io.open(full, "r", encoding="utf-8-sig") as f:
            prog = json.load(f)
    except Exception as exc:              # noqa: BLE001 - reported, not swallowed
        return None, f"attempts log unreadable ({type(exc).__name__}: {exc})"
    attempts = prog.get("attempts")
    if not isinstance(attempts, dict):
        return None, "attempts log carries no attempts map"
    try:
        threshold = int(getattr(_load_module(spec["module"]), "QUARANTINE_AT", 0))
    except Exception:                     # noqa: BLE001
        threshold = 0
    if threshold <= 0:
        return None, "the lane's quarantine threshold is unreadable"
    quarantined, pending, unexplained = [], [], []
    for code in sorted(missing):
        n = attempts.get(str(code))
        if not isinstance(n, int):
            unexplained.append(code)
        elif n >= threshold:
            quarantined.append(code)
        else:
            pending.append(code)
    return ({"threshold": threshold, "quarantined": quarantined,
             "pending": pending, "unexplained": unexplained}, "")


def _status_path_value(spec, path, root=ROOT):
    """-> (value|None, source, note). Dotted path into the lane's own status face."""
    doc, note = _read_json_rel(spec["status"], root=root)
    if doc is None:
        return None, None, note
    cur = doc
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None, None, f"{spec['status']} has no {path}"
    return cur, f"{spec['status']}:{path}", ""


def _count_extra(spec, root=ROOT):
    val, src, note = _status_path_value(spec, spec["status_path"], root=root)
    if val is None:
        return {"declared_count": None, "roster_note": note}
    if isinstance(val, bool) or not isinstance(val, int):
        return {"declared_count": None,
                "roster_note": f"{spec['status_path']} is not a count ({val!r})"}
    return {"declared_count": val, "declared_count_source": src}


def _dir_newest_bar(dir_rel, suffix, root=ROOT):
    """Newest first-column date across a CSV panel, or None.

    Member-vs-roster says nothing about TIME: `options` agreed 254/254 by count
    while every file in it stopped at 2026-09-30. The date belongs next to the
    verdict so "matches" cannot be read as "current".
    """
    d = os.path.join(root, *dir_rel.split("/"))
    if not os.path.isdir(d) or suffix != ".csv":
        return None
    newest = None
    for name in sorted(os.listdir(d))[:600]:
        if not name.lower().endswith(suffix):
            continue
        full = os.path.join(d, name)
        try:
            size = os.path.getsize(full)
            with open(full, "rb") as fh:
                fh.seek(max(0, size - 300))
                tail = fh.read().decode("utf-8", "replace").strip().splitlines()
        except OSError:
            continue
        if not tail:
            continue
        first = tail[-1].split(",")[0].strip().strip('"')[:10]
        if len(first) >= 8 and first[:4].isdigit() and (newest is None or first > newest):
            newest = first
    return newest


def build(root=ROOT, specs=None):
    rows = []
    for spec in (specs if specs is not None else ROSTERS):
        disk, disk_note = scan_disk(spec, root=root)
        if spec.get("kind") == "status_count":
            row = count_only_row(spec, _count_extra(spec, root=root), disk, disk_note)
        else:
            declared, frozen, note, extra = read_roster(spec)
            row = judge(spec, declared, frozen, note, disk, disk_note)
            row.update(extra or {})
            if row.get("declared_not_on_disk"):
                if spec.get("progress"):
                    disp, disp_note = missing_disposition(
                        spec, row["declared_not_on_disk"], root=root)
                else:
                    disp, disp_note = status_disposition(
                        spec, row["declared_not_on_disk"], root=root)
                row["missing_disposition"] = disp
                row["missing_disposition_note"] = disp_note or None
        if spec.get("keying"):
            row["keying"] = spec["keying"]
        row["panel_newest_bar"] = (_dir_newest_bar(spec["dir"], spec["pattern"], root=root)
                                   if spec.get("pattern") else None)
        # A gitignored panel belongs to the machine that wrote it; this repo
        # checkout holds one machine's copy (r1290: a shared face must say whose
        # disk it read). Neither agreement nor absence here is the lane's verdict.
        if spec.get("tracked") is False:
            row["observed_verdict"] = row["verdict"]
            row["local_copy"] = True
            row["owner"] = spec.get("owner")
            lane_n, lane_src, lane_note = (None, None, "")
            if spec.get("laneside_path"):
                lane_n, lane_src, lane_note = _status_path_value(
                    spec, spec["laneside_path"], root=root)
            row["laneside"] = {"value": lane_n, "source": lane_src,
                               "local_disk_n": row.get("disk_n"),
                               "note": lane_note or None,
                               "agree": (lane_n is not None
                                         and lane_n == row.get("disk_n"))}
            row["verdict"] = "LOCAL_COPY_ONLY"
            row["why"] = (
                f"this panel is gitignored (machine-local) and the lane is "
                f"{spec.get('owner')}'s -- what was read here is THIS machine's "
                f"copy (observed: {row['observed_verdict']}); it is not the "
                f"lane's statement about itself")
        rows.append(row)
    counts = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    defects = [r for r in rows
               if r["verdict"] in ("ROSTER_OMITS_DISK", "DECLARED_BUT_ABSENT")]
    unchecked = [r["lane"] for r in rows if r["verdict"] in (
        "ROSTER_UNREADABLE", "PANEL_UNREADABLE", "LOCAL_COPY_ONLY",
        "MEMBER_NAMES_NOT_PUBLISHED")]
    return {
        "generated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "evidence_cutoff": None,   # set by build_and_write from the newest panel
        "lanes": rows,
        "verdict_counts": counts,
        "defect_lanes": [r["lane"] for r in defects],
        "unchecked_lanes": unchecked,
        "all_closed_rosters_match": bool(rows) and not defects and not unchecked,
        "law": ("roster vs disk: a file on disk that the lane's roster does not "
                "name is refreshed by nobody (r1724 TS); a roster member with no "
                "file is a promise with no panel; unreadable is never clean; a "
                "count that agrees is not the same set; a gitignored panel is one "
                "machine's copy, not the lane's statement"),
    }


def _newest_bar(rows):
    """Newest date across audited panels, or None. Reuses the panel readers' own
    convention: last line of a CSV is the newest bar."""
    newest = None
    for spec in ROSTERS:
        d = os.path.join(ROOT, *spec["dir"].split("/"))
        if not os.path.isdir(d):
            continue
        suffix = spec["pattern"]
        for name in os.listdir(d)[:400]:
            if not name.lower().endswith(suffix) or suffix != ".csv":
                continue
            try:
                with open(os.path.join(d, name), "rb") as fh:
                    fh.seek(max(0, os.path.getsize(os.path.join(d, name)) - 400))
                    tail = fh.read().decode("utf-8", "replace").strip().splitlines()
                if not tail:
                    continue
                first = tail[-1].split(",")[0].strip().strip('"')
                if len(first) >= 8 and first[:4].isdigit():
                    cand = first[:10]
                    if newest is None or cand > newest:
                        newest = cand
            except OSError:
                continue
    return newest


def build_and_write():
    rep = build()
    rep["evidence_cutoff"] = _newest_bar(rep["lanes"])
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    os.replace(tmp, OUT)
    return rep


def render_md(rep):
    out = ["# 车道名单 vs 盘面（roster vs disk）", ""]
    out.append(f"生成：{rep['generated']}｜数据截点：{rep['evidence_cutoff'] or '读不出'}")
    out.append("")
    for r in rep["lanes"]:
        out.append(f"## {r['lane']} — {r['verdict']}")
        out.append(f"- 名单来源：{r['roster_source']}")
        if r.get("keying") == "date":
            out.append("- 这个目录按**日**命名（每个交易日一份快照），没有成员名单这项检查")
        if r.get("local_copy"):
            lane = r.get("laneside") or {}
            out.append(f"- **这份面板不入库（各机自留），车道属主＝{r.get('owner')}**："
                       f"这里读到的是本机副本，不是车道对自己的陈述")
            if lane.get("agree"):
                out.append(f"- 本机副本 {lane.get('local_disk_n')} 件＝车道自报 "
                           f"{lane.get('value')}（{lane.get('source')}）——只说明这份副本"
                           f"与它自己的刷新计数一致，不说明别的机器")
            elif lane.get("value") is not None:
                out.append(f"- 本机副本 {lane.get('local_disk_n')} 件 ≠ 车道自报 "
                           f"{lane.get('value')}（{lane.get('source')}）")
            elif lane.get("note"):
                out.append(f"- 车道自报计数读不出：{lane.get('note')}")
        if r.get("declared_count") is not None:
            out.append(f"- 名单只公布**个数** {r['declared_count']}"
                       f"（{r.get('declared_count_source')}）／盘面 {r['disk_n']} 件"
                       f"——两数{'相等' if r.get('counts_agree') else '不等'}")
        if r.get("panel_newest_bar"):
            out.append(f"- 这份面板自己的最新一根 bar：**{r['panel_newest_bar']}**"
                       f"（成员对得上不等于数据是新的）")
        out.append(f"- 名单 {r['declared_n']} / 盘面 {r['disk_n']}（{r['dir']}）")
        if r["on_disk_not_declared"]:
            out.append(f"- **盘面有、名单没有**：{', '.join(r['on_disk_not_declared'])}")
        if r["on_disk_not_declared"] is None:
            out.append("- 盘面有、名单没有：不适用（共享宇宙目录）")
        if r["declared_not_on_disk"]:
            out.append(f"- **名单有、盘面没有**：{', '.join(r['declared_not_on_disk'][:20])}")
            disp = r.get("missing_disposition")
            if disp:
                if disp["quarantined"]:
                    out.append(f"  - 已被车道隔离（连续 {disp['threshold']} 次拉取失败＝"
                               f"不会自己回来）：{', '.join(disp['quarantined'])}")
                if disp["pending"]:
                    out.append(f"  - 待拉（下次刷新会回来）：{', '.join(disp['pending'])}")
                if disp["unexplained"]:
                    out.append(f"  - 车道记录里查不到（既没拉过也没隔离）："
                               f"{', '.join(disp['unexplained'])}")
                elif not (disp["quarantined"] or disp["pending"]):
                    out.append("  - 车道记录里没有任何一只的条目")
            else:
                out.append(f"  - 无法分辨待拉还是隔离：{r['missing_disposition_note']}")
        if r["declared_frozen"]:
            out.append(f"- 已声明冻结（在盘但不采）：{', '.join(r['declared_frozen'])}")
        out.append(f"- 判词：{r['why']}")
        out.append("")
    return "\n".join(out)


def selftest():
    fails = []

    def ok(cond, msg):
        if not cond:
            fails.append(msg)

    closed = {"lane": "x", "writer": "w", "dir": "d", "scope": "closed",
              "roster_source": "unit"}
    shared = dict(closed, scope="shared")

    r = judge(closed, {"A", "B"}, set(), "", {"A", "B"}, "")
    ok(r["verdict"] == "ROSTER_MATCHES_DISK", "L1 exact match is clean")
    ok(r["on_disk_not_declared"] == [], "L1 no phantom defects")

    r = judge(closed, {"A"}, set(), "", {"A", "TS"}, "")
    ok(r["verdict"] == "ROSTER_OMITS_DISK", "L2 the TS class is named")
    ok(r["on_disk_not_declared"] == ["TS"], "L2 names the file, not a count")

    r = judge(closed, {"A", "B"}, set(), "", {"A"}, "")
    ok(r["verdict"] == "DECLARED_BUT_ABSENT", "L3 a promise with no panel")

    # frozen members are on disk on purpose -- printing them as defects is the
    # alert-nobody-can-act-on trap
    r = judge(closed, {"A"}, {"OLD"}, "", {"A", "OLD"}, "")
    ok(r["verdict"] == "ROSTER_MATCHES_DISK", "L4 declared-frozen is not a defect")
    ok(r["declared_frozen"] == ["OLD"], "L4 frozen is still printed out loud")

    # a shared universe directory has no closed roster
    r = judge(shared, {"A"}, set(), "", {"A", "B", "C"}, "")
    ok(r["verdict"] == "UNPLANNED_CHECK_NOT_APPLICABLE", "L5 shared dir is not judged")
    ok(r["on_disk_not_declared"] is None, "L5 no invented defect in a shared dir")

    # unreadable is never green
    r = judge(closed, None, set(), "ImportError: no akshare", {"A"}, "")
    ok(r["verdict"] == "ROSTER_UNREADABLE", "L6 unreadable roster is its own verdict")
    ok("ImportError" in (r["why"] or ""), "L6 says why")

    r = judge(closed, {"A"}, set(), "", None, "panel directory absent (d)")
    ok(r["verdict"] == "PANEL_UNREADABLE", "L7 missing dir is not an empty dir")

    # cross-drive display path must not raise (r1371/r1375/r1594)
    ok(display_path(os.path.join(ROOT, "results", "x.json")).startswith(("results", "K:", "/")),
       "L8 display_path survives")

    rep = build(specs=[closed])
    ok(rep["all_closed_rosters_match"] in (True, False), "L9 build runs")
    ok(isinstance(rep["verdict_counts"], dict), "L9 counts present")

    # --- E318 class: an absent member is queued or quarantined, and those two
    # need opposite actions. The split must come from the lane's own log.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "data", "x"), exist_ok=True)
        with io.open(os.path.join(td, "data", "x", "_progress.json"), "w",
                     encoding="utf-8") as f:
            json.dump({"attempts": {"A": 3, "B": 1}}, f)
        spec = dict(closed, progress="data/x/_progress.json",
                    module="lane_roster_disk_audit", kind=None)
        # threshold is read off the lane module; this module has none -> the
        # disposition must refuse to answer rather than invent one
        disp, note = missing_disposition(spec, ["A", "B"], root=td)
        ok(disp is None and "threshold" in (note or ""),
           "L10 no lane threshold -> cannot say, never 'fine'")

        class _Threshold:            # stand-in module exposing the lane constant
            QUARANTINE_AT = 3
        sys.modules["_lane_threshold_fixture"] = _Threshold
        spec["module"] = "_lane_threshold_fixture"
        disp, note = missing_disposition(spec, ["A", "B", "Z"], root=td)
        ok(disp["quarantined"] == ["A"], "L11 quarantined member is named")
        ok(disp["pending"] == ["B"], "L11 queued member is a different class")
        ok(disp["unexplained"] == ["Z"], "L11 a member with no log entry is not assumed")
        ok(note == "", "L11 readable log carries no note")

    with tempfile.TemporaryDirectory() as td:
        spec = dict(closed, progress="data/x/_progress.json", module="lane_roster_disk_audit")
        disp, note = missing_disposition(spec, ["A"], root=td)
        ok(disp is None and "absent" in note, "L12 missing log is not an empty log")
        os.makedirs(os.path.join(td, "data", "x"), exist_ok=True)
        with io.open(os.path.join(td, "data", "x", "_progress.json"), "w",
                     encoding="utf-8") as f:
            f.write("{not json")
        disp, note = missing_disposition(spec, ["A"], root=td)
        ok(disp is None and "unreadable" in note, "L12 corrupt log says so")

        spec_no = dict(closed)
        spec_no.pop("progress", None)
        disp, note = missing_disposition(spec_no, ["A"], root=td)
        ok(disp is None, "L13 a lane with no log is never judged fine")

    # --- L14-L16: a lane that publishes a COUNT, not names, cannot be green.
    spec_c = dict(closed, kind="status_count", status_path="panel.universe")
    r = count_only_row(spec_c, {"declared_count": 254}, {"a", "b"}, "")
    ok(r["verdict"] == "MEMBER_NAMES_NOT_PUBLISHED", "L14 count-only is not a match")
    ok(r["declared_n"] == 254, "L14 the published count is carried")
    r = count_only_row(spec_c, {"declared_count": 2}, {"a", "b"}, "")
    ok(r["counts_agree"] is True, "L15 equal numbers are reported as equal")
    ok(r["verdict"] != "ROSTER_MATCHES_DISK",
       "L15 equal counts still are not a set match (retire one, add one)")
    r = count_only_row(spec_c, {"declared_count": None, "roster_note": "no path"},
                       {"a"}, "")
    ok(r["verdict"] == "ROSTER_UNREADABLE" and "no path" in r["why"],
       "L16 no count at all is unreadable, not zero")

    # --- L17/L18: a gitignored panel is ONE machine's copy.
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "data", "p"), exist_ok=True)
        for n in ("A.csv", "B.csv"):
            io.open(os.path.join(td, "data", "p", n), "w").close()

        class _ListFixture:                 # stand-in lane roster
            MEMBERS = ["A"]
        sys.modules["_lane_local_fixture"] = _ListFixture
        spec_l = {"lane": "loc", "writer": "w", "dir": "data/p", "pattern": ".csv",
                  "scope": "closed", "tracked": False, "owner": "bm-a",
                  "module": "_lane_local_fixture", "attr": "MEMBERS", "kind": "list",
                  "roster_source": "unit"}
        rep = build(root=td, specs=[spec_l])
        r = rep["lanes"][0]
        ok(r["verdict"] == "LOCAL_COPY_ONLY", "L17 a local panel is not judged")
        ok(r["observed_verdict"] == "ROSTER_OMITS_DISK",
           "L17 what was observed is still recorded")
        ok(r["on_disk_not_declared"] == ["B"],
           "L17 the observation keeps the names, not a count")
        ok(rep["all_closed_rosters_match"] is False and rep["unchecked_lanes"] == ["loc"],
           "L17 a local copy never counts as green")
        spec_d = dict(spec_l, keying="date")
        rep = build(root=td, specs=[spec_d])
        ok(rep["lanes"][0]["keying"] == "date", "L18 a date-keyed panel says so")

    # --- L19/L20: the same three-way split, from the lane's STATUS face.
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "results"), exist_ok=True)
        with io.open(os.path.join(td, "results", "s.json"), "w", encoding="utf-8") as f:
            json.dump({"quarantined": {"X": "3 cumulative failures"}}, f)
        spec_s = dict(closed, status="results/s.json", quarantine_path="quarantined")
        disp, note = status_disposition(spec_s, ["X", "Y"], root=td)
        ok(disp and disp["quarantined"] == ["X"], "L19 quarantined member is named")
        ok(disp and disp["unexplained"] == ["Y"],
           "L19 a member with no record is not assumed quarantined")
        spec_n = dict(closed)
        disp, note = status_disposition(spec_n, ["X"], root=td)
        ok(disp is None and "no quarantine record" in note,
           "L20 a lane with no record is never judged fine")

    # --- L21: a member match says nothing about time (options: 254/254 at 09-30)
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "data", "q"), exist_ok=True)
        for name, day in (("a.csv", "2026-09-30"), ("b.csv", "2026-11-13")):
            with io.open(os.path.join(td, "data", "q", name), "w", encoding="utf-8") as f:
                f.write("date,close\n%s,1.0\n" % day)
        ok(_dir_newest_bar("data/q", ".csv", root=td) == "2026-11-13",
           "L21 newest bar is read, not assumed")
        ok(_dir_newest_bar("data/none", ".csv", root=td) is None,
           "L21 an absent panel has no date (not today)")

    total = 28
    if fails:
        for f in fails:
            print("[FAIL]", f)
        print(f"[FAIL] {len(fails)}/{total} assertions failed")
        return 1
    print(f"[PASS] selftest {total}/{total} -- roster vs disk: the TS class is "
          f"named, frozen members are not defects, unreadable is never clean")
    return 0


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    rep = build_and_write()
    print(f"lanes={len(rep['lanes'])} defects={rep['defect_lanes']} "
          f"cutoff={rep['evidence_cutoff']}")
    for r in rep["lanes"]:
        if r["verdict"] not in ("ROSTER_MATCHES_DISK",
                                "UNPLANNED_CHECK_NOT_APPLICABLE"):
            print(f"  {r['lane']}: {r['verdict']} -- {r['why']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
