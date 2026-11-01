"""E338 -- how long does a census face stay green, and what would pinning the population cost?

E337 showed the opt-in itself was free and the only cost the diff carried was the corpus.  That is a
population-definition claim: every census face in the E32x..E33x chain counts its population over
``e326.corpus()`` -- every ``.py`` under scripts/Tools/live/monitor/firm -- read off the *disk*.  A
face therefore re-derives only while the population does not move, and in a repo where research
lands a new script every round, "does not move" is a claim about time, not about correctness.

This study measures that claim instead of asserting it, on the repository's own history:

    landing   the commit that first added each census face (git --diff-filter=A)
    window    landing -> the next commit that touches any ``.py`` in the five producing packages
    two reads
      all        any ``.py`` touch closes the window (what the face actually sees)
      non_census any touch outside the census family closes it (what production code does)

The second reading exists because the first is a tautology once research is the loudest writer: a
study lands, its own file is a new population member, and the window closes on the next round's
research whether or not any producer changed.  Publishing only the "all" number would let this study
report a short window that its own siblings caused.

Pinning is priced on three axes, because the usual cost model (CPU seconds) is the wrong one here:

    size        the pinned commit's ``.py`` manifest (files, bytes) versus today's disk
    read time   measured ``git cat-file --batch`` over the pinned manifest versus a disk read
    dependency  a pinned population cannot be rebuilt offline and cannot be rebuilt without this
                commit's objects surviving; that is an external dependency, not a runtime cost

Usage:
    python scripts/e338_census_green_window.py run|verify|selftest
"""

import io
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-01"
FACE = "GREENWINDOW-%s.json" % TODAY
LATEST = "greenwindow_latest.json"
STUDY = "E338_census_green_window"

PATHS = ("scripts", "Tools", "live", "monitor", "firm")

# The census family: every script whose corpus() chain bottoms out in e323.corpus().  Listed, not
# discovered, because a face added after this study lands is exactly the population drift being
# measured -- a discovered list would silently include this study's own readers.
CENSUS_FAMILY = (
    "scripts/e322_residual_refusal_causes.py",
    "scripts/e323_reach_under_wider_needle.py",
    "scripts/e324_unpublished_key_causes.py",
    "scripts/e325_orphan_gate_faces.py",
    "scripts/e326_template_parameter_consumers.py",
    "scripts/e327_who_reads_a_face_through_a_pointer.py",
    "scripts/e328_quoted_number_staleness.py",
    "scripts/e329_two_vintage_binding.py",
    "scripts/e330_unpinned_choice.py",
    "scripts/e331_pointer_only_readers.py",
    "scripts/e332_invisible_tail_recovery.py",
    "scripts/e333_surviving_e3xx_conclusions.py",
    "scripts/e334_helper_repair_blast_radius.py",
    "scripts/e335_sibling_entry_point.py",
    "scripts/e336_consumer_optin_ranking.py",
    "scripts/e337_optin_executed.py",
)

ONE_ROUND_SECONDS = 600
PIN_HARD_SECONDS = 5.0

V_ROUND = "green_window_closes_inside_one_round_and_pinning_trades_a_disk_read_for_a_git_object_dependency"
V_DEPENDENT = "green_window_outlives_a_round_but_pinning_is_still_a_dependency_not_a_runtime_cost"
V_AFFORDABLE = "window_survives_a_round_and_the_pin_costs_an_object_dependency_not_cpu"
V_SELF_TERMINATING = (
    "every_window_is_closed_by_the_next_census_sibling_and_the_two_readings_coincide_because_"
    "research_ships_its_wiring_in_the_same_commit")


def say(message):
    sys.stdout.write(str(message) + "\n")
    sys.stdout.flush()


def relp(path):
    return (path or "").replace("\\", "/")


# ---------------------------------------------------------------------------------------- git access

