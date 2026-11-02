"""E352 -- what a reader of a channel file actually sees, in commits and hours.

E349 established the shape of the channel: 139 live pointers (128 ``*_latest.json`` mirrors and
11 live state files), 840 comparisons outside fixtures, and only 14 of those comparisons ask
whether what was read is *current*.  It stopped at the population.  This study prices the window
that leaves open, using the only clock that cannot argue with us: the repository's own history.

    For every channel file that reaches a non-fixture comparison, walk its history on the
    first-parent line, then stand at each of the last W commits (a round boundary) and ask:
    which blob would a reader have opened, and how far behind the newest blob is it?

Two clocks are published for each file, because they answer different questions:

    lag in commits    the number of commits since the blob a reader would take was written --
                       "how many rounds of the repository is this copy behind"
    lag in hours      the wall-clock age of that same copy at the boundary

and once the lag is known, the three classes the card asks for fall out:

    (a) per-file lag median / p90 / max
    (b) the files whose lag is zero -- a writer rewrites them every round
    (c) the boundaries at which a reader ran code newer than the artifact it read: the file's
        last write index is OLDER than the last change of the source that decides on it

The verdict vocabulary is the card's and nothing else.  The one word that could drift is the
third: ``stale_window_unmeasured`` is defined here as *a stale window exists and the channel's own
checks do not measure it*, NOT as "we could not measure it" -- because we can, and do, measure the
lag.  A file whose writer never touched it inside the window is published as censored with an
explicit floor rather than as a zero (the card's bound: what a writer outside the repo does cannot
be timed).

Usage:
    python scripts/e352_staleness_window.py run|verify|selftest
"""

import json
import os
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-02"
FACE = "STALEWIN-%s.json" % TODAY
LATEST = "stalewin_latest.json"
STUDY = "E352_staleness_window"
SELF_REL = "scripts/e352_staleness_window.py"
SELF_OUTPUTS = (FACE, LATEST)

# The population comes from E349's published row table; the window is wide enough that a
# per-round writer is touched dozens of times inside it.
MIRROR_FACE = os.path.join(OUTDIR, "MIRROR-2026-11-01.json")
WINDOW = 240
CHAIN = "Tools/s6_chain_bmb.py"
ROUND_SOURCES = ("smoke_test.py",)  # sources that run every round besides the chain's own legs

WRITE_TOKENS = ('json.dump', 'write_text', 'write_bytes', '.to_json(', 'to_parquet(')
MAX_ROWS = 80

# Lag thresholds: a copy written at the boundary itself is one round old at the next boundary,
# so a median of 1 commit is "rewritten every round" and 0 is "written by this very commit".
ROUND_LAG = 1


# ------------------------------------------------------------------------------- plumbing

def say(message):
    sys.stdout.write(str(message) + "\n")
    sys.stdout.flush()


def _run(args, inp=None):
    return subprocess.run(args, cwd=ROOT, input=inp, capture_output=True)


def git(*args):
    p = _run(["git"] + list(args))
    if p.returncode != 0:
        return ""
    return p.stdout.decode("utf-8", "replace")


