"""E351 -- how many `product:` smoke gates have ever observed a second state.

E348 published one gate that stayed green for 279 commits because its subject never moved
(1 distinct face blob, 1 distinct panel tail).  This is the census question over the whole
`product:` family: for every check label beginning ``product:``, resolve the face files its own
try-body reads, replay this line's commit history for those paths, and count how many distinct
blob states each gate's subject has actually taken.

  (1) gates = distinct ``check("product: ...")`` labels in smoke_test.py (the label is the id;
      duplicated labels across a try/except pair are one gate);
  (2) a gate's subject = every path-shaped string literal inside the enclosing ``try`` body of
      the check call (plus the check's own arguments), split into ``results/`` faces and
      ``data/`` companions.  Wildcard literals are published as unresolved, never expanded:
      a glob is not a subject;
  (3) history = one ``git log --raw`` over the union of subject paths, pinned at HEAD and
      limited to the last N non-merge commits (``replay_head`` published);
  (4) per gate, the state at commit k = the blobs of its subjects as of k (absent if never
      written yet), so the distinct-state count is over commits, not over writes;
  (5) class: never_evaluated (subject absent in every window commit) | frozen_subject
      (exactly one distinct state, so every green run is the same observation) | live_subject
      (>= 2 states).

Nothing is executed from the analysis; this reads source and git objects only.

Usage:
  python scripts/e351_gate_state_census.py build      # write the face
  python scripts/e351_gate_state_census.py verify     # re-derive + compare to face
  python scripts/e351_gate_state_census.py selftest   # offline fixture legs
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-01"
FACE = "GATESTATE-%s.json" % TODAY
LATEST = "gatestate_latest.json"
STUDY = "E351_gate_state_census"
SELF_REL = "scripts/e351_gate_state_census.py"

SMOKE_REL = "smoke_test.py"
DEADLINE = "2026-11-01"
REPLAY_COMMITS = 300
MAX_ROWS = 40
MATURE_COMMITS = 50
SELF_LEG_PREFIX = "product: the product-gate state census"

PATH_RE = re.compile(r"^(results|data|docs)/[A-Za-z0-9_./-]+$")
FACE_KEYS = ("verdict", "states")


def say(message):
    sys.stdout.write(str(message) + "\n")


def sha16(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


# ----------------------------------------------------------------- source side

def _walk_parents(nodes):
    """parent map for an AST."""
    parents = {}
    for node in ast.walk(nodes):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    return parents


def _try_body_for(node, parents):
    """the nearest enclosing ``try`` body -- the scope a check's subject is loaded in.

    The fallback is the check's own arguments, never the enclosing function: a literal anywhere
    in the function is not evidence that this check reads it (selftest leg names the difference).
    """
    cur = node
    while cur in parents:
        cur = parents[cur]
        if isinstance(cur, ast.Try):
            return cur.body
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
            return []
    return []


def _strings(nodes):
    out = []
    for stmt in nodes:
        for sub in ast.walk(stmt):
            if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                out.append(sub.value)
    return out


def paths_in(strings):
    """split literals into (face paths, companion paths, wildcard literals).

    A literal is a path only when it resolves to a repo-relative file name under a known root;
    anything with a wildcard character is published separately and never expanded.
    """
    faces, companions, wildcards, other = [], [], [], []
    for raw in strings:
        text = raw.strip()
        if not PATH_RE.match(text):
            if any(ch in text for ch in "*?[") and text.startswith(("results/", "data/")):
                wildcards.append(text)
            continue
        if any(ch in text for ch in "*?["):
            wildcards.append(text)
        elif text.startswith("results/"):
            faces.append(text)
        else:
            companions.append(text)
    return sorted(set(faces)), sorted(set(companions)), sorted(set(wildcards))


def collect_gates(source, filename=SMOKE_REL):
    """every distinct `product:` check label with its subject paths."""
    tree = ast.parse(source, filename=filename)
    parents = _walk_parents(tree)
    gates = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = getattr(func, "id", None) or getattr(func, "attr", None)
        if name != "check" or not node.args:
            continue
        first = node.args[0]
        if not (isinstance(first, ast.Constant) and isinstance(first.value, str)):
            continue
        label = first.value
        if not label.startswith("product:"):
            continue
        # the check's own arguments carry the comparison companions; the try body carries
        # the face it loaded.  Label strings are never paths, so they drop out below.
        body = _try_body_for(node, parents)
        strings = _strings(body) + _strings([node])
        faces, companions, wildcards = paths_in(strings)
        row = gates.setdefault(label, {"label": label, "sites": 0,
                                       "faces": set(), "companions": set(),
                                       "wildcards": set()})
        row["sites"] += 1
        row["faces"].update(faces)
        row["companions"].update(companions)
        row["wildcards"].update(wildcards)
    out = []
    for label in sorted(gates):
        row = gates[label]
        out.append({"label": label, "sites": row["sites"],
                    "faces": sorted(row["faces"]),
                    "companions": sorted(row["companions"]),
                    "wildcards": sorted(row["wildcards"])})
    return out


# ----------------------------------------------------------------- git side

def git(args, cwd=ROOT):
    proc = subprocess.run(["git"] + args, cwd=cwd, capture_output=True)
    return proc.stdout.decode("utf-8", "replace"), proc.returncode


def replay_head(cwd=ROOT):
    out, rc = git(["rev-parse", "HEAD"], cwd=cwd)
    return out.strip() if rc == 0 else ""


RAW_RE = re.compile(r"^:(\d{6}) (\d{6}) ([0-9a-f]{7,40}) ([0-9a-f]{7,40}) ([A-Z])\t(.+)$")


def parse_raw_log(text):
    """parse `git log --raw --format=COMMIT %H` into (commits, events).

    commits: chronological list of commit shas (oldest first).
    events: {commit_index: {path: new_blob_or_None}} -- only paths that changed, in order.
    """
    commits, events = [], {}
    for line in text.splitlines():
        if line.startswith("COMMIT "):
            commits.append(line.split(None, 1)[1].strip())
            continue
        m = RAW_RE.match(line)
        if not m:
            continue
        old, new, status, path = m.group(3), m.group(4), m.group(5), m.group(6)
        idx = len(commits) - 1
        if idx < 0:
            continue
        events.setdefault(idx, {})[path] = None if set(new) == {"0"} else new
    commits.reverse()
    events = {len(commits) - 1 - k: v for k, v in events.items()}
    return commits, events


def blob_states(paths, commits, events, n_commits):
    """per-path blob as of each commit index (None where the path is not yet written)."""
    tracked = {p: [None] * n_commits for p in paths}
    for idx in range(n_commits):
        for path, blob in (events.get(idx) or {}).items():
            if path in tracked:
                tracked[path][idx] = blob
    for path, seq in tracked.items():
        last = None
        for idx in range(n_commits):
            if seq[idx] is None and last is not None:
                seq[idx] = last
            elif seq[idx] is not None:
                last = seq[idx]
    return tracked


def gate_states(gate, tracked):
    """distinct subject states over the window + absent-commit count."""
    faces = [p for p in gate["faces"] if p in tracked]
    companions = [p for p in gate["companions"] if p in tracked]
    if not faces and not companions:
        return {"distinct_states": 0, "absent_commits": 0, "window_commits": 0,
                "states": [], "resolved": []}
    series = [tracked[p] for p in faces + companions]
    n = len(series[0]) if series else 0
    seen, order, absent = set(), [], 0
    for idx in range(n):
        state = tuple(s[idx] for s in series)
        if all(v is None for v in state):
            absent += 1
            continue
        if state not in seen:
            seen.add(state)
            order.append([v or "ABSENT" for v in state])
    return {"distinct_states": len(order), "absent_commits": absent, "window_commits": n,
            "present_commits": n - absent, "states": order[:8], "resolved": faces + companions}


def classify(row):
    if not row["resolved"]:
        return "unresolved_subject"
    if row["distinct_states"] == 0:
        return "never_evaluated"
    if row["distinct_states"] == 1:
        return "frozen_subject"
    return "live_subject"


# ----------------------------------------------------------------- build / verify

def build_face(root=ROOT, pin=None):
    smoke = os.path.join(root, SMOKE_REL)
    with open(smoke, encoding="utf-8") as fh:
        source = fh.read()
    gates = collect_gates(source)
    # E319/E207 family: a study that reads a corpus must not count the leg it adds to that corpus.
    # The leg this study wires into smoke_test.py is a `product:` gate whose subject is this very
    # face, so counting it would make the census a function of its own publication.
    self_labels = [g["label"] for g in gates if SELF_LEG_PREFIX in g["label"]]
    gates = [g for g in gates if SELF_LEG_PREFIX not in g["label"]]
    head = pin or replay_head(root)
    all_paths = sorted({p for g in gates for p in g["faces"] + g["companions"]})
    text, rc = git(["log", "--no-merges", "-n", str(REPLAY_COMMITS), head,
                    "--format=COMMIT %H", "--raw", "--no-abbrev", "--", *all_paths], cwd=root)
    commits, events = parse_raw_log(text) if rc == 0 else ([], {})
    tracked = blob_states(all_paths, commits, events, len(commits))

    rows = []
    for gate in gates:
        row = gate_states(gate, tracked)
        row.update({"label": gate["label"], "sites": gate["sites"],
                    "faces": gate["faces"], "companions": gate["companions"],
                    "wildcards": gate["wildcards"]})
        row["class"] = classify(row)
        rows.append(row)

    from collections import Counter
    counts = Counter(r["class"] for r in rows)
    frozen = [r for r in rows if r["class"] == "frozen_subject"]
    live = [r for r in rows if r["class"] == "live_subject"]
    most = max(live, key=lambda r: r["distinct_states"]) if live else None
    unread = [r for r in rows if r["class"] == "unresolved_subject"]
    never = [r for r in rows if r["class"] == "never_evaluated"]
    evaluated = len(frozen) + len(live)
    share = (100.0 * len(frozen) / evaluated) if evaluated else 0.0

    summary = {
        "smoke_source": SMOKE_REL,
        "product_gates": len(rows),
        "gates_with_subject": len(rows) - len(unread),
        "gates_unresolved_subject": len(unread),
        "class_counts": dict(sorted(counts.items())),
        "frozen_subject_gates": len(frozen),
        "live_subject_gates": len(live),
        "never_evaluated_gates": len(never),
        "green_by_freeze_share_pct": round(share, 1),
        "frozen_mature": sorted(r["label"] for r in frozen if r["present_commits"] >= MATURE_COMMITS),
        "frozen_young": sorted(r["label"] for r in frozen if r["present_commits"] < MATURE_COMMITS),
        "mature_commits_threshold": MATURE_COMMITS,
        "frozen_present_commits": {r["label"]: r["present_commits"] for r in frozen},
        "distinct_subject_paths": len(all_paths),
        "replay_head": head,
        "replay_commits": len(commits),
        "replay_commits_requested": REPLAY_COMMITS,
        "most_moved_gate": most["label"] if most else None,
        "most_moved_states": most["distinct_states"] if most else 0,
        "wildcard_literals_published_unexpanded": sorted({w for r in rows for w in r["wildcards"]})[:20],
        "self_legs_excluded": self_labels,
    }
    headline = {
        "frozen_share_of_evaluated": summary["green_by_freeze_share_pct"],
        "frozen": len(frozen), "live": len(live),
        "unresolved": len(unread), "never": len(never),
        "gates": len(rows), "commits": len(commits),
    }
    face = {
        "schema": "gate-state-census/v1",
        "study": STUDY,
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": DEADLINE,
        "generated_by": "bm-b r1372",
        "source_rel": SELF_REL,
        "method": ("per `product:` smoke gate: subject = path literals in the check's enclosing"
                   " try body; history = one git log --raw over the union of subjects, pinned at"
                   " replay_head; state at commit k = subject blobs as of k (absent if unwritten)"),
        "gate": "frozen_share_of_evaluated",
        "summary": summary,
        "headline": headline,
        "verdict": _verdict(summary),
        "rows": rows,
        "bounds": {
            "glob_subjects": "a wildcard literal is published, never expanded -- a glob is not a subject",
            "companions": "data/ companions are tracked by blob state, so a rewrite that keeps bytes identical does not register",
            "window": "the replay window is the last %d non-merge commits of this line; older states are out of scope" % REPLAY_COMMITS,
            "execution": "nothing is executed: a gate with >=2 states is live as a *subject*, not proven to have failed",
        },
    }
    return face


def _verdict(summary):
    if summary["product_gates"] == 0:
        return "no_product_gate_was_found_in_the_smoke_source_so_no_claim_is_made"
    if summary["live_subject_gates"] == 0:
        return "no_product_gate_has_observed_a_second_subject_state_in_this_window"
    if not (summary.get("frozen_mature") or []):
        return ("%d_of_%d_product_gates_that_resolve_a_subject_never_saw_it_change_but_all_%d_are_"
                "younger_than_%d_commits_so_no_gate_has_been_green_against_a_long_still_subject" % (
                    summary["frozen_subject_gates"],
                    summary["frozen_subject_gates"] + summary["live_subject_gates"],
                    len(summary.get("frozen_young") or []),
                    summary.get("mature_commits_threshold", 0)))
    return ("%d_of_%d_product_gates_that_resolve_a_subject_never_saw_it_change_so_%.1f_pct_of_"
            "their_green_runs_are_the_same_observation_and_%d_of_them_have_held_that_state_for_at_"
            "least_%d_commits" % (
                summary["frozen_subject_gates"],
                summary["frozen_subject_gates"] + summary["live_subject_gates"],
                summary["green_by_freeze_share_pct"],
                len(summary["frozen_mature"]),
                summary.get("mature_commits_threshold", 0)))


def write_face(face, root=ROOT):
    outdir = os.path.join(root, "results", "state_tilt")
    os.makedirs(outdir, exist_ok=True)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    for name in (FACE, LATEST):
        with open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    return body


def verify(root=ROOT):
    path = os.path.join(root, "results", "state_tilt", FACE)
    problems = []
    if not os.path.exists(path):
        return ["face absent: %s" % FACE]
    with open(path, encoding="utf-8") as fh:
        published = json.load(fh)
    pin = (published.get("summary") or {}).get("replay_head") or None
    if not pin:
        return ["replay_head not published, so the window cannot be replayed"]
    fresh = build_face(root, pin=pin)
    if fresh["verdict"] != published.get("verdict"):
        problems.append("verdict does not re-derive")
    if fresh["summary"]["class_counts"] != published.get("summary", {}).get("class_counts"):
        problems.append("class counts do not re-derive")
    if fresh["summary"]["replay_commits"] != published.get("summary", {}).get("replay_commits"):
        problems.append("replay window length does not re-derive at its own pin")
    pub_rows = {r["label"]: r["class"] for r in published.get("rows") or []}
    new_rows = {r["label"]: r["class"] for r in fresh["rows"]}
    if pub_rows != new_rows:
        drift = sorted(set(pub_rows) ^ set(new_rows))[:3]
        problems.append("gate classes drifted at the pin (%d labels differ; e.g. %s)"
                        % (len(set(pub_rows) ^ set(new_rows)), drift))
    return problems


# ----------------------------------------------------------------- selftest

def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    src = (
        "def run():\n"
        "    try:\n"
        "        d = json.load(open('results/a/x.json', encoding='utf-8'))\n"
        "        p = json.load(open('data/panel/y.csv'))\n"
        "        check('product: gate A', d.get('v') == 1, 'panel=%s' % p)\n"
        "    except Exception as e:\n"
        "        check('product: gate A', False, str(e))\n"
        "    try:\n"
        "        g = json.load(open('results/b/*.json'))\n"
        "        check('product: gate B', bool(g), 'wild')\n"
        "    except Exception as e:\n"
        "        check('product: gate B', False, str(e))\n"
        "    check('product: gate C', True, 'no face')\n"
        "    check('other: not a product gate', True)\n"
        "    outside = 'results/c/never.json'\n"
    )
    gates = collect_gates(src, "fixture_smoke.py")
    by = {g["label"]: g for g in gates}
    leg("only product: labels are gates", list(by) == ["product: gate A", "product: gate B",
                                                       "product: gate C"])
    leg("duplicate label across try/except is one gate with 2 sites", by["product: gate A"]["sites"] == 2)
    leg("face from the try body is the subject", by["product: gate A"]["faces"] == ["results/a/x.json"])
    leg("data companion is separated from faces", by["product: gate A"]["companions"] == ["data/panel/y.csv"])
    leg("label text is never a path", "product: gate A" not in json.dumps(by["product: gate A"]["faces"]))
    leg("a literal outside the try body is not a subject", not by["product: gate C"]["faces"])
    leg("wildcard literal is published unexpanded", by["product: gate B"]["wildcards"] == ["results/b/*.json"])
    leg("wildcard is not a face", by["product: gate B"]["faces"] == [])
    leg("non-product labels are ignored", "other: not a product gate" not in by)

    A = "a" * 40
    B = "b" * 40
    C = "c" * 40
    raw = (
        "COMMIT c3\n"
        ":100644 100644 %s %s M\tresults/a/x.json\n"
        "\n"
        "COMMIT c2\n"
        ":100644 100644 %s %s A\tresults/a/x.json\n"
        "\n"
        "COMMIT c1\n"
    ) % (A, B, "0" * 40, C)
    commits, events = parse_raw_log(raw)
    leg("raw log is read oldest-first", commits == ["c1", "c2", "c3"])
    leg("add event carries the new blob", events.get(1, {}).get("results/a/x.json") == C)
    tracked = blob_states(["results/a/x.json"], commits, events, len(commits))
    leg("a path unwritten at commit 1 reads ABSENT", tracked["results/a/x.json"][0] is None)
    leg("blob holds forward without a new event", tracked["results/a/x.json"][2] == B)

    gate = {"faces": ["results/a/x.json"], "companions": []}
    # frozen = written once, never rewritten: the same blob at every commit it is present at.
    frozen = gate_states(gate, blob_states(["results/a/x.json"], ["c1", "c2"],
                                          {0: {"results/a/x.json": B}}, 2))
    leg("one state classifies frozen", classify(frozen) == "frozen_subject")
    leg("a frozen subject was written at some point", frozen["distinct_states"] == 1)
    live = gate_states(gate, tracked)
    leg("two states classify live", classify(live) == "live_subject")
    never = gate_states(gate, blob_states(["results/a/x.json"], ["c1"], {}, 1))
    absent = {"faces": [], "companions": []}
    leg("no resolved subject is not frozen", classify(gate_states(absent, {})) == "unresolved_subject")
    empty = gate_states({"faces": ["results/zz/none.json"], "companions": []},
                        blob_states(["results/zz/none.json"], ["c1"], {}, 1))
    leg("a subject absent throughout is never_evaluated", classify(empty) == "never_evaluated")
    leg("absent commits are counted, not folded into states", empty["absent_commits"] == 1)
    leg("never_evaluated is never counted as frozen", classify(empty) != "frozen_subject")

    # the share denominator is evaluated gates only: unresolved/never must not dilute it
    fake = {"product_gates": 4, "live_subject_gates": 1, "frozen_subject_gates": 1,
            "green_by_freeze_share_pct": 50.0, "frozen_mature": [], "frozen_young": ["a"],
            "mature_commits_threshold": 50}
    leg("verdict names both the count and the share when a subject is mature",
        "50.0" in _verdict(dict(fake, frozen_mature=["a"], frozen_young=[]))
        and "1_of_2" in _verdict(dict(fake, frozen_mature=["a"], frozen_young=[])))
    leg("a young-only freeze says so instead of claiming green-by-freeze",
        "younger_than_50" in _verdict(fake) and "50.0" not in _verdict(fake))
    leg("empty population makes no claim", "no_claim" in _verdict({"product_gates": 0}))
    leg("no live subject makes a different claim",
        "no_product_gate_has_observed" in _verdict({"product_gates": 2, "live_subject_gates": 0}))

    from collections import Counter
    leg("leg count", len(legs) >= 20)
    passed = sum(1 for _, ok in legs if ok)
    for name, ok in legs:
        say(("PASS " if ok else "FAIL ") + name)
    say("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv):
    mode = (argv[1] if len(argv) > 1 else "build").lower()
    if mode == "selftest":
        return selftest()
    if mode == "verify":
        problems = verify()
        for p in problems:
            say("PROBLEM " + p)
        say("verify: %d problems" % len(problems))
        return 0 if not problems else 1
    face = build_face()
    write_face(face)
    s = face["summary"]
    say("gates=%d evaluated=%d frozen=%d live=%d unresolved=%d never=%d share=%.1f%% commits=%d"
        % (s["product_gates"], s["frozen_subject_gates"] + s["live_subject_gates"],
           s["frozen_subject_gates"], s["live_subject_gates"], s["gates_unresolved_subject"],
           s["never_evaluated_gates"], s["green_by_freeze_share_pct"], s["replay_commits"]))
    say("verdict: " + face["verdict"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))