def _git(*args, **kw):
    proc = subprocess.run(["git"] + list(args), cwd=kw.get("cwd") or ROOT,
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode not in (0, 1):
        raise RuntimeError("git %s rc=%s %s" % (" ".join(args), proc.returncode,
                                                (proc.stderr or "")[:300]))
    return proc.stdout


MARK = "\x01"


def parse_log(text):
    """Turn ``git log --format=<MARK>%H|%ct --name-status`` into py-touch events.

    Only commits that touch a ``.py`` under the producing packages survive; the rest are not
    population events at all.  Added / removed / modified are kept apart because "a new script
    landed" and "an old script was edited" are different kinds of drift and the study prices them
    separately.
    """
    events = []
    cur = None
    for line in (text or "").splitlines():
        if line.startswith(MARK):
            if cur is not None:
                events.append(cur)
            body = line[1:].strip()
            sha, _sep, ts = body.partition("|")
            cur = {"sha": sha, "ts": int(ts) if ts.strip().isdigit() else 0,
                   "added": [], "removed": [], "modified": []}
            continue
        if cur is None or not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status, path = parts[0].strip(), relp(parts[-1].strip())
        if not path.endswith(".py"):
            continue
        if status.startswith("A"):
            cur["added"].append(path)
        elif status.startswith("D"):
            cur["removed"].append(path)
        else:
            cur["modified"].append(path)
    if cur is not None:
        events.append(cur)
    return [e for e in events if e["added"] or e["removed"] or e["modified"]]


def parse_ls_tree(text):
    """``git ls-tree -r -l`` -> [(path, size)] for ``.py`` entries only."""
    rows = []
    for line in (text or "").splitlines():
        # 100644 blob <sha>   <size>\t<path>
        head, _tab, path = line.partition("\t")
        if not path:
            continue
        fields = head.split()
        if len(fields) < 4:
            continue
        size = fields[3]
        path = relp(path.strip())
        if not path.endswith(".py"):
            continue
        rows.append((path, int(size) if size.isdigit() else 0))
    return rows


def touch_events():
    """Oldest-first.  ``git log`` emits newest-first, and a window built on that order measures
    ``older - newer`` clamped at zero -- every window reads 0s and the study's headline becomes a
    tautology (found on the first burn: median 0.0s over 16/16 closed windows)."""
    out = _git("log", "--format=%s%%H|%%ct" % MARK, "--name-status", "--", *PATHS)
    events = parse_log(out)
    events.reverse()
    return events


def is_ascending(events):
    """The invariant the whole measurement rests on: commit time never decreases down the list."""
    return all(events[i]["ts"] <= events[i + 1]["ts"] for i in range(len(events) - 1))


def landing_of(rel_path):
    """The commit that first added this file (oldest, not the latest re-add)."""
    out = _git("log", "--diff-filter=A", "--format=%H|%ct", "--", rel_path)
    rows = [ln.strip() for ln in out.splitlines() if "|" in ln]
    if not rows:
        return None
    sha, _sep, ts = rows[-1].partition("|")
    return {"sha": sha, "ts": int(ts) if ts.strip().isdigit() else 0}


def pinned_manifest(sha):
    out = _git("ls-tree", "-r", "-l", sha, "--", *PATHS)
    return parse_ls_tree(out)


def disk_manifest():
    rows = []
    for sub in PATHS:
        base = os.path.join(ROOT, sub)
        for dirpath, _dirs, files in os.walk(base):
            for name in files:
                if not name.endswith(".py"):
                    continue
                full = os.path.join(dirpath, name)
                try:
                    size = os.path.getsize(full)
                except OSError:
                    size = 0
                rows.append((relp(os.path.relpath(full, ROOT)), size))
    return sorted(rows)


def read_pinned(sha, paths):
    """Time an actual ``git cat-file --batch`` read of the pinned population."""
    query = "".join("%s:%s\n" % (sha, p) for p, _s in paths)
    started = time.perf_counter()
    proc = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT, input=query.encode("utf-8"),
                          capture_output=True)
    elapsed = time.perf_counter() - started
    if proc.returncode != 0:
        return None
    return elapsed