def read_tree_file(path):
    """Read a source file from the WORKING TREE, never through a promisor blob read.

    ``git show <pin>:<path>`` on this clone is a lazy-fetch trap: the clone is ``blob:none``, so
    any path whose blob is not already materialised starts a network fetch and the round hangs.
    Metadata commands (``ls-tree``, ``log -- path``) touch no blobs and stay; every read of file
    *contents* in this study goes through the disk, which is the same tree a reader would use.
    """
    try:
        with open(os.path.join(ROOT, path), "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def first_parent_window(width=WINDOW, at=None):
    """``[(sha, epoch)]`` oldest->newest on the first-parent line (a round boundary per commit).

    ``at`` anchors the walk at the face's own pin.  Without it the window is HEAD's, so every
    commit this line makes (including the one that publishes the face) shifts the window and the
    leg's own re-derivation moves -- the r1373 family: a gate graded by fresh re-derivation is
    invalidated by every writer that runs after it.  Verifying at the pin makes the table a
    function of the history it names, not of how many rounds have landed since.
    """
    out = git("log", "--first-parent", "-%d" % width, "--format=%H %ct",
              *([at] if at else []))
    rows = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 2:
            rows.append((parts[0], int(parts[1])))
    rows.reverse()
    return rows


def window_touch_map(window):
    """``{path: [boundary idx, ...]}`` from ONE ``git log --name-only`` over the whole window.

    WHY (r1374): the first version asked git per file (``git log -- <path>``, plus a
    ``--diff-filter=A`` walk for every file that was not present at the window's first boundary).
    A path-limited ``git log`` diffs trees commit by commit, so each call took 1-2 minutes on this
    tree and the whole leg ran ~16 minutes -- over the chain's own 900 s wall, i.e. a gate that
    cannot run is not a gate. One unfiltered walk over the same 240 commits gives the identical
    fact (which commits wrote which path) in a single pass, and the union of the paths is exactly
    the population this study needs.
    """
    index = {sha: i for i, (sha, _t) in enumerate(window)}
    p = _run(["git", "log", "--first-parent", "-%d" % len(window),
              "--name-only", "-z", "--format=%x01%H"])
    raw = p.stdout.decode("utf-8", "replace") if p.returncode == 0 else ""
    return _parse_touch_log(raw, index)


def _parse_touch_log(raw, index):
    """``{path: sorted boundary idxs}`` from a ``--name-only -z`` git log (pure, pinned by leg)."""
    out, cur = {}, None
    for tok in raw.split("\x00"):
        tok = tok.strip("\n")
        if not tok:
            continue
        if tok.startswith("\x01"):
            cur = index.get(tok[1:].strip())
            continue
        if cur is None:
            continue
        for name in tok.splitlines():
            name = name.strip()
            if name:
                out.setdefault(name, set()).add(cur)
    return {k: sorted(v) for k, v in out.items()}


def touches_in_window(path, window, tmap=None, present_at_start=None):
    """Indices of the window commits that wrote ``path``, plus where it first appeared.

    Presence at the window's first boundary comes from one ``ls-tree`` of that commit (or from a
    caller-supplied set), and the add index is the file's own first touch in the window: a path
    absent at the first boundary can only appear at the first commit that writes it -- which is
    what the old ``--diff-filter=A`` walk asked git to recompute per file.
    """
    idxs = list((tmap or {}).get(path) or [])
    if present_at_start is None:
        return idxs, (None if git("ls-tree", window[0][0], "--", path).strip() else
                      (min(idxs) if idxs else 0))
    if path in present_at_start:
        return idxs, None
    return idxs, (min(idxs) if idxs else 0)


def lag_series(touch_idxs, add_idx, window):
    """``[(boundary_idx, lag_commits, lag_hours, state)]`` for one file over one window.

    ``state`` is ``written_at_boundary`` (touched by this commit), ``lagging``, ``censored``
    (never touched inside the window, so the lag is a floor) or ``absent`` (the file did not
    exist yet -- a reader would have failed to open it at all).
    """
    times = [t for _sha, t in window]
    rows, last = [], None
    touch_set = set(touch_idxs)
    for i, t in enumerate(times):
        if i in touch_set:
            last = i
        if add_idx is not None and i < add_idx:
            rows.append((i, None, None, "absent"))
            continue
        if last is None:
            # present at the window's first boundary and never rewritten inside it: the last
            # write is at or before that boundary's parent, so i + 1 is a FLOOR, not a reading.
            rows.append((i, i + 1, (t - times[0]) / 3600.0, "censored"))
            continue
        rows.append((i, i - last, (t - times[last]) / 3600.0,
                     "written_at_boundary" if last == i else "lagging"))
    return rows


def _quantile(values, q):
    """Nearest-rank quantile over a sorted list; a single value is its own p90."""
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    pos = int(round(q * (len(ordered) - 1)))
    return ordered[max(0, min(len(ordered) - 1, pos))]


def summarise_lag(series):
    lags = [r[1] for r in series if r[1] is not None]
    hours = [r[2] for r in series if r[2] is not None]
    counts = {}
    for row in series:
        counts[row[3]] = counts.get(row[3], 0) + 1
    zero = len([x for x in lags if x == 0])
    return {
        "boundaries": len(series),
        "measured_boundaries": len(lags),
        "lag_median_commits": _quantile(lags, 0.5),
        "lag_p90_commits": _quantile(lags, 0.9),
        "lag_max_commits": max(lags) if lags else None,
        "lag_median_hours": _quantile(hours, 0.5),
        "lag_p90_hours": _quantile(hours, 0.9),
        "lag_max_hours": round(max(hours), 2) if hours else None,
        "zero_lag_boundaries": zero,
        "zero_lag_share_pct": round(100.0 * zero / len(lags), 2) if lags else None,
        "states": counts,
    }


# --------------------------------------------------------------------------- the population

def tree_paths(pin):
    return [p for p in (git("ls-tree", "-r", "--name-only", pin) or "").splitlines() if p]


def resolve_path(name, kind, paths):
    """One repo path for a channel basename, or ``None`` when the name is not unique."""
    cands = [p for p in paths if p.replace("\\", "/").rsplit("/", 1)[-1] == name]
    if not cands:
        return None, "missing_from_tree"
    if len(cands) == 1:
        return cands[0], ""
    prefer = ("results/", "fleet/machines/") if kind == "state" else ("results/",)
    narrowed = [p for p in cands if p.replace("\\", "/").startswith(prefer)]
    if len(narrowed) == 1:
        return narrowed[0], ""
    root = [p for p in cands if "/" not in p.replace("\\", "/")]
    if kind == "state" and len(root) == 1:
        return root[0], ""
    return None, "ambiguous_basename:%d" % len(cands)


def deciding_rows():
    """E349's row table, kept to the files that reach a non-fixture comparison."""
    if not os.path.exists(MIRROR_FACE):
        return [], {"source_face": None, "reason": "E349 face absent"}
    face = json.load(open(MIRROR_FACE, encoding="utf-8"))
    rows = [r for r in face.get("rows") or [] if int(r.get("non_fixture_gates") or 0) > 0]
    meta = {
        "source_face": os.path.basename(MIRROR_FACE),
        "source_pin": (face.get("pin") or "")[:8],
        "source_rows_published": len(face.get("rows") or []),
        "source_rows_truncated": face.get("rows_truncated"),
        "with_a_non_fixture_gate": (face.get("summary") or {}).get("with_a_non_fixture_gate"),
    }
    return rows, meta


def round_sources(pin):
    """Sources that still run: this machine's S6 chain legs, the smoke suite, plus its helpers."""
    text = read_tree_file(CHAIN)
    named = {s for s in ROUND_SOURCES if s in text}
    for row in tree_paths(pin):
        if row in text:
            named.add(row)
    return named


def in_repo_writers(names):
    """``{name: [source]}`` -- source files naming the basename that also contain a write token.

    A heuristic, published as one: a file that merely *loads* the basename is a reader, not a
    writer, and the only machine check that separates them without an AST of every writer is a
    write-token scan.  Read straight off the disk (``read_tree_file``) -- a ``git grep`` here
    inherited a stdin pipe from the round's shell and blocked with zero CPU for ten minutes,
    which is the same promisor-hazard class as ``git show``: this study reads contents from the
    working tree only, and takes no subprocess it does not need.
    """
    names = sorted(names)
    if not names:
        return {}
    out = {}
    scanned = 0
    for path in py_sources():
        text = read_tree_file(path)
        scanned += 1
        if not any(tok in text for tok in WRITE_TOKENS):
            continue
        for name in names:
            if name in text:
                out.setdefault(name, []).append(path)
    say("writer scan: %d sources" % scanned)
    return {name: sorted(srcs) for name, srcs in out.items()}


SKIP_TOPS = ("legacy", "Money02", "Money0923", "results", "data", "dist", "build",
             "node_modules", ".git", ".codely-cli", "__pycache__")


def py_sources():
    """Every tracked-looking ``.py`` source outside the artifact and vendored trees."""
    out = []
    for base, dirs, files in os.walk(ROOT):
        rel = os.path.relpath(base, ROOT).replace("\\", "/")
        rel = "" if rel == "." else rel
        if rel.split("/")[0] in SKIP_TOPS:
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if d not in ("__pycache__", "node_modules")]
        for name in files:
            if name.endswith(".py"):
                out.append(("%s/%s" % (rel, name)) if rel else name)
    return sorted(out)


