"""E348 -- what a restored gate does not protect in retrospect.

E345 published a 9.26-hour, 10-round window in which the futures-TSMOM smoke check
was absent from this line while the suite kept running, and classified that window
`nothing`: no surviving check asserted the property.  That answer is about COVERAGE.
This asks the other question, the one an absence cannot answer by itself: inside that
window, was there a value for the gate to be wrong about -- and if there was, did any
clause the restore now asserts stand violated?

Method: the five clauses the restored check literally compares are frozen here from
smoke_test.py at HEAD (`actionable is False`, `shadow is True`, `book.gross <= 3.0`,
`generated_for_bar == panel tail`, `staleness.stale is False`).  Every commit of the
window is then replayed from its own tree: the face blob and the futures panel blobs
are read at that commit, and each clause is classified held | violated | not_evaluable.
Panel tails are resolved per blob, so ten varieties x N commits cost the number of
distinct blobs, not the number of commits.

The verdict vocabulary is deliberately narrow:

  nothing_to_evaluate -- the gate had nothing to be wrong about (face absent, or no
                         clause evaluable at any commit inside the window);
  window_was_clean    -- the face existed and every evaluable clause held at every
                         commit in which it existed;
  violation_was_relayed -- at least one clause stood violated inside the window, with
                         the round that shipped it, the round where the restore began
                         asserting it, and the relay length between them.

A subtlety this face publishes rather than smooths over: if the face and the gate first
appear in the SAME commit, the window was not merely clean -- the assertion arrived
with its subject, so the gate has never been exercised against anything on this line
except the state it was imported with.  That is reported as
`assertion_and_subject_arrived_together`, not as a clean window.

Modes: run (write the face), selftest (hermetic, no git), verify (re-derive from git).

Written by bm-b r1369.
"""
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACE_DIR = os.path.join(ROOT, "results", "state_tilt")
SOURCE_FACE = os.path.join(FACE_DIR, "GATEABSENCE-2026-11-01.json")
FACE_NAME = "RESTOREDGATE-2026-11-01.json"
LATEST = "restoredgate_latest.json"
GUARDED = "smoke_test.py"
SIGNAL = "results/futures_tsmom_signal.json"
PANEL_DIR = "data/futures_daily"
GROSS_CAP = 3.0 + 1e-9
ROUNDS = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")

# The clause table is frozen from the restored check body in smoke_test.py.  Each entry
# is (key, what the gate literally compares, the field names that must appear in the
# check text).  verify() re-reads the guarded file and refuses a table that has drifted
# away from the gate it claims to model.
CLAUSES = [
    ("actionable_is_false", "face.actionable is False", ("actionable",)),
    ("shadow_is_true", "face.shadow is True", ("shadow",)),
    ("gross_within_cap", "face.book.gross is a number and <= 3.0 (1e-9 tolerance)", ("gross",)),
    ("bar_matches_panel_tail",
     "face.generated_for_bar equals the newest bar date across data/futures_daily/*.csv "
     "in that same commit", ("generated_for_bar",)),
    ("not_stale", "face.staleness.stale is False", ("stale",)),
]
CLAUSE_KEYS = [c[0] for c in CLAUSES]


# ---------------------------------------------------------------- git plumbing
def _run(args, inp=None):
    return subprocess.run(args, cwd=ROOT, input=inp, capture_output=True)


def git(*args):
    p = _run(["git"] + list(args))
    if p.returncode != 0:
        return None
    return p.stdout.decode("utf-8", "replace")


def iso(ts):
    return datetime.fromtimestamp(int(ts), timezone.utc).astimezone().isoformat(timespec="seconds")


