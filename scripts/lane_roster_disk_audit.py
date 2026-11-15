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


def build(root=ROOT, specs=None):
    rows = []
    for spec in (specs if specs is not None else ROSTERS):
        declared, frozen, note, extra = read_roster(spec)
        disk, disk_note = scan_disk(spec, root=root)
        row = judge(spec, declared, frozen, note, disk, disk_note)
        row.update(extra or {})
        if row.get("declared_not_on_disk"):
            disp, disp_note = missing_disposition(
                spec, row["declared_not_on_disk"], root=root)
            row["missing_disposition"] = disp
            row["missing_disposition_note"] = disp_note or None
        rows.append(row)
    counts = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    defects = [r for r in rows
               if r["verdict"] in ("ROSTER_OMITS_DISK", "DECLARED_BUT_ABSENT")]
    return {
        "generated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "evidence_cutoff": None,   # set by build_and_write from the newest panel
        "lanes": rows,
        "verdict_counts": counts,
        "defect_lanes": [r["lane"] for r in defects],
        "all_closed_rosters_match": bool(rows) and not defects and not [
            r for r in rows if r["verdict"] in ("ROSTER_UNREADABLE",
                                                "PANEL_UNREADABLE")],
        "law": ("roster vs disk: a file on disk that the lane's roster does not "
                "name is refreshed by nobody (r1724 TS); a roster member with no "
                "file is a promise with no panel; unreadable is never clean"),
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

    total = 21
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