def read_disk(paths):
    started = time.perf_counter()
    total = 0
    for p, _s in paths:
        try:
            with io.open(os.path.join(ROOT, p), "rb") as fh:
                total += len(fh.read())
        except OSError:
            pass
    return time.perf_counter() - started, total


# ---------------------------------------------------------------------------------------- the maths

def classify(event):
    if event["added"]:
        return "new_py"
    if event["removed"]:
        return "removed_py"
    return "edit_py"


def is_census_only(event):
    touched = set(event["added"]) | set(event["removed"]) | set(event["modified"])
    return bool(touched) and touched.issubset(set(CENSUS_FAMILY))


def window_from(events, idx, predicate=None, family=None):
    """The first later event satisfying ``predicate`` closes the window.

    ``idx`` is the index of the landing event in the oldest-first list.  A window with no closing
    event is published as open (``closed=False``), never as zero -- an open window and an instantly
    closed one are the two ends of the claim and must not collapse into each other.
    """
    family = set(family or ())
    start = events[idx]
    for j in range(idx + 1, len(events)):
        ev = events[j]
        if predicate is not None and not predicate(ev):
            continue
        return {
            "closed": True,
            "closing_sha": ev["sha"],
            "closing_ts": ev["ts"],
            "seconds": max(0, ev["ts"] - start["ts"]),
            "kind": classify(ev),
            "commits_between": j - idx - 1,
            "added_census": [p for p in ev["added"] if p in family],
            "touched": {
                "added": ev["added"][:8],
                "removed": ev["removed"][:8],
                "modified": ev["modified"][:8],
            },
            "touched_counts": {"added": len(ev["added"]), "removed": len(ev["removed"]),
                               "modified": len(ev["modified"])},
        }
    return {"closed": False, "closing_sha": None, "closing_ts": None, "seconds": None,
            "kind": None, "commits_between": len(events) - idx - 1,
            "added_census": [],
            "touched": {"added": [], "removed": [], "modified": []},
            "touched_counts": {"added": 0, "removed": 0, "modified": 0}}


def summarize(windows):
    closed = [w["seconds"] for w in windows if w.get("closed")]
    open_n = sum(1 for w in windows if not w.get("closed"))
    if not closed:
        return {"n": len(windows), "closed": 0, "open": open_n, "median_seconds": None,
                "min_seconds": None, "max_seconds": None, "inside_one_round": 0,
                "share_inside_one_round": None}
    closed_sorted = sorted(closed)
    mid = len(closed_sorted) // 2
    median = (closed_sorted[mid] if len(closed_sorted) % 2
              else (closed_sorted[mid - 1] + closed_sorted[mid]) / 2.0)
    inside = sum(1 for s in closed_sorted if s <= ONE_ROUND_SECONDS)
    return {"n": len(windows), "closed": len(closed), "open": open_n,
            "median_seconds": median, "min_seconds": closed_sorted[0],
            "max_seconds": closed_sorted[-1], "inside_one_round": inside,
            "share_inside_one_round": round(float(inside) / len(closed_sorted), 4)}


def coincides(rows):
    """Do the two readings close the same window in the same commit?  Measured, not assumed.

    The design intent was to separate "the research noise" from "production code moved".  If they
    coincide, the separation is vacuous and must be published as such rather than reported as two
    agreeing measurements.
    """
    both = [r for r in rows
            if r.get("window_all") and r.get("window_non_census")
            and r["window_all"]["closed"] and r["window_non_census"]["closed"]]
    same = [r for r in both if r["window_all"]["closing_sha"] == r["window_non_census"]["closing_sha"]]
    return {"compared": len(both), "same_closing_commit": len(same)}


def sibling_closed(rows):
    closed = [r for r in rows if r.get("window_all") and r["window_all"]["closed"]]
    sib = [r for r in closed if r["window_all"]["added_census"]]
    return {"closed": len(closed), "closed_by_a_census_sibling": len(sib)}