# ------------------------------------------------------------------------------- the study

def build(pin=None, width=WINDOW):
    pin = (pin or (git("rev-parse", "HEAD") or "")).strip()
    if not pin:
        raise SystemExit("no git HEAD")
    window = first_parent_window(width, pin)
    if not window:
        raise SystemExit("empty first-parent window")
    say("window: %d first-parent commits" % len(window))
    rows, pop_meta = deciding_rows()
    paths = tree_paths(pin)
    live = round_sources(pin)
    say("population: %d deciding rows, %d live round sources" % (len(rows), len(live)))
    writers = in_repo_writers(
        {r["file"] for r in rows if r.get("file") not in SELF_OUTPUTS})

    tmap = window_touch_map(window)
    say("touch map: %d paths written inside the window" % len(tmap))
    present_at_start = set(tree_paths(window[0][0]))
    src_last = {}

    def source_index(src):
        if src not in src_last:
            idxs, _add = touches_in_window(src, window, tmap, present_at_start)
            src_last[src] = max(idxs) if idxs else None
        return src_last[src]

    files, skipped = [], []
    for n, row in enumerate(rows):
        name = row.get("file") or ""
        if name in SELF_OUTPUTS:      # E319: the census is not its own target
            skipped.append({"file": name, "reason": "self_output"})
            continue
        path, why = resolve_path(name, row.get("kind") or "", paths)
        if not path:
            skipped.append({"file": name, "reason": why})
            continue
        if n % 10 == 0:
            say("history %d/%d %s" % (n + 1, len(rows), name))
        idxs, add_idx = touches_in_window(path, window, tmap, present_at_start)
        series = lag_series(idxs, add_idx, window)
        stats = summarise_lag(series)
        gates_live = [s for s in (row.get("sources") or []) if s in live]
        instances, deepest = 0, 0
        for src in gates_live:
            si = source_index(src)
            if si is None:
                continue
            for i, lag_c, _h, state in series:
                if state == "absent" or lag_c is None:
                    continue
                touch_at = i - lag_c
                if touch_at < si <= i:
                    instances += 1
                    deepest = max(deepest, i - si + 1)
        files.append({
            "file": name,
            "path": path,
            "kind": row.get("kind"),
            "non_fixture_gates": row.get("non_fixture_gates"),
            "freshness_gates": row.get("freshness_gates"),
            "live_gate_sources": gates_live,
            "in_repo_writers": writers.get(name, []),
            "touches_in_window": len(idxs),
            "added_in_window": add_idx is not None,
            "measured": bool([s for s in series if s[3] != "absent"]),
            "censored": stats["states"].get("censored", 0) > 0,
            "class": ("rewritten_every_round"
                      if stats["lag_median_commits"] is not None
                      and stats["lag_median_commits"] <= ROUND_LAG else "lagging"),
            "decide_stale_instances": instances,
            "decide_stale_deepest_commits": deepest,
            "stats": stats,
        })

    measured = [f for f in files if f["measured"]]
    every_round = [f for f in measured if f["class"] == "rewritten_every_round"]
    lagging = [f for f in measured if f["class"] == "lagging"]
    stale = [f for f in measured if f["decide_stale_instances"] > 0]
    unmeasurable = [f for f in files if not f["measured"]] + [
        {"file": s["file"], "path": None, "reason": s["reason"]} for s in skipped]

    med = [f["stats"]["lag_median_commits"] for f in measured
           if f["stats"]["lag_median_commits"] is not None]
    summary = {
        "deciding_population_from_E349": pop_meta,
        "deciding_rows": len(rows),
        "files_resolved": len(files),
        "files_unresolved_or_unmeasurable": len(unmeasurable),
        "unmeasurable_share_pct": (round(100.0 * len(unmeasurable) / len(rows), 2)
                                   if rows else None),
        "measured_files": len(measured),
        "files_rewritten_every_round": len(every_round),
        "files_lagging": len(lagging),
        "median_of_file_medians_commits": _quantile(med, 0.5),
        "p90_of_file_medians_commits": _quantile(med, 0.9),
        "worst_file": (max(measured, key=lambda f: (f["stats"]["lag_p90_commits"] or 0, f["file"]))
                       or {}).get("file") if measured else None,
        "worst_file_p90_commits": max([f["stats"]["lag_p90_commits"] or 0 for f in measured],
                                     default=None),
        "worst_file_p90_hours": max([f["stats"]["lag_p90_hours"] or 0.0 for f in measured],
                                    default=None),
        "files_with_a_decide_stale_instance": len(stale),
        "decide_stale_instances_total": sum(f["decide_stale_instances"] for f in files),
        "decide_stale_deepest_commits": max([f["decide_stale_deepest_commits"] for f in files],
                                            default=0),
        "files_with_a_freshness_gate": len([f for f in files
                                            if int(f.get("freshness_gates") or 0) > 0]),
        "window_commits": len(window),
        "window_hours": round((window[-1][1] - window[0][1]) / 3600.0, 2),
        "window_head": pin[:8],
        "live_round_sources": len(live),
        "gates_from_live_sources": len([f for f in files if f["live_gate_sources"]]),
    }
    verdict = decide(summary)
    return {
        "study": STUDY,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "today": TODAY,
        "pin": pin,
        "source": SELF_REL,
        "evidence_cutoff": TODAY,
        "summary": summary,
        "verdict": verdict,
        "verdict_definition": (
            "fresh_by_construction: every measured deciding file is rewritten within %d commit of "
            "every boundary AND no boundary exists at which a reader ran gate code newer than the "
            "artifact it read. fresh_by_luck: the lag is that short but such boundaries do exist, "
            "so nothing ties the writer to the reader's code. stale_window_unmeasured: a stale "
            "window exists that the channel's own comparisons do not measure (E349: 14 freshness "
            "gates of 840) -- the window is measured here; what is missing is the check."
            % ROUND_LAG),
        "rows": files[:MAX_ROWS],
        "unmeasurable": unmeasurable[:MAX_ROWS],
        "rows_truncated": max(0, len(files) - MAX_ROWS),
        "bound": ("the lag is measured on this line's own first-parent history over %d commits; a "
                  "file never touched inside that window is censored rather than zero, and a "
                  "writer living outside this repository cannot be timed at all -- it appears in "
                  "'unmeasurable', never as a fresh copy" % len(window)),
    }