def blob_map(specs):
    """{'<sha>:<path>': blobsha|None} in one batch-check call.

    A missing path comes back as '<spec> missing' -- three tokens, not two, which is
    exactly the shape that turns a naive split()[0] read into a silent filename.
    """
    if not specs:
        return {}
    inp = ("\n".join(specs) + "\n").encode("utf-8")
    p = _run(["git", "cat-file", "--batch-check=%(objectname) %(objecttype)"], inp)
    out = p.stdout.decode("utf-8", "replace").splitlines()
    res = {}
    for spec, line in zip(specs, out):
        parts = line.split()
        if len(parts) == 2 and parts[1] == "blob":
            res[spec] = parts[0]
        else:
            res[spec] = None
    return res


def blob_contents(shas):
    """{blobsha: bytes} in one batch call."""
    uniq = sorted({s for s in shas if s})
    if not uniq:
        return {}
    inp = ("\n".join(uniq) + "\n").encode("utf-8")
    p = _run(["git", "cat-file", "--batch"], inp)
    data = p.stdout
    res = {}
    pos = 0
    while pos < len(data):
        nl = data.find(b"\n", pos)
        if nl < 0:
            break
        header = data[pos:nl].decode("utf-8", "replace").split()
        if len(header) < 3:
            break
        size = int(header[2])
        body = data[nl + 1:nl + 1 + size]
        res[header[0]] = body
        pos = nl + 1 + size + 1
    return res


def list_panel_paths(ref="HEAD"):
    t = git("ls-tree", "--name-only", ref, PANEL_DIR + "/") or ""
    return [p for p in t.splitlines() if p.endswith(".csv")]


def panel_tail(text):
    """Newest bar date in one csv, read the way the smoke check reads it."""
    try:
        lines = text.strip().splitlines()
        if len(lines) < 2:
            return None
        return lines[-1].split(",")[0].strip()[:10]
    except Exception:
        return None


def window_commits(lo, hi):
    """Commits inside (lo, hi) in topological order: hi is the restore, excluded."""
    t = git("log", "--reverse", "--format=%H|%at|%s", "%s..%s^" % (lo, hi))
    if t is None:
        t = git("log", "--reverse", "--format=%H|%at|%s", "%s..%s" % (lo, hi)) or ""
    rows = []
    for line in t.splitlines():
        if "|" in line:
            sha, ts, subj = line.split("|", 2)
            rows.append({"sha": sha, "ts": int(ts), "subject": subj})
    return rows


# ---------------------------------------------------------------- clause evaluation
def evaluate(face, panel_tail_date):
    """{(clause): ('held'|'violated'|'not_evaluable', detail)} for one commit's state."""
    res = {}
    if face is None:
        for k in CLAUSE_KEYS:
            res[k] = ("not_evaluable", "the face is not in this commit's tree")
        return res
    gross = None
    book = face.get("book")
    if isinstance(book, dict):
        gross = book.get("gross")
    stale = None
    st = face.get("staleness")
    if isinstance(st, dict):
        stale = st.get("stale")
    bar = face.get("generated_for_bar")

    res["actionable_is_false"] = (
        ("held" if face.get("actionable") is False else "violated"),
        "actionable=%r" % (face.get("actionable"),))
    res["shadow_is_true"] = (
        ("held" if face.get("shadow") is True else "violated"),
        "shadow=%r" % (face.get("shadow"),))
    # the same expression the check uses: bool is an int in Python, and the gate
    # accepts it, so the model must not be stricter than the thing it models.
    if isinstance(gross, (int, float)):
        res["gross_within_cap"] = (
            ("held" if gross <= GROSS_CAP else "violated"), "gross=%r" % (gross,))
    else:
        res["gross_within_cap"] = ("not_evaluable", "gross=%r is not a number" % (gross,))
    if panel_tail_date and bar:
        res["bar_matches_panel_tail"] = (
            ("held" if bar == panel_tail_date else "violated"),
            "bar=%r panel_tail=%r" % (bar, panel_tail_date))
    else:
        res["bar_matches_panel_tail"] = (
            "not_evaluable",
            "no panel tail in the tree (%r) or no generated_for_bar (%r)" % (panel_tail_date, bar))
    if stale is None:
        res["not_stale"] = ("not_evaluable", "staleness absent from the face")
    else:
        res["not_stale"] = (("held" if stale is False else "violated"), "stale=%r" % (stale,))
    return res