def decide(summary_all, summary_non_census, pin, coincide=None, sibling=None):
    """Frozen rule: the verdict is read off the published summaries, never typed by hand."""
    reasons = []
    median = summary_all.get("median_seconds")
    share = summary_all.get("share_inside_one_round")
    pin_seconds = pin.get("pinned_read_seconds")
    if median is None:
        return V_DEPENDENT, ["no closed window in the repository history -- nothing to price"]
    coincide = coincide or {"compared": 0, "same_closing_commit": 0}
    sibling = sibling or {"closed": 0, "closed_by_a_census_sibling": 0}
    closed_n = sibling.get("closed") or 0
    if (closed_n and coincide.get("compared") == closed_n
            and coincide.get("same_closing_commit") == closed_n
            and sibling.get("closed_by_a_census_sibling") >= 0.8 * closed_n):
        reasons.append("%s/%s windows close on a new census sibling and the two readings pick the "
                       "same commit %s/%s times -- the split measures nothing"
                       % (sibling["closed_by_a_census_sibling"], closed_n,
                          coincide["same_closing_commit"], coincide["compared"]))
        reasons.append("median window %ss, inside one round %s of %s"
                       % (int(median), summary_all.get("inside_one_round"), closed_n))
        return V_SELF_TERMINATING, reasons
    if median <= ONE_ROUND_SECONDS and (share or 0) >= 0.5:
        reasons.append("median %ss <= one round and %s of closed windows close inside it"
                       % (int(median), share))
        return V_ROUND, reasons
    if pin_seconds is None or pin_seconds >= PIN_HARD_SECONDS:
        reasons.append("median %ss outlives a round but a pinned read costs %s"
                       % (int(median), pin_seconds))
        return V_DEPENDENT, reasons
    reasons.append("median %ss outlives a round and a pinned read costs %.3fs"
                   % (int(median), pin_seconds))
    return V_AFFORDABLE, reasons


# ---------------------------------------------------------------------------------------- build