def decide(summary):
    unmeas = summary.get("unmeasurable_share_pct")
    measured = summary.get("measured_files") or 0
    med = summary.get("median_of_file_medians_commits")
    instances = summary.get("decide_stale_instances_total") or 0
    if measured == 0 or unmeas is None or unmeas > 50.0:
        return "stale_window_unmeasured"
    if med is not None and med <= ROUND_LAG and instances == 0:
        return "fresh_by_construction"
    if med is not None and med <= ROUND_LAG and instances > 0:
        return "fresh_by_luck"
    return "stale_window_unmeasured"


def write(face):
    os.makedirs(OUTDIR, exist_ok=True)
    out = []
    for target in (os.path.join(OUTDIR, FACE), os.path.join(OUTDIR, LATEST)):
        with open(target, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        out.append(target)
    return out


def verify():
    dated = os.path.join(OUTDIR, FACE)
    if not os.path.exists(dated):
        dated = os.path.join(OUTDIR, LATEST)
    if not os.path.exists(dated):
        say("no published face")
        return 2
    face = json.load(open(dated, encoding="utf-8"))
    pin = (face.get("pin") or "").strip()
    if not pin:
        say("the face carries no pin")
        return 2
    fresh = build(pin)
    problems = []
    keys = ("measured_files", "files_rewritten_every_round", "files_lagging",
            "decide_stale_instances_total", "window_commits", "files_resolved")
    for key in keys:
        if (face.get("summary") or {}).get(key) != fresh["summary"].get(key):
            problems.append("%s does not re-derive (%s vs %s)"
                            % (key, (face.get("summary") or {}).get(key),
                               fresh["summary"].get(key)))
    if face.get("verdict") != fresh["verdict"]:
        problems.append("verdict does not re-derive (%s vs %s)"
                        % (face.get("verdict"), fresh["verdict"]))
    say(json.dumps({"problems": problems}, ensure_ascii=False))
    return 0 if not problems else 1


# ------------------------------------------------------------------------------ selftest

def _window(times):
    return [("%040d" % i, t) for i, t in enumerate(times)]


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    hours = [i * 3600 for i in range(10)]
    win = _window(hours)

    # 1. a file written at every boundary has zero lag at zero-hour boundaries
    series = lag_series(list(range(10)), None, win)
    stats = summarise_lag(series)
    leg("a file written every round reads zero lag",
        stats["lag_median_commits"] == 0 and stats["lag_max_commits"] == 0
        and stats["states"].get("written_at_boundary") == 10, stats)

    # 2. one write at the window's first boundary lags by the boundary index, in commits AND
    #    hours; the median of an even count is the lower middle (seeded, so it cannot drift)
    series = lag_series([0], None, win)
    stats = summarise_lag(series)
    leg("the lag is counted in commits and hours from the last write",
        stats["lag_max_commits"] == 9 and stats["lag_max_hours"] == 9.0
        and stats["lag_median_commits"] == 4
        and _quantile([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 0.9) == 8, stats)

    # 3. a writer silent inside the window is censored with a FLOOR, never zero (the card's bound)
    series = lag_series([], None, win)
    stats = summarise_lag(series)
    leg("a silent writer is censored, not fresh",
        stats["zero_lag_boundaries"] == 0 and stats["states"].get("censored") == 10
        and stats["lag_median_commits"] == 5 and stats["lag_max_commits"] == 10, stats)

    # 4. a file added mid-window is absent before its add, and the lag restarts there
    series = lag_series([4], 4, win)
    states = [s[3] for s in series]
    leg("a file appears at its add commit and is absent before it",
        states[:4] == ["absent"] * 4 and states[4] == "written_at_boundary"
        and summarise_lag(series)["lag_max_commits"] == 5, states)

    # 5. a reader running code newer than the artifact it reads is an instance, and one commit
    #    of fence is enough -- the boundary itself is not an instance
    src_written_at_6 = 6
    instances = []
    for i, lag_c, _h, state in lag_series([0], None, win):
        touch_at = i - lag_c
        if touch_at < src_written_at_6 <= i:
            instances.append(i)
    leg("gate code newer than the artifact counts fence boundaries only",
        instances and min(instances) == 6 and 6 not in
        [i for i, lag_c, _h, st in lag_series([6], None, win)
         if (i - lag_c) < src_written_at_6 <= i], instances)

    # 6. p90 of a single reading is that reading (not an IndexError, not a zero)
    leg("a single reading is its own p90", _quantile([7], 0.9) == 7 and _quantile([], 0.9) is None)

    # 7. the writer heuristic does not count a reader, and does count a write
    leg("a load is not a write",
        not any(tok in 'd = json.load(open("x_latest.json"))' for tok in WRITE_TOKENS))
    leg("a dump is a write",
        any(tok in 'json.dump(face, open(p, "w"))' for tok in WRITE_TOKENS))

    # 8. the verdict vocabulary is the card's, and each branch is reachable
    base = {"measured_files": 10, "unmeasurable_share_pct": 0.0,
            "median_of_file_medians_commits": 0, "decide_stale_instances_total": 0}
    leg("zero lag and no stale fence is construction",
        decide(base) == "fresh_by_construction", decide(base))
    leg("zero lag with a stale fence is luck",
        decide(dict(base, decide_stale_instances_total=3)) == "fresh_by_luck")
    leg("real lag with no freshness check is an unmeasured stale window",
        decide(dict(base, median_of_file_medians_commits=6)) == "stale_window_unmeasured")
    leg("an unmeasurable majority makes no fresh claim",
        decide(dict(base, unmeasurable_share_pct=80.0)) == "stale_window_unmeasured")
    leg("no measured file at all makes no fresh claim",
        decide(dict(base, measured_files=0)) == "stale_window_unmeasured")

    # 9. a basename that lives in two places is not guessed at
    paths = ["results/a/dup.json", "results/b/dup.json", "fleet/machines/x.json"]
    leg("an ambiguous basename is refused rather than guessed",
        resolve_path("dup.json", "mirror", paths) == (None, "ambiguous_basename:2"))
    leg("a unique basename resolves", resolve_path("x.json", "state", paths)[0]
        == "fleet/machines/x.json")

    # 10. the single-pass touch map is the same fact the per-file walk asked for: paths land on
    #     their own commit, a path with a space survives -z, and a path before any commit marker
    #     is not attributed to an unknown commit
    _idx = {"a" * 40: 0, "b" * 40: 1}
    _raw = "\x01%s\0results/one.json\0results/two words.json\0\x01%s\0results/one.json\0" % (
        "a" * 40, "b" * 40)
    _tm = _parse_touch_log(_raw, _idx)
    leg("the touch map attributes each path to its own boundary",
        _tm.get("results/one.json") == [0, 1]
        and _tm.get("results/two words.json") == [0] and len(_tm) == 2, _tm)
    leg("a path outside any known commit is not attributed",
        _parse_touch_log("\x00results/orphan.json\0\x01%s\0x.json\0" % ("c" * 40), _idx)
        == {})

    failed = [r for r in legs if not r[1]]
    for name, ok, detail in legs:
        say("[%s] %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else " :: %s" % (detail,)))
    say("selftest %d/%d" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


# ---------------------------------------------------------------------------------- main

def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        face = build()
        dated, latest = write(face)
        say(json.dumps({"study": STUDY, "verdict": face["verdict"],
                        "summary": face["summary"],
                        "dated": dated.replace(ROOT + os.sep, ""),
                        "latest": latest.replace(ROOT + os.sep, "")},
                       ensure_ascii=False, indent=1))
        return 0
    if cmd == "verify":
        return verify()
    say("usage: run|verify|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))