def _state_of(entry):
    """Clause entries are published as {'state','detail'}; plain states are accepted too."""
    if isinstance(entry, dict):
        return entry.get("state")
    if isinstance(entry, tuple):
        return entry[0]
    return entry


def tally(rows):
    """Per-clause held/violated/not_evaluable counts over the window's commit rows."""
    out = {}
    for k in CLAUSE_KEYS:
        out[k] = {"held": 0, "violated": 0, "not_evaluable": 0}
    for row in rows:
        for k, entry in row["clauses"].items():
            out[k][_state_of(entry)] += 1
    return out


def verdict_of(rows):
    """The narrow vocabulary, in the order its precedence demands.

    An unevaluable clause never counts as held: 'nothing to evaluate' must not be
    laundered into 'clean'.
    """
    evaluated = [r for r in rows if r["clauses_evaluable"] > 0]
    if not evaluated:
        return "nothing_to_evaluate"
    if any(r["clauses_violated"] > 0 for r in evaluated):
        return "violation_was_relayed"
    return "window_was_clean"


# ---------------------------------------------------------------- rounds
def parse_rounds(path=ROUNDS):
    rows = []
    if not os.path.exists(path):
        return rows
    with io.open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.startswith("|"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 4:
                continue
            m = re.match(r"(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)", parts[1])
            r = re.match(r"r(\d+)", parts[2])
            if not (m and r):
                continue
            dt = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")
            rows.append({"round": int(r.group(1)), "epoch": int(dt.timestamp()),
                         "postscript": "postscript" in parts[2].lower()})
    return rows


def round_at(rows, ts):
    """The round whose row is the last one starting at or before ts."""
    live = sorted({r["epoch"]: r["round"] for r in rows if not r["postscript"]}.items())
    hit = None
    for epoch, rnd in live:
        if epoch <= ts:
            hit = rnd
        else:
            break
    return hit


def _has_commits(lo, hi):
    t = git("rev-list", "--count", "%s..%s" % (lo, hi))
    if not t:
        return False
    try:
        return int(t.strip() or 0) > 0
    except ValueError:
        return False


# ---------------------------------------------------------------- the study
def build(head=None):
    """Build the face.  `head` pins the post-restore replay, so re-deriving later does
    not read new commits as drift (the measurement is time-scoped, not a moving target)."""
    head = (head or (git("rev-parse", "HEAD") or "")).strip()
    src = json.load(io.open(SOURCE_FACE, encoding="utf-8"))
    windows = [w for w in src.get("windows", []) if w.get("restore_sha")]
    if not windows:
        raise SystemExit("no window with a restore in the source face")
    rounds = parse_rounds()
    panel_paths = list_panel_paths("HEAD")

    out_windows = []
    for w in windows:
        rem = w["removal_sha"]
        restore = w["restore_sha"]
        # E345 stores abbreviated shas; resolve to full ones so rev-range is exact
        rem = (git("rev-parse", rem) or rem).strip()
        restore = (git("rev-parse", restore) or restore).strip()
        commits = window_commits(rem, restore)
        after = window_commits(restore, head) if _has_commits(restore, head) else []

        def replay(commits_, extra=()):
            """Replay commits from their own trees.

            extra specs are boundary commits the question asks about but that are not
            inside the range (the restore and its parent).  Without them a lookup miss
            and "the panel was not in that tree" are the same value -- which would
            publish a not_evaluable clause that was never actually asked.
            """
            specs = list(extra)
            for c in commits_:
                specs.append("%s:%s" % (c["sha"], SIGNAL))
                for p in panel_paths:
                    specs.append("%s:%s" % (c["sha"], p))
            bmap = blob_map(specs)
            face_blobs = {b for k, b in bmap.items() if k.endswith(":" + SIGNAL)}
            panel_blobs = {b for k, b in bmap.items() if b and (PANEL_DIR in k)}
            contents = blob_contents(list(face_blobs) + list(panel_blobs))

            def face_of(sha):
                b = bmap.get("%s:%s" % (sha, SIGNAL))
                if not b:
                    return None
                try:
                    return json.loads(contents[b].decode("utf-8", "replace"))
                except Exception:
                    return None

            def tail_of(sha):
                tails = []
                for p in panel_paths:
                    b = bmap.get("%s:%s" % (sha, p))
                    if not b:
                        continue
                    t = panel_tail(contents[b].decode("utf-8", "replace"))
                    if t:
                        tails.append(t)
                return max(tails) if tails else None

            rows = []
            for c in commits_:
                face = face_of(c["sha"])
                tail = tail_of(c["sha"])
                cl = evaluate(face, tail)
                states = [s for s, _ in cl.values()]
                rows.append({
                    "sha": c["sha"][:11],
                    "ts": iso(c["ts"]),
                    "subject": c["subject"][:90],
                    "face_present": face is not None,
                    "panel_tail": tail,
                    "clauses": {k: {"state": s, "detail": d} for k, (s, d) in cl.items()},
                    "clauses_evaluable": sum(1 for s in states if s != "not_evaluable"),
                    "clauses_held": sum(1 for s in states if s == "held"),
                    "clauses_violated": sum(1 for s in states if s == "violated"),
                })
            return rows, bmap, face_of, tail_of

        boundary = ["%s^:%s" % (restore, SIGNAL), "%s:%s" % (restore, SIGNAL)]
        for p in panel_paths:
            boundary.append("%s^:%s" % (restore, p))
            boundary.append("%s:%s" % (restore, p))
        rows, bmap, face_of, tail_of = replay(commits, boundary)

        counts = tally(rows)
        verdict = verdict_of(rows)
        face_present_rows = [r for r in rows if r["face_present"]]
        violated_rows = [r for r in rows if r["clauses_violated"] > 0]

        first_violation = violated_rows[0] if violated_rows else None
        ship_round = round_at(rounds, _epoch(first_violation["ts"])) if first_violation else None
        restore_epoch = int((git("log", "-1", "--format=%at", restore) or "0").strip() or 0)
        restore_round = round_at(rounds, restore_epoch) if restore_epoch else None
        relay = (restore_round - ship_round) if (ship_round and restore_round) else None

        face_before = bmap.get("%s^:%s" % (restore, SIGNAL))
        face_at = bmap.get("%s:%s" % (restore, SIGNAL))
        arrived_together = (not face_before) and bool(face_at)

        at_restore = evaluate(face_of(restore), tail_of(restore))
        at_head_cl = evaluate(_load_head_face(), _head_panel_tail(panel_paths))

        after_rows, after_bmap, _after_face, _after_tail = (replay(after) if after else ([], {}, None, None))
        after_counts = tally(after_rows) if after_rows else None
        after_viol = [r for r in after_rows if r["clauses_violated"] > 0]
        # 279 green runs are not 279 observations: count the states actually observed
        after_face_blobs = {after_bmap.get("%s:%s" % (c["sha"], SIGNAL)) for c in after} - {None}
        after_panel_tails = {r["panel_tail"] for r in after_rows if r["panel_tail"]}
        after_first_bad = None
        if after_viol:
            after_first_bad = {"sha": after_viol[0]["sha"], "ts": after_viol[0]["ts"],
                               "clauses": [k for k, v in after_viol[0]["clauses"].items()
                                           if v["state"] == "violated"]}

        out_windows.append({
            "name": w["name"],
            "removal_sha": rem[:11],
            "restore_sha": restore[:11],
            "commits_replayed": len(rows),
            "wall_hours": w.get("wall_hours"),
            "rounds_in_window": w.get("rounds_in_window"),
            "face_present_commits": len(face_present_rows),
            "face_absent_commits": len(rows) - len(face_present_rows),
            "assertion_and_subject_arrived_together": arrived_together,
            "clause_counts": counts,
            "first_violation": ({"sha": first_violation["sha"], "ts": first_violation["ts"],
                                 "clauses": [k for k, v in first_violation["clauses"].items()
                                             if v["state"] == "violated"]}
                                if first_violation else None),
            "shipped_by_round": ship_round,
            "restore_round": restore_round,
            "relay_rounds": relay,
            "clauses_at_restore_commit": {k: v[0] for k, v in at_restore.items()},
            "clauses_at_head": {k: v[0] for k, v in at_head_cl.items()},
            "after_the_restore": {
                "population": "commits in (restore, replay_head] on this line",
                "replay_head": head[:11],
                "commits": len(after_rows),
                "face_present_commits": sum(1 for r in after_rows if r["face_present"]),
                "clause_counts": after_counts,
                "commits_with_a_violation": len(after_viol),
                "first_violation": after_first_bad,
                "panel_tail_at_head": _head_panel_tail(panel_paths),
                "distinct_face_blobs": len(after_face_blobs),
                "distinct_panel_tails": len(after_panel_tails),
                "one_observation_repeated": (len(after_face_blobs) == 1
                                             and len(after_panel_tails) == 1
                                             and len(after_rows) > 1),
            },
            "verdict": verdict,
            "why": _why(verdict, counts, arrived_together),
            "commits": rows,
        })

    by_verdict = {}
    for w in out_windows:
        by_verdict[w["verdict"]] = by_verdict.get(w["verdict"], 0) + 1

    # both windows share one restore commit, so the post-restore replay is the same
    # population twice -- dedupe by restore sha before publishing a total
    uniq_after = {}
    for w in out_windows:
        uniq_after[w["restore_sha"]] = w["after_the_restore"]

    summary = {
        "windows": len(out_windows),
        "by_verdict": by_verdict,
        "commits_replayed": sum(w["commits_replayed"] for w in out_windows),
        "commits_where_the_face_existed": sum(w["face_present_commits"] for w in out_windows),
        "clauses_never_evaluable": sum(
            1 for w in out_windows for k in CLAUSE_KEYS
            if w["clause_counts"][k]["not_evaluable"] == w["commits_replayed"]),
        "clauses_violated_at_any_commit": sum(
            1 for w in out_windows for k in CLAUSE_KEYS
            if w["clause_counts"][k]["violated"] > 0),
        "windows_where_the_gate_arrived_with_its_subject": sum(
            1 for w in out_windows if w["assertion_and_subject_arrived_together"]),
        "post_restore_commits": sum(a["commits"] for a in uniq_after.values()),
        "post_restore_commits_with_the_face": sum(
            a["face_present_commits"] for a in uniq_after.values()),
        "post_restore_commits_with_a_violation": sum(
            a["commits_with_a_violation"] for a in uniq_after.values()),
        "post_restore_replays_that_are_one_observation_repeated": sum(
            1 for a in uniq_after.values() if a.get("one_observation_repeated")),
    }

    verdict = "+".join(sorted(by_verdict)) if by_verdict else "no_windows"
    return {
        "study": "E348 what a restored gate does not protect in retrospect",
        "evidence_cutoff": datetime.now().astimezone().isoformat(timespec="seconds"),
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "definition": {
            "source": "results/state_tilt/GATEABSENCE-2026-11-01.json (E345 windows that have a restore)",
            "clauses": {k: text for k, text, _f in CLAUSES},
            "clauses_frozen_from": "smoke_test.py at HEAD: check('product: futures TSMOM face is "
                                  "current, capped and not an order', _ok, ...)",
            "population": "every commit in (removal, restore) on this line, replayed from its own "
                          "tree; the face and the futures panel are read as blobs at that commit, "
                          "and panel tails are resolved per distinct blob so cost tracks blob "
                          "count, not commit count",
            "states": "held | violated | not_evaluable; an unevaluable clause is never counted as "
                      "held, and a commit with no evaluable clause does not count as clean",
            "not_measured": "the suite's own verdicts inside the window (that is E345); this face "
                            "only asks what a correct gate would have said",
        },
        "head": head[:11],
        "replay_head": head,
        "panel_paths": panel_paths,
        "windows": out_windows,
        "summary": summary,
        "verdict": verdict,
    }


def _epoch(iso_text):
    return int(datetime.strptime(iso_text[:19], "%Y-%m-%dT%H:%M:%S").timestamp())


def _load_head_face():
    p = os.path.join(ROOT, SIGNAL)
    if not os.path.exists(p):
        return None
    try:
        return json.load(io.open(p, encoding="utf-8"))
    except Exception:
        return None


def _head_panel_tail(panel_paths):
    tails = []
    for rel in panel_paths:
        p = os.path.join(ROOT, rel)
        try:
            with io.open(p, encoding="utf-8", errors="replace") as fh:
                lines = [l for l in fh.read().splitlines() if l.strip()]
            if len(lines) > 1:
                t = panel_tail("\n".join(lines))
                if t:
                    tails.append(t)
        except Exception:
            pass
    return max(tails) if tails else None


def _why(verdict, counts, arrived_together):
    if verdict == "nothing_to_evaluate":
        base = ("no clause was evaluable at any commit inside the window: the face was not in "
                "this line's tree for the whole window")
        if arrived_together:
            base += ("; the gate and its subject first appear in the SAME commit (the merge that "
                     "restored the check), so the window was empty rather than clean")
        return base
    if verdict == "violation_was_relayed":
        bad = [k for k in CLAUSE_KEYS if counts[k]["violated"]]
        return "clause(s) stood violated inside the window: %s" % ", ".join(bad)
    return "the face existed and every evaluable clause held at every commit where it existed"


def write(face):
    os.makedirs(FACE_DIR, exist_ok=True)
    for name in (FACE_NAME, LATEST):
        with io.open(os.path.join(FACE_DIR, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
    return os.path.join(FACE_DIR, FACE_NAME)


# ---------------------------------------------------------------- selftest
def selftest():
    legs, fails = [], []

    def leg(name, cond, detail=""):
        (legs if cond else fails).append(name + ((" -- " + detail) if detail and not cond else ""))

    good = {"actionable": False, "shadow": True, "book": {"gross": 3.0},
            "generated_for_bar": "2026-10-28", "staleness": {"stale": False}}
    cl = evaluate(good, "2026-10-28")
    leg("L1 a fully satisfied face holds all five clauses",
        all(s == "held" for s, _ in cl.values()), str(cl))

    bad = dict(good, actionable=True)
    leg("L2 an actionable face violates the not-an-order clause",
        evaluate(bad, "2026-10-28")["actionable_is_false"][0] == "violated")

    leg("L3 a stale face violates the currency clause",
        evaluate(dict(good, staleness={"stale": True}), "2026-10-28")["not_stale"][0] == "violated")

    leg("L4 a face on an older bar than the panel violates the panel-tail clause",
        evaluate(good, "2026-10-29")["bar_matches_panel_tail"][0] == "violated")

    over = dict(good, book={"gross": 3.0 + 1e-6})
    leg("L5 gross over the cap violates it, and the 1e-9 tolerance is the only slack",
        evaluate(over, "2026-10-28")["gross_within_cap"][0] == "violated"
        and evaluate(dict(good, book={"gross": 3.0 + 1e-12}), "2026-10-28")["gross_within_cap"][0] == "held")

    leg("L6 a non-numeric gross is not evaluable, never held",
        evaluate(dict(good, book={"gross": "3.0"}), "2026-10-28")["gross_within_cap"][0]
        == "not_evaluable")

    leg("L7 a missing face makes every clause not evaluable",
        all(s == "not_evaluable" for s, _ in evaluate(None, "2026-10-28").values()))

    leg("L8 a missing panel tail makes the currency clause not evaluable, not violated",
        evaluate(good, None)["bar_matches_panel_tail"][0] == "not_evaluable")

    leg("L9 a missing staleness block is not evaluable (absent != fresh)",
        evaluate({k: v for k, v in good.items() if k != "staleness"}, "2026-10-28")["not_stale"][0]
        == "not_evaluable")

    # verdict precedence
    rows_absent = [{"clauses_evaluable": 0, "clauses_violated": 0}] * 3
    leg("L10 no evaluable commit anywhere -> nothing_to_evaluate",
        verdict_of(rows_absent) == "nothing_to_evaluate")
    rows_clean = [{"clauses_evaluable": 5, "clauses_violated": 0}]
    leg("L11 an evaluable window with no violation -> window_was_clean",
        verdict_of(rows_clean) == "window_was_clean")
    rows_mixed = [{"clauses_evaluable": 0, "clauses_violated": 0},
                  {"clauses_evaluable": 4, "clauses_violated": 1}]
    leg("L12 one violated commit anywhere -> violation_was_relayed",
        verdict_of(rows_mixed) == "violation_was_relayed")
    leg("L13 unevaluable commits do not dilute a clean window into nothing",
        verdict_of([{"clauses_evaluable": 0, "clauses_violated": 0},
                    {"clauses_evaluable": 5, "clauses_violated": 0}]) == "window_was_clean")

    # tally must count each clause independently
    t = tally([{"clauses": {"actionable_is_false": ("held", ""),
                            "shadow_is_true": ("violated", "")}},
               {"clauses": {"actionable_is_false": ("held", ""),
                            "shadow_is_true": ("held", "")}}])
    leg("L14 the tally is per clause, and unlisted clauses stay zero",
        t["actionable_is_false"] == {"held": 2, "violated": 0, "not_evaluable": 0}
        and t["shadow_is_true"] == {"held": 1, "violated": 1, "not_evaluable": 0}
        and t["not_stale"] == {"held": 0, "violated": 0, "not_evaluable": 0}, str(t))

    # panel tail parsing: header line is not a bar
    leg("L15 panel tail is the last data row's date, not the header",
        panel_tail("date,open,high,low,close\n2026-10-27,1,1,1,1\n2026-10-28,2,2,2,2") == "2026-10-28")
    leg("L16 a header-only panel has no tail",
        panel_tail("date,open,high,low,close") is None)
    leg("L17 an empty panel has no tail", panel_tail("") is None)

    # rounds: a postscript row never establishes a round start
    fx = [{"round": 5, "epoch": 100, "postscript": False},
          {"round": 5, "epoch": 160, "postscript": True},
          {"round": 6, "epoch": 200, "postscript": False}]
    leg("L18 rounds map by the last row at or before the stamp", round_at(fx, 150) == 5)
    leg("L19 a stamp after the next round row belongs to that round", round_at(fx, 260) == 6)
    leg("L20 a stamp before every row has no round", round_at(fx, 50) is None)

    # the frozen clause table still describes the published gate
    try:
        text = io.open(os.path.join(ROOT, GUARDED), encoding="utf-8", errors="replace").read()
        label = "product: futures TSMOM face is current, capped and not an order"
        i = text.find(label)
        # the condition is computed BEFORE the check call, so the window has to reach
        # backwards: a slice starting at the label misses every field it compares.
        body = text[max(0, i - 1600):i + 600] if i >= 0 else ""
        missing = [f for _k, _t, fields in CLAUSES for f in fields if f not in body]
        leg("L21 the frozen clause table's fields all appear in the gate's own body",
            i >= 0 and not missing, "label_found=%s missing=%s" % (i >= 0, missing))
    except Exception as e:  # pragma: no cover
        leg("L21 the frozen clause table's fields all appear in the gate's own body", False, str(e))

    print("E348 selftest %d/%d" % (len(legs), len(legs) + len(fails)))
    for f in fails:
        print("FAIL", f)
    return 0 if not fails else 1


def verify():
    p = os.path.join(FACE_DIR, FACE_NAME)
    if not os.path.exists(p):
        print("verify: no face")
        return 2
    face = json.load(io.open(p, encoding="utf-8"))
    problems = []
    if not face.get("windows"):
        problems.append("no windows published")
    for w in face.get("windows", []):
        if w["verdict"] not in ("nothing_to_evaluate", "window_was_clean",
                                "violation_was_relayed"):
            problems.append("%s: verdict outside the frozen vocabulary" % w["name"][:40])
        if w["face_present_commits"] == 0 and w["verdict"] != "nothing_to_evaluate":
            problems.append("%s: no commit carried the face but the verdict is not "
                            "nothing_to_evaluate" % w["name"][:40])
        if w["verdict"] == "violation_was_relayed" and not w.get("first_violation"):
            problems.append("%s: violation verdict with no violating commit" % w["name"][:40])
        for k in CLAUSE_KEYS:
            c = w["clause_counts"][k]
            if sum(c.values()) != w["commits_replayed"]:
                problems.append("%s: %s counts %r do not sum to the replayed commits"
                                % (w["name"][:40], k, c))
        if w["assertion_and_subject_arrived_together"] and w["face_present_commits"] != 0:
            problems.append("%s: 'arrived together' is published beside commits that carried "
                            "the face" % w["name"][:40])

    # re-derive from git and compare: the face must not be its own evidence.
    # The post-restore replay is pinned to the face's own replay_head, otherwise every
    # new commit would read as drift in a measurement that is time-scoped by design.
    fresh = build(head=face.get("replay_head"))
    old = {w["name"]: w for w in face.get("windows", [])}
    new = {w["name"]: w for w in fresh.get("windows", [])}
    if set(old) != set(new):
        problems.append("window set changed: %r -> %r" % (sorted(old), sorted(new)))
    for name in sorted(set(old) & set(new)):
        for key in ("verdict", "face_present_commits", "clause_counts",
                    "assertion_and_subject_arrived_together", "restore_sha",
                    "clauses_at_restore_commit"):
            if old[name].get(key) != new[name].get(key):
                problems.append("%s: %s moved %r -> %r"
                                % (name[:40], key, old[name].get(key), new[name].get(key)))
        oa = old[name].get("after_the_restore") or {}
        na = new[name].get("after_the_restore") or {}
        for key in ("commits", "face_present_commits", "commits_with_a_violation",
                    "clause_counts", "replay_head", "distinct_face_blobs",
                    "distinct_panel_tails", "one_observation_repeated"):
            if oa.get(key) != na.get(key):
                problems.append("%s: after_the_restore.%s moved %r -> %r"
                                % (name[:40], key, oa.get(key), na.get(key)))

    # the frozen table must still describe the gate in the guarded file
    try:
        text = io.open(os.path.join(ROOT, GUARDED), encoding="utf-8", errors="replace").read()
        label = "product: futures TSMOM face is current, capped and not an order"
        i = text.find(label)
        body = text[max(0, i - 1600):i + 600] if i >= 0 else ""
        missing = sorted({f for _k, _t, fields in CLAUSES for f in fields if f not in body})
        if i < 0:
            problems.append("the guarded check label is gone from %s" % GUARDED)
        elif missing:
            problems.append("the gate no longer mentions %r -- the clause table is stale"
                            % (missing,))
    except Exception as e:
        problems.append("guarded file unreadable: %s" % e)

    print("verify: %d problems" % len(problems))
    for x in problems:
        print(" -", x)
    return 0 if not problems else 1


def main(argv):
    mode = (argv[1] if len(argv) > 1 else "run").lower()
    if mode == "selftest":
        return selftest()
    if mode == "verify":
        return verify()
    face = build()
    path = write(face)
    print("E348 wrote", os.path.relpath(path, ROOT))
    print("verdict:", face["verdict"])
    for w in face["windows"]:
        print("  %-46s %-24s commits=%-3d face_present=%-3d together=%s"
              % (w["name"].split(": ")[-1][:46], w["verdict"], w["commits_replayed"],
                 w["face_present_commits"], w["assertion_and_subject_arrived_together"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))