def build(root=None):
    root = root or ROOT
    events = touch_events()
    if not is_ascending(events):
        raise RuntimeError("touch events are not oldest-first -- refusing to publish a window "
                           "measured against the wrong neighbour")
    say("events (commits touching a .py in the five packages): %s" % len(events))

    rows = []
    for rel_path in CENSUS_FAMILY:
        landing = landing_of(rel_path)
        if landing is None:
            rows.append({"face": rel_path, "landing": None, "window_all": None,
                         "window_non_census": None,
                         "note": "no landing commit found -- the file is untracked or renamed"})
            continue
        idx = next((i for i, ev in enumerate(events) if ev["sha"] == landing["sha"]), None)
        if idx is None:
            # A landing commit that touches no .py under PATHS cannot happen for a census face, so
            # this is a real disagreement, published rather than smoothed over.
            rows.append({"face": rel_path, "landing": landing, "window_all": None,
                         "window_non_census": None,
                         "note": "landing commit is absent from the touch-event list"})
            continue
        all_w = window_from(events, idx, family=CENSUS_FAMILY)
        non_census_w = window_from(events, idx, predicate=lambda ev: not is_census_only(ev),
                                   family=CENSUS_FAMILY)
        rows.append({"face": rel_path, "landing": landing, "window_all": all_w,
                     "window_non_census": non_census_w, "note": None})

    usable = [r for r in rows if r.get("window_all")]
    summary_all = summarize([r["window_all"] for r in usable])
    summary_non_census = summarize([r["window_non_census"] for r in usable if r["window_non_census"]])
    coincide = coincides(rows)
    sibling = sibling_closed(rows)

    disk = disk_manifest()
    earliest = min((r["landing"] for r in rows if r.get("landing")), key=lambda r: r["ts"])
    pinned = pinned_manifest(earliest["sha"])
    pinned_read = read_pinned(earliest["sha"], pinned)
    disk_seconds, disk_bytes = read_disk(disk)
    oldest_bytes = sum(s for _p, s in pinned)
    pin = {
        "sha": earliest["sha"],
        "why_this_commit": "the oldest census landing in the family (e322)",
        "files": len(pinned),
        "bytes": oldest_bytes,
        "disk_files": len(disk),
        "disk_bytes": disk_bytes,
        "file_delta": len(disk) - len(pinned),
        "byte_delta": disk_bytes - oldest_bytes,
        "dependency": ("a pinned population is only reproducible while this commit's blobs survive "
                       "and git is available; the measured read is cheap, so the price of pinning "
                       "is an object dependency, not CPU"),
    }

    per_face_pin = []
    for row in usable:
        landing = row.get("landing")
        if not landing:
            continue
        man = pinned_manifest(landing["sha"])
        size = sum(s for _p, s in man)
        per_face_pin.append({
            "face": row["face"],
            "landing_sha": landing["sha"],
            "pinned_files": len(man),
            "pinned_bytes": size,
            "files_vs_today": len(disk) - len(man),
            "bytes_vs_today": disk_bytes - size,
        })

    verdict, reasons = decide(summary_all, summary_non_census,
                              {"pinned_read_seconds": pinned_read}, coincide, sibling)

    doc = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "definition": {
            "population": "every .py under scripts/Tools/live/monitor/firm (e323.corpus())",
            "window_start": "the commit that first added the census face",
            "window_end": "the next commit that touches a .py in the population",
            "one_round_seconds": ONE_ROUND_SECONDS,
            "two_readings": ["all .py touches", "touches outside the census family"],
        },
        "population": {
            "commits_touching_py": len(events),
            "disk_py_files": len(disk),
            "disk_py_bytes": sum(s for _p, s in disk),
            "census_family_size": len(CENSUS_FAMILY),
        },
        "faces": rows,
        "summary_all": summary_all,
        "summary_non_census": summary_non_census,
        "readings_coincide": coincide,
        "windows_closed_by": sibling,
        "pin": pin,
        "per_face_pin": per_face_pin,
        "timings": {
            "pinned_read_seconds": None if pinned_read is None else round(pinned_read, 4),
            "disk_read_seconds": round(disk_seconds, 4),
            "note": ("wall-clock metadata, excluded from re-derivation: a face that carried a "
                     "stopwatch could not reproduce itself (first verify died on "
                     "0.4188 vs 0.4169 with nothing else different)"),
        },
        "verdict": verdict,
        "reasons": reasons,
        "self_disclosure": {
            "this_study_is_a_population_member": True,
            "note": ("this file lands after the measurement and is therefore one more new .py in "
                     "the population every census face reads; the window it publishes is true of "
                     "a tree that no longer exists, which is the finding rather than a caveat"),
        },
    }
    os.makedirs(OUTDIR, exist_ok=True)
    for name in (FACE, LATEST):
        with io.open(os.path.join(OUTDIR, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=2, sort_keys=False)
            fh.write("\n")
    return doc


# ---------------------------------------------------------------------------------------- verify

def _cmp(a, b, path, out):
    if type(a) is not type(b) and not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
        out.append("%s: type %s vs %s" % (path, type(a).__name__, type(b).__name__))
        return
    if isinstance(a, dict):
        for key in set(a) | set(b):
            if key in ("generated", "timings"):
                continue
            if key not in a or key not in b:
                out.append("%s.%s: present in only one side" % (path, key))
                continue
            _cmp(a[key], b[key], "%s.%s" % (path, key), out)
        return
    if isinstance(a, list):
        if len(a) != len(b):
            out.append("%s: length %s vs %s" % (path, len(a), len(b)))
            return
        for i, (x, y) in enumerate(zip(a, b)):
            _cmp(x, y, "%s[%s]" % (path, i), out)
        return
    if isinstance(a, float):
        if abs(a - b) > 1e-9:
            out.append("%s: %r vs %r" % (path, a, b))
        return
    if a != b:
        out.append("%s: %r vs %r" % (path, a, b))


def verify(root=None):
    root = root or ROOT
    path = os.path.join(OUTDIR, FACE)
    if not os.path.exists(path):
        return ["face missing: %s" % FACE]
    with io.open(path, encoding="utf-8") as fh:
        disk = json.load(fh)
    fresh = build(root)
    problems = []
    _cmp(disk, fresh, "face", problems)
    return problems


# --------------------------------------------------------------------------------------- selftest

def _ev(sha, ts, added=None, removed=None, modified=None):
    return {"sha": sha, "ts": ts, "added": list(added or []), "removed": list(removed or []),
            "modified": list(modified or [])}


def cmd_selftest():
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    # -- parse_log
    log = ("%saaa|100\nM\tscripts/x.py\nM\tdocs/a.md\n"
           "%sbbb|200\nA\tscripts/new.py\n"
           "%sccc|300\nD\tTools/old.py\n" % (MARK, MARK, MARK))
    evs = parse_log(log)
    check("L1 parse_log keeps only .py touches", len(evs) == 3, str(len(evs)))
    check("L2 added/removed/modified kept apart",
          evs[1]["added"] == ["scripts/new.py"] and evs[2]["removed"] == ["Tools/old.py"],
          str(evs[1]))
    check("L3 a non-py-only commit still parsed but contributes nothing",
          parse_log("%sddd|400\nM\tdocs/a.md\n" % MARK) == [], "expected empty")

    # -- classify
    check("L4 classify new_py", classify(_ev("s", 1, added=["a.py"])) == "new_py")
    check("L5 classify removed_py", classify(_ev("s", 1, removed=["a.py"])) == "removed_py")
    check("L6 classify edit_py", classify(_ev("s", 1, modified=["a.py"])) == "edit_py")

    # -- is_census_only
    check("L7 a census-only touch is census-only",
          is_census_only(_ev("s", 1, modified=[CENSUS_FAMILY[0]])))
    check("L8 a mixed touch is not census-only",
          not is_census_only(_ev("s", 1, modified=[CENSUS_FAMILY[0], "scripts/live_paper.py"])))

    # -- window_from
    events = [
        _ev("L", 0, added=[CENSUS_FAMILY[0]]),                    # landing
        _ev("C1", 100, modified=[CENSUS_FAMILY[1]]),               # census-only touch
        _ev("C2", 900, added=["scripts/producer.py"]),             # production touch
        _ev("C3", 2000, modified=["scripts/other.py"]),
    ]
    w_all = window_from(events, 0)
    check("L9 all window closes at the very next touch",
          w_all["closed"] and w_all["closing_sha"] == "C1" and w_all["seconds"] == 100,
          str(w_all))
    w_nc = window_from(events, 0, predicate=lambda ev: not is_census_only(ev), family=CENSUS_FAMILY)
    check("L10 non-census window skips the census touch",
          w_nc["closed"] and w_nc["closing_sha"] == "C2" and w_nc["seconds"] == 900, str(w_nc))
    check("L11 commits_between counts skipped commits",
          w_nc["commits_between"] == 1, str(w_nc["commits_between"]))
    check("L12 the non-census window is never shorter than the all window",
          (w_nc["seconds"] or 0) >= (w_all["seconds"] or 0), "%s vs %s" % (w_nc, w_all))

    open_w = window_from(events[:1], 0)
    check("L13 a window with no later touch is open, not zero",
          open_w["closed"] is False and open_w["seconds"] is None, str(open_w))

    same_commit = [_ev("L", 0, added=[CENSUS_FAMILY[0]]), _ev("N", 0, modified=["scripts/x.py"])]
    zero_w = window_from(same_commit, 0)
    check("L14 a same-second closing touch yields 0 seconds and stays closed",
          zero_w["closed"] and zero_w["seconds"] == 0, str(zero_w))

    # -- summarize
    s = summarize([{"closed": True, "seconds": 100}, {"closed": True, "seconds": 300},
                   {"closed": False, "seconds": None}])
    # Every closed window here (100s, 300s) is inside one round, so the count is 2 -- the fixture
    # was wrong, not the rule (E336 pit 3: a fixture that disagrees with the frozen rule is re-read).
    check("L15 summarize: median over closed windows, open counted separately",
          s["median_seconds"] == 200 and s["open"] == 1 and s["inside_one_round"] == 2, str(s))
    s2 = summarize([{"closed": True, "seconds": 700}, {"closed": True, "seconds": 900}])
    check("L16 summarize: nothing inside one round", s2["inside_one_round"] == 0
          and s2["share_inside_one_round"] == 0.0, str(s2))
    s3 = summarize([{"closed": False, "seconds": None}])
    check("L17 summarize: all-open publishes no median rather than 0",
          s3["median_seconds"] is None and s3["closed"] == 0, str(s3))

    # -- parse_ls_tree
    tree = ("100644 blob aaaa   1234\tscripts/a.py\n"
            "100644 blob bbbb   99\tREADME.md\n"
            "100644 blob cccc   2048\tTools/b.py\n")
    rows = parse_ls_tree(tree)
    check("L18 parse_ls_tree keeps only .py with sizes",
          rows == [("scripts/a.py", 1234), ("Tools/b.py", 2048)], str(rows))

    # -- decide
    v, _r = decide({"median_seconds": 300, "share_inside_one_round": 0.8},
                   {"median_seconds": 900}, {"pinned_read_seconds": 2.0})
    check("L19 decide: short window -> round-dependent", v == V_ROUND, v)
    v, _r = decide({"median_seconds": 7200, "share_inside_one_round": 0.1},
                   {"median_seconds": 9000}, {"pinned_read_seconds": 8.0})
    check("L20 decide: long window + hard pin -> dependency", v == V_DEPENDENT, v)
    v, _r = decide({"median_seconds": 7200, "share_inside_one_round": 0.1},
                   {"median_seconds": 9000}, {"pinned_read_seconds": 0.2})
    check("L21 decide: long window + cheap pin -> affordable", v == V_AFFORDABLE, v)
    v, _r = decide({"median_seconds": None, "share_inside_one_round": None},
                   {"median_seconds": None}, {"pinned_read_seconds": 0.1})
    check("L22 decide: no closed window -> dependency, never affordable", v == V_DEPENDENT, v)

    # -- _cmp
    problems = []
    _cmp({"a": 1, "generated": "x"}, {"a": 1, "generated": "y"}, "t", problems)
    check("L23 _cmp ignores generated and reports nothing", problems == [], str(problems))
    problems = []
    _cmp({"a": 1}, {"a": 2}, "t", problems)
    check("L24 _cmp catches a changed number", len(problems) == 1, str(problems))
    problems = []
    _cmp({"a": [1, 2]}, {"a": [1, 2, 3]}, "t", problems)
    check("L25 _cmp catches a length change", len(problems) == 1, str(problems))
    problems = []
    _cmp({"a": 1, "timings": {"s": 0.4}}, {"a": 1, "timings": {"s": 0.5}}, "t", problems)
    check("L36 _cmp ignores the wall-clock timing block", problems == [], str(problems))

    # -- family integrity
    missing = [p for p in CENSUS_FAMILY if not os.path.exists(os.path.join(ROOT, p))]
    check("L26 every named census face exists on disk", not missing, str(missing[:3]))
    check("L27 the census family is the listed 16 and this study is not in it",
          len(CENSUS_FAMILY) == 16 and "scripts/e338_census_green_window.py" not in CENSUS_FAMILY,
          str(len(CENSUS_FAMILY)))

    # -- ordering guard (the bug that made the first burn publish median 0.0s)
    check("L28 is_ascending accepts an oldest-first list",
          is_ascending([_ev("a", 1), _ev("b", 5), _ev("c", 5)]))
    check("L29 is_ascending rejects newest-first",
          not is_ascending([_ev("a", 5), _ev("b", 1)]))
    live = touch_events()
    check("L30 live events are oldest-first and non-empty",
          len(live) > 100 and is_ascending(live), "n=%s" % len(live))

    # -- sibling / coincidence reporting
    sib_events = [_ev("L", 0, added=[CENSUS_FAMILY[0]]),
                  _ev("S", 600, added=[CENSUS_FAMILY[1]], modified=["Tools/s6_chain_bmb.py"])]
    w = window_from(sib_events, 0, family=CENSUS_FAMILY)
    check("L31 added_census records the family member that closed the window",
          w["added_census"] == [CENSUS_FAMILY[1]], str(w["added_census"]))
    rows = [{"window_all": dict(w), "window_non_census": dict(w)},
            {"window_all": dict(w, closing_sha="OTHER"), "window_non_census": dict(w)}]
    coin = coincides(rows)
    check("L32 coincides counts only same-closing-commit pairs",
          coin["compared"] == 2 and coin["same_closing_commit"] == 1, str(coin))
    sib = sibling_closed(rows)
    check("L33 sibling_closed counts windows closed by a census addition",
          sib["closed"] == 2 and sib["closed_by_a_census_sibling"] == 2, str(sib))

    coincide_all = {"compared": 3, "same_closing_commit": 3}
    sibling_all = {"closed": 3, "closed_by_a_census_sibling": 3}
    v, _r = decide({"median_seconds": 2000, "share_inside_one_round": 0.0},
                   {"median_seconds": 2000}, {"pinned_read_seconds": 0.3},
                   coincide_all, sibling_all)
    check("L34 decide: sibling-terminated + coincident readings -> self-terminating",
          v == V_SELF_TERMINATING, v)
    v, _r = decide({"median_seconds": 2000, "share_inside_one_round": 0.0},
                   {"median_seconds": 3000}, {"pinned_read_seconds": 0.3},
                   {"compared": 3, "same_closing_commit": 1}, sibling_all)
    check("L35 decide: a non-coincident reading keeps the ordinary tiers", v == V_AFFORDABLE, v)

    for name, ok, detail in checks:
        say("%s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else " | " + str(detail)))
    failed = [name for name, ok, _d in checks if not ok]
    say("selftest %d/%d" % (len(checks) - len(failed), len(checks)))
    return 0 if not failed else 1


# ------------------------------------------------------------------------------------------- cli

def cmd_run():
    doc = build()
    s = doc["summary_all"]
    n = doc["summary_non_census"]
    pin = doc["pin"]
    say("%s -> %s" % (STUDY, os.path.join(OUTDIR, FACE)))
    say("verdict: %s" % doc["verdict"])
    say("windows: all median %ss (closed %s/%s, %s open) | non-census median %ss"
        % (s["median_seconds"], s["closed"], s["n"], s["open"], n["median_seconds"]))
    say("inside one round (%ss): %s of %s closed windows"
        % (ONE_ROUND_SECONDS, s["inside_one_round"], s["closed"]))
    say("readings coincide: %s/%s | closed by a new census sibling: %s/%s"
        % (doc["readings_coincide"]["same_closing_commit"], doc["readings_coincide"]["compared"],
           doc["windows_closed_by"]["closed_by_a_census_sibling"], doc["windows_closed_by"]["closed"]))
    say("pin %s: %s files / %s bytes vs disk %s files / %s bytes | pinned read %ss vs disk %ss"
        % (pin["sha"][:9], pin["files"], pin["bytes"], pin["disk_files"], pin["disk_bytes"],
           doc["timings"]["pinned_read_seconds"], doc["timings"]["disk_read_seconds"]))
    for reason in doc["reasons"]:
        say("  - %s" % reason)
    return 0


def cmd_verify():
    problems = verify()
    if problems:
        say("PROBLEMS: " + "; ".join(problems[:8]))
        return 1
    say("verify: 0 problems")
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    say(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))