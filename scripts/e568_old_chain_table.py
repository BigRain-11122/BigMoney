"""E568 (r1599 bm-b): is the table of a pre-receipt round still recoverable from git?

E567 judged 28 of 878 printed chain sentences and could not judge 809 of them for one reason:
the receipt corpus starts at r1204, and the join it uses needs a receipt to name the round.  Its
own note said the missing half is a property of the *runner source at that round* and git still
has every version of it.  This study tests that sentence instead of assuming it.

Two ways to ask git for the table, priced separately:

  * ``arm_canonical`` -- guess the path.  ``Tools/s6_chain_bm<X>.py`` at the round's own commit.
    This is what E561 does for the rounds that have receipts.
  * ``arm_tree_scan`` -- do not guess.  List the tree of that commit and keep every path under
    ``results/`` or ``Tools/`` whose basename carries both an ``s6`` and a ``chain`` token and
    that round's own number, then take the first one that yields a legs count.

A guess can only find a file that was still there under the name we guessed.  A scan finds the
per-round script a round actually committed (``results/_r098bmc_s6_chain.ps1``), which is a
different naming convention, and which is where most of the pre-receipt tables live.

Counting the legs is done from the source, never from a sentence:

  * ``.py``  -- ``ast``: ``len(LEGS)`` of the module's own table.
  * ``.ps1`` -- the ``$legs = @( ... )`` block, counted by its ``@{n=`` items.

Every claim in the population is then reclassified against the recovered table, and the classes
are re-derived in :func:`face_problems` so a published label cannot be hand-set.

  python scripts/e568_old_chain_table.py build      # write the dated face + latest
  python scripts/e568_old_chain_table.py check      # re-derive the population and every witness
  python scripts/e568_old_chain_table.py check-fast # re-read the published witnesses only
  python scripts/e568_old_chain_table.py verify     # re-derive, print problems
  python scripts/e568_old_chain_table.py selftest   # fixtures only
"""
from __future__ import annotations

import ast
import hashlib
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EVIDENCE_CUTOFF = "2026-11-08"
DATED_PREFIX = "OLDCHAINTABLE"
STATE_TILT = os.path.join(ROOT, "results", "state_tilt")
LATEST = os.path.join(STATE_TILT, "oldchaintable_latest.json")
DATED = os.path.join(STATE_TILT, "%s-%s.json" % (DATED_PREFIX, EVIDENCE_CUTOFF))

# the population is E567's unjudged-for-one-reason class, taken from its own face
E567_MODULE = "e567_chain_claim"
POPULATION_CLASS = "the_round_carries_no_receipt_in_the_corpus"

# ---- the two arms ---------------------------------------------------------------
ARM_CANON = "arm_canonical_path"
ARM_TREE = "arm_tree_scan"
ARM_BOTH = "both_arms_found_it"

# ---- what a claim becomes once the table is recovered -----------------------------
G_EQUALS = "the_denominator_equals_the_table_recovered_from_git"
G_LABELLED = "the_denominator_is_below_the_table_and_the_sentence_says_it_is_a_subset"
G_SILENT = "the_denominator_is_below_the_table_and_the_sentence_reads_as_the_whole_chain"
G_ABOVE = "the_denominator_is_larger_than_the_table_recovered_from_git"
G_NO_COMMIT = "no_commit_in_local_history_for_that_round"
G_NO_SCRIPT = "that_commit_carries_no_chain_script_naming_the_round"
G_NO_TABLE = "a_chain_script_was_found_but_no_legs_table_could_be_read_from_it"
G_EMPTY_TABLE = "a_legs_table_was_read_but_it_says_zero_legs"

G_CLASSES = (G_EQUALS, G_LABELLED, G_SILENT, G_ABOVE,
             G_NO_COMMIT, G_NO_SCRIPT, G_NO_TABLE, G_EMPTY_TABLE)
G_JUDGED = (G_EQUALS, G_LABELLED, G_SILENT, G_ABOVE)
G_UNJUDGED = (G_NO_COMMIT, G_NO_SCRIPT, G_NO_TABLE, G_EMPTY_TABLE)

V_SILENT = ("git_does_still_hold_the_table_of_a_pre_receipt_round_and_a_few_sentences_read_as_"
            "the_whole_chain_while_printing_less_than_it")
V_ALL_NAME = ("git_does_still_hold_the_table_of_a_pre_receipt_round_and_every_recovered_sentence_"
              "names_it_or_says_it_is_a_subset")
V_BLIND = "the_tables_could_not_be_recovered_so_git_does_not_answer_this_and_nothing_is_concluded"
V_GUESS_ONLY = ("guessing_the_canonical_path_finds_almost_nothing_and_the_tree_scan_is_what_"
                "recovers_the_table")

ROUND_SUBJECT = (r"^round (\d+):", r"^[Rr]ound (\d+)\b", r"^r(\d+)\b")
TREE_ROOTS = ("results/", "Tools/")


# ---- git helpers ----------------------------------------------------------------
def _git(args, timeout=240):
    try:
        p = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True, timeout=timeout)
    except Exception:
        return None
    if p.returncode != 0:
        return None
    return p.stdout


def round_commits():
    """round number -> the first commit whose subject names that round.

    The whole local history is read, not a window: the whole point of the study is rounds that
    predate the receipt corpus, and a window that stops at r809 would answer a different question.
    """
    raw = _git(["log", "--format=%H%x09%s"])
    if raw is None:
        return {}
    out = {}
    for line in raw.decode("utf-8", "replace").splitlines():
        sha, _, subject = line.partition("\t")
        subject = subject.strip()
        for pat in ROUND_SUBJECT:
            m = re.match(pat, subject)
            if m:
                out.setdefault(int(m.group(1)), sha.strip())
                break
    return out


def blobs(specs):
    """{spec: text} for the specs this clone can answer, through ONE cat-file process.

    A missing object is a legitimate answer (promisor clone; r1243 forbids an unattended rebase
    for the same reason) and the study prices what it could not read instead of retrying.
    """
    specs = [s for s in dict.fromkeys(specs) if s]
    if not specs:
        return {}
    payload = ("\n".join(specs) + "\n").encode("utf-8")
    try:
        p = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT, input=payload,
                           capture_output=True, timeout=300)
    except Exception:
        return {}
    if p.returncode != 0:
        return {}
    out, i, found = p.stdout, 0, {}
    for spec in specs:
        nl = out.find(b"\n", i)
        if nl < 0:
            break
        header = out[i:nl].decode("utf-8", "replace").strip()
        i = nl + 1
        parts = header.rsplit(" ", 2)
        if len(parts) != 3 or not parts[2].isdigit():
            continue  # "missing" / "ambiguous": not readable from this clone
        size = int(parts[2])
        found[spec] = out[i:i + size].decode("utf-8-sig", "replace")
        i += size + 1
    return found


_TREE_CACHE = {}


def tree_names(sha):
    if sha in _TREE_CACHE:
        return _TREE_CACHE[sha]
    out = []
    for root in TREE_ROOTS:
        raw = _git(["ls-tree", "-r", "--name-only", sha, root])
        if raw:
            out.extend(x for x in raw.decode("utf-8", "replace").splitlines() if x.strip())
    _TREE_CACHE[sha] = out
    return out


# ---- the legs table ------------------------------------------------------------
def py_leg_count(src):
    """len(LEGS) for a python runner, or None when it does not state its own list."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "LEGS" for t in node.targets):
            if isinstance(node.value, (ast.List, ast.Tuple)):
                return len(node.value.elts)
    return None


def ps1_leg_count(src):
    """``@{n=`` items inside the ``$legs = @( ... )`` block of a powershell chain.

    The block is isolated by paren depth rather than by line, because the item bodies carry
    ``{python ...}`` script blocks and a line-based reader stops on the first balanced line.
    A file without that block is not counted at all -- a whole-file count would also count the
    report-building hashtables further down and inflate the table.
    """
    m = re.search(r"\$legs\s*=\s*@\(", src)
    if not m:
        return None
    depth, i, end = 0, m.end() - 1, None
    while i < len(src):
        ch = src[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                end = i
                break
        i += 1
    if end is None:
        return None
    inner = src[m.end():end]
    # Two item shapes are in use in this corpus and both are one leg per item:
    #   @{n='compute_audit'; c={python ...}}  and  @("dualrun", "python ...")
    # Counting the interior (not the block) is what keeps the opener and any later hashtable in
    # the same file out of the number; a first version subtracted an opener that is not on its
    # own line and read the 30-leg rounds as 29 for eight rounds in a row.
    hashtable = len(re.findall(r"@\{\s*n\s*=", inner))
    pairs = len(re.findall(r"""@\(\s*['"]""", inner))
    return hashtable + pairs


def leg_count(path, src):
    if path.lower().endswith(".py"):
        return py_leg_count(src)
    if path.lower().endswith(".ps1"):
        return ps1_leg_count(src)
    return None


# ---- candidate discovery -------------------------------------------------------
def is_chain_script(name):
    base = os.path.basename(name).lower()
    return "s6" in base and "chain" in base


def round_token(rnd):
    return re.compile(r"(?:^|[^0-9])r0*%d(?:[^0-9]|$)" % rnd)


def machine_token(machine):
    return re.compile(r"bm-?%s" % re.escape(machine))


def machine_of_name(name):
    """Which machine's chain a file belongs to, or None when its name does not say.

    A round number is shared across the fleet, but the chain table is not: at r103 the bm-b table
    and the bm-c table are different lists.  Reading bm-c's script for a bm-b sentence produced
    eight of the first ten "above the table" rows in this study's first build, so a file that
    names another machine is not a witness for this one -- it is a different population.
    """
    m = re.search(r"bm-?([abc])(?![a-z])", name.lower())
    return m.group(1) if m else None


def candidates_for(sha, machine, rnd):
    """(preferred, fallback) paths in that commit's tree that could hold this round's table."""
    rtok = round_token(rnd)
    preferred, fallback = [], []
    for name in tree_names(sha):
        if not is_chain_script(name) or not rtok.search(os.path.basename(name)):
            continue
        if not name.lower().endswith((".py", ".ps1")):
            continue
        owner = machine_of_name(os.path.basename(name))
        if owner is None:
            fallback.append(name)
        elif owner == machine:
            preferred.append(name)
    return sorted(preferred), sorted(fallback)


def canonical_path(machine):
    return "Tools/s6_chain_bm%s.py" % machine


# ---- classification ------------------------------------------------------------
def classify(table, denominator, subset_label):
    if table is None:
        return None
    if table == 0:
        return G_EMPTY_TABLE
    if denominator == table:
        return G_EQUALS
    if denominator < table:
        return G_LABELLED if subset_label else G_SILENT
    return G_ABOVE


def _verdict(summary):
    s = summary
    if not s.get("claims_with_a_recovered_table"):
        return V_BLIND
    if s.get(G_SILENT):
        v = V_SILENT
    elif sum(s.get(c, 0) for c in G_JUDGED):
        v = V_ALL_NAME
    else:
        v = V_BLIND
    if s.get("canonical_only_tables", 0) == 0 and s.get("tree_scan_only_tables", 0) > 0:
        v = V_GUESS_ONLY
    return v


def _verdict_line(s):
    return ("%d of %d printed chain sentences had no receipt to join (E567); git recovers a legs "
            "table for %d of their %d distinct rounds, which makes %d of them judgeable: %d name "
            "the whole table, %d are below it and say so, %d are below it and read as the whole "
            "chain, %d are above it. %d rounds have no commit in local history, %d have a commit "
            "but no chain script naming the round, %d have a script with no readable table, %d "
            "read as zero legs. Of the %d recovered tables, %d were found only by scanning the "
            "tree and %d only by guessing the canonical path."
            % (s.get("population", 0), s.get("upstream_claims", 0),
               s.get("rounds_with_a_recovered_table", 0),
               s.get("rounds_in_population", 0), sum(s.get(c, 0) for c in G_JUDGED),
               s.get(G_EQUALS, 0), s.get(G_LABELLED, 0), s.get(G_SILENT, 0), s.get(G_ABOVE, 0),
               s.get(G_NO_COMMIT, 0), s.get(G_NO_SCRIPT, 0), s.get(G_NO_TABLE, 0),
               s.get(G_EMPTY_TABLE, 0), s.get("rounds_with_a_recovered_table", 0),
               s.get("tree_scan_only_tables", 0), s.get("canonical_only_tables", 0)))


# ---- build ---------------------------------------------------------------------
def _load_e567():
    sys.path.insert(0, HERE)
    return __import__(E567_MODULE)


def build(write=False):
    e567 = _load_e567()
    upstream = e567.build(write=False)
    population = [c for c in upstream.get("claims") or []
                  if c.get("class") == POPULATION_CLASS]

    rounds = round_commits()
    pairs = sorted({(c.get("machine"), c.get("round")) for c in population
                    if c.get("round") and c.get("machine")})

    # one pass for every file the two arms could possibly read
    wanted = {}
    for machine, rnd in pairs:
        sha = rounds.get(rnd)
        if not sha:
            continue
        pref, fall = candidates_for(sha, machine, rnd)
        specs = [sha + ":" + canonical_path(machine)]
        specs.extend(sha + ":" + p for p in pref + fall)
        wanted[(machine, rnd)] = specs
    text_of = blobs([s for v in wanted.values() for s in v])

    witness = {}
    for (machine, rnd), specs in wanted.items():
        canon = specs[0]
        canon_table = leg_count(canon.split(":", 1)[1], text_of[canon]) \
            if canon in text_of else None
        scan_table, scan_path = None, None
        for spec in specs[1:]:
            if spec not in text_of:
                continue
            val = leg_count(spec.split(":", 1)[1], text_of[spec])
            if val is not None:
                scan_table, scan_path = val, spec.split(":", 1)[1]
                break
        if canon_table is not None and scan_table is not None:
            arm = ARM_BOTH
        elif canon_table is not None:
            arm = ARM_CANON
        elif scan_table is not None:
            arm = ARM_TREE
        else:
            arm = None
        witness[(machine, rnd)] = {
            "sha": rounds.get(rnd),
            "table": canon_table if canon_table is not None else scan_table,
            "path": canonical_path(machine) if canon_table is not None else scan_path,
            "arm": arm,
            "canonical_table": canon_table,
            "tree_scan_table": scan_table,
            "tree_scan_path": scan_path,
        }

    rows = []
    for c in population:
        machine, rnd = c.get("machine"), c.get("round")
        w = witness.get((machine, rnd)) if rnd and machine else None
        if rnd is None or machine is None:
            cls, table, path, arm = G_NO_COMMIT, None, None, None
        elif not rounds.get(rnd):
            cls, table, path, arm = G_NO_COMMIT, None, None, None
        elif w is None or w["table"] is None:
            if w is None:
                cls, table, path, arm = G_NO_SCRIPT, None, None, None
            else:
                # a tree exists but nothing carried a readable table: a script named the round
                # (the pair was discoverable) or nothing did at all
                if w.get("tree_scan_path") is None:
                    # was any chain script even present for the round?
                    pref, fall = candidates_for(rounds[rnd], machine, rnd)
                    cls = G_NO_TABLE if (pref or fall) else G_NO_SCRIPT
                else:
                    cls = G_NO_TABLE
                table = path = arm = None
        else:
            table, path, arm = w["table"], w["path"], w["arm"]
            cls = classify(table, c.get("denominator"), c.get("subset_label"))
        rows.append({
            "report": c.get("report"),
            "line": c.get("line"),
            "machine": machine,
            "round": rnd,
            "numerator": c.get("numerator"),
            "denominator": c.get("denominator"),
            "subset_label": c.get("subset_label"),
            "table": table,
            "witness_path": path,
            "witness_commit": (w or {}).get("sha"),
            "witness_arm": arm,
            "class": cls,
        })

    summary = {"population": len(rows),
               "upstream_claims": len(upstream.get("claims") or []),
               "rounds_in_population": len(pairs),
               "rounds_with_a_commit": sum(1 for (m, r) in pairs if rounds.get(r)),
               "rounds_whose_tree_carries_a_chain_script": 0,
               "rounds_with_a_recovered_table": 0,
               "claims_with_a_recovered_table": 0,
               "canonical_only_tables": 0, "tree_scan_only_tables": 0,
               "both_arms_found_it": 0,
               "rows_without_a_round_or_machine": 0}
    for cls in G_CLASSES:
        summary[cls] = sum(1 for r in rows if r["class"] == cls)
    for (machine, rnd), w in witness.items():
        if w["table"] is not None:
            summary["rounds_with_a_recovered_table"] += 1
            if w["arm"] == ARM_CANON:
                summary["canonical_only_tables"] += 1
            elif w["arm"] == ARM_TREE:
                summary["tree_scan_only_tables"] += 1
            elif w["arm"] == ARM_BOTH:
                summary["both_arms_found_it"] += 1
    for (machine, rnd) in pairs:
        sha = rounds.get(rnd)
        if sha and (candidates_for(sha, machine, rnd)[0] or candidates_for(sha, machine, rnd)[1]):
            summary["rounds_whose_tree_carries_a_chain_script"] += 1
    summary["claims_with_a_recovered_table"] = sum(
        1 for r in rows if r["table"] is not None)
    summary["judged_from_git"] = sum(1 for r in rows if r["class"] in G_JUDGED)
    summary["still_unjudged"] = sum(1 for r in rows if r["class"] in G_UNJUDGED)

    pinned = hashlib.sha256(
        json.dumps(pairlist(rows), sort_keys=True).encode("utf-8")).hexdigest()

    face = {
        "study": "E568",
        "card": "E568",
        "round": 1599,
        "machine": "bm-b",
        "dept": "research+engineering",
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "note": ("the population is E567's `the_round_carries_no_receipt_in_the_corpus` class, so "
                 "the two faces partition the same 878 sentences; a table read here does not "
                 "re-open the 28 E567 judged, it only prices the 809 it could not judge"),
        "parse_rule": {
            "arms": [ARM_CANON, ARM_TREE],
            "canonical_path": "Tools/s6_chain_bm<X>.py at the round's own commit",
            "tree_roots": list(TREE_ROOTS),
            "tree_name_test": "basename carries both an 's6' and a 'chain' token and the round "
                              "token r<round> (zero-padded accepted)",
            "prefer_machine_token": "bm<X> / bm-<X> in the basename, fallback = any machine",
            "py_table": "ast: len(LEGS) of the module's own list",
            "ps1_table": "count of '@{n=' items inside the '$legs = @( ... )' block, isolated by "
                         "paren depth",
            "no_retry_on_missing_object": "a promisor clone may not hold an old blob; published "
                                          "as a class, never retried (r1243)",
        },
        "population_source": {
            "face": os.path.relpath(e567.LATEST, ROOT).replace(os.sep, "/"),
            "study": "E567",
            "class": POPULATION_CLASS,
            "claims": len(rows),
            "population_sha16": pinned[:16],
        },
        "rows": rows,
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_line": _verdict_line(summary),
    }
    face["problems"] = face_problems(face)
    if write:
        _write(LATEST, face)
        _write(DATED, face)
    return face


def pairlist(rows):
    """The population as the pin sees it: identity and value, not the witness."""
    return [[r.get("machine"), r.get("round"), r.get("line"),
             r.get("numerator"), r.get("denominator"), r.get("subset_label")]
            for r in rows]


# ---- gate ----------------------------------------------------------------------
def _write(path, obj):
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write("\n")


def face_problems(face):
    problems = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    if s.get("population") != len(rows):
        problems.append("summary.population %r != %d rows" % (s.get("population"), len(rows)))
    for cls in G_CLASSES:
        got = sum(1 for r in rows if r.get("class") == cls)
        if s.get(cls) != got:
            problems.append("summary.%s %r != %d in rows" % (cls, s.get(cls), got))
    if sum(s.get(c, 0) for c in G_CLASSES) != len(rows):
        problems.append("a row is in no class or in two")
    if s.get("judged_from_git") != sum(s.get(c, 0) for c in G_JUDGED):
        problems.append("summary.judged_from_git does not re-derive")
    if s.get("still_unjudged") != sum(s.get(c, 0) for c in G_UNJUDGED):
        problems.append("summary.still_unjudged does not re-derive")
    if s.get("claims_with_a_recovered_table") != sum(1 for r in rows if r.get("table") is not None):
        problems.append("summary.claims_with_a_recovered_table does not re-derive")
    # every row's class must follow from its own stored table and pair
    for r in rows:
        t = r.get("table")
        if t is None:
            if r.get("class") not in (G_NO_COMMIT, G_NO_SCRIPT, G_NO_TABLE):
                problems.append("row %s/%s has no table but class %r"
                                % (r.get("machine"), r.get("round"), r.get("class")))
            continue
        want = classify(t, r.get("denominator"), r.get("subset_label"))
        if r.get("class") != want:
            problems.append("row %s/%s line %s stores class %r but its own numbers give %r"
                            % (r.get("machine"), r.get("round"), r.get("line"),
                               r.get("class"), want))
        if r.get("witness_path") is None:
            problems.append("row %s/%s has a table but no witness path"
                            % (r.get("machine"), r.get("round")))
        if r.get("witness_commit") is None:
            problems.append("row %s/%s has a table but no witness commit, so it cannot be "
                            "re-read" % (r.get("machine"), r.get("round")))
    # the two arms must not be confused for one another
    if (s.get("canonical_only_tables", 0) + s.get("tree_scan_only_tables", 0)
            + s.get("both_arms_found_it", 0)) != s.get("rounds_with_a_recovered_table", 0):
        problems.append("the arm split does not sum to the recovered rounds")
    pop = face.get("population_source") or {}
    if pop.get("claims") != len(rows):
        problems.append("population_source.claims %r != %d rows" % (pop.get("claims"), len(rows)))
    pin = hashlib.sha256(json.dumps(pairlist(rows), sort_keys=True).encode("utf-8")).hexdigest()
    if pop.get("population_sha16") != pin[:16]:
        problems.append("the population pin does not re-derive from the rows")
    if not face.get("verdict"):
        problems.append("no verdict")
    else:
        want = _verdict(s)
        if face["verdict"] != want:
            problems.append("the published verdict %r is not the one its own summary derives (%r); "
                            "a verdict is computed, never written"
                            % (face["verdict"], want))
    return problems


def _fixture_face():
    """A two-row face built by hand that satisfies every gate condition."""
    rows = [
        {"report": "logs/iteration-loop/round_reports.md", "line": 1, "machine": "b",
         "round": 292, "numerator": 30, "denominator": 30, "subset_label": False,
         "table": 30, "witness_path": "results/_r292_s6_chain.ps1",
         "witness_commit": "0" * 40, "witness_arm": ARM_TREE, "class": G_EQUALS},
        {"report": "logs/iteration-loop/round_reports.md", "line": 2, "machine": "b",
         "round": 609, "numerator": 33, "denominator": 33, "subset_label": False,
         "table": None, "witness_path": None, "witness_arm": None, "class": G_NO_SCRIPT},
    ]
    pin = hashlib.sha256(json.dumps(pairlist(rows), sort_keys=True).encode("utf-8")).hexdigest()
    summary = {"population": len(rows), "upstream_claims": 2, "rounds_in_population": 2,
               "rounds_with_a_commit": 2, "rounds_whose_tree_carries_a_chain_script": 1,
               "rounds_with_a_recovered_table": 1, "claims_with_a_recovered_table": 1,
               "canonical_only_tables": 0, "tree_scan_only_tables": 1, "both_arms_found_it": 0,
               "rows_without_a_round_or_machine": 0, "judged_from_git": 1, "still_unjudged": 1}
    for cls in G_CLASSES:
        summary[cls] = sum(1 for r in rows if r["class"] == cls)
    return {"study": "E568", "card": "E568", "evidence_cutoff": EVIDENCE_CUTOFF,
            "rows": rows, "summary": summary,
            "population_source": {"claims": len(rows), "population_sha16": pin[:16]},
            # the fixture's own arm split makes the guess-only verdict its correct one
            "verdict": V_GUESS_ONLY, "verdict_line": "fixture"}


def selftest():
    arms = []

    def check(name, cond, detail=""):
        arms.append({"arm": name, "ok": bool(cond), "detail": detail})

    ps1 = ("$legs = @(\n"
           "  @{n='compute_audit'; c={python scripts\\compute_audit.py}},\n"
           "  @{n='py_watermark';  c={python scripts\\py_watermark.py probe}},\n"
           ")\n"
           "$rows = @( @{n='not a leg'} )\n")
    check("ps1 block counts only its own items", ps1_leg_count(ps1) == 2, ps1_leg_count(ps1))
    ps1_pairs = "$legs = @(\n  @(\"dualrun\", \"python a.py\"),\n  @(\"audit\", \"python b.py\"),\n)\n"
    check("ps1 pair-shape legs are counted too", ps1_leg_count(ps1_pairs) == 2,
          ps1_leg_count(ps1_pairs))
    ps1_single = "$legs = @(\n    @('dualrun', 'scripts\\a.py', 'run'),\n    @('audit', 'scripts\\b.py', ''),\n)\n"
    check("ps1 single-quoted pair legs are counted too", ps1_leg_count(ps1_single) == 2,
          ps1_leg_count(ps1_single))
    check("a ps1 block with no items is zero, not None", ps1_leg_count("$legs = @(\n)\n") == 0)
    check("ps1 without a legs block is not counted",
          ps1_leg_count("$rows = @( @{n='x'} )\n") is None)
    check("ps1 unbalanced block is refused",
          ps1_leg_count("$legs = @( @{n='a'}") is None)

    py = "LEGS = [('a', 1), ('b', 2)]\n"
    check("py reads its own LEGS", py_leg_count(py) == 2)
    check("py without LEGS is not counted", py_leg_count("X = 1\n") is None)
    check("py LEGS imported from elsewhere is not counted",
          py_leg_count("from mod import LEGS\n") is None)

    check("equal denominator names the table", classify(30, 30, False) == G_EQUALS)
    check("below and labelled is honest", classify(30, 7, True) == G_LABELLED)
    check("below and unlabelled reads as the whole chain",
          classify(30, 7, False) == G_SILENT)
    check("above the table is its own class", classify(30, 39, False) == G_ABOVE)
    check("a zero-leg table is not a table", classify(0, 1, False) == G_EMPTY_TABLE)

    rt = round_token(98)
    check("round token matches a zero-padded name", bool(rt.search("_r098bmc_s6_chain.ps1")))
    check("round token rejects a neighbour round", not rt.search("_r0980bmc_s6_chain.py"))
    check("chain script test needs both words",
          is_chain_script("results/_r098bmc_s6_chain.ps1") and not is_chain_script("results/_r098bmc_chain.json"))
    check("machine token matches bm-b and bmb",
          bool(machine_token("b").search("_r1204bmb_s6_chain.py")) and
          bool(machine_token("b").search("bm-b")))

    # the gate itself, on fixtures -- `check` is what re-derives the live face (a build here
    # would reset the arms' own cost model: this suite must stay offline and cheap)
    fx = _fixture_face()
    check("a consistent fixture face passes the gate", not face_problems(fx), face_problems(fx))
    bad = json.loads(json.dumps(fx))
    bad["rows"][0]["class"] = G_SILENT
    check("a hand-written class is refused", bool(face_problems(bad)),
          face_problems(bad)[:2])
    bad2 = json.loads(json.dumps(fx))
    bad2["summary"]["canonical_only_tables"] += 1
    check("an arm count that does not sum is refused", bool(face_problems(bad2)))
    bad3 = json.loads(json.dumps(fx))
    bad3["rows"][0]["witness_path"] = None
    check("a table without a witness path is refused", bool(face_problems(bad3)))
    bad4 = json.loads(json.dumps(fx))
    bad4["population_source"]["population_sha16"] = "0" * 16
    check("a population pin that does not re-derive is refused", bool(face_problems(bad4)))

    failed = [a for a in arms if not a["ok"]]
    print(json.dumps({"arms": len(arms), "failed": len(failed),
                      "results": arms if failed else [a["arm"] for a in arms]},
                     ensure_ascii=False, indent=1))
    return 0 if not failed else 1


def check_fast():
    """Re-read the published witnesses instead of rediscovering them.

    The full ``check`` walks the tree of 727 commits (~165s, one git process each) and is the
    wrong thing to put in a chain that must stay cheap.  This gate asserts the half that can go
    stale on its own: every recorded (commit, path) still yields the table the face publishes,
    and every class still follows from its own numbers.  Discovery is what ``check`` covers.
    """
    try:
        with io.open(LATEST, encoding="utf-8") as fh:
            face = json.load(fh)
    except Exception as exc:
        print(json.dumps({"ok": False, "problems": ["latest face unreadable: %s" % exc]}))
        return 2
    problems = list(face_problems(face))
    rows = [r for r in face.get("rows") or [] if r.get("table") is not None]
    specs = ["%s:%s" % (r["witness_commit"], r["witness_path"]) for r in rows
             if r.get("witness_commit") and r.get("witness_path")]
    text_of = blobs(specs)
    mismatched, unreadable = [], []
    for spec, r in zip(specs, rows):
        if spec not in text_of:
            unreadable.append(spec)
            continue
        got = leg_count(r["witness_path"], text_of[spec])
        if got != r["table"]:
            mismatched.append({"spec": spec, "published": r["table"], "recount": got})
    if mismatched:
        problems.append("%d witnesses no longer yield the published table" % len(mismatched))
    print(json.dumps({"ok": not problems, "problems": problems[:6],
                      "witnesses": len(specs), "tables_matching": len(specs) - len(mismatched)
                      - len(unreadable), "unreadable_from_this_clone": len(unreadable),
                      "verdict": face.get("verdict")}, ensure_ascii=False))
    return 0 if not problems else 1


def check():
    face = build(write=False)
    problems = face.get("problems") or []
    try:
        with io.open(LATEST, encoding="utf-8") as fh:
            published = json.load(fh)
    except Exception as exc:
        print(json.dumps({"ok": False, "problems": ["latest face unreadable: %s" % exc]}))
        return 2
    if published.get("population_source", {}).get("population_sha16") != \
            face["population_source"]["population_sha16"]:
        problems.append("the published population pin differs from the live one (the reports grew "
                        "or were edited); rebuild rather than editing the face")
    if published.get("summary", {}).get("population") != face["summary"]["population"]:
        problems.append("the published population size differs from the live one")
    print(json.dumps({"ok": not problems, "problems": problems,
                      "population": face["summary"]["population"],
                      "judged_from_git": face["summary"]["judged_from_git"],
                      "verdict": face["verdict"]}, ensure_ascii=False))
    return 0 if not problems else 1


def verify():
    face = build(write=False)
    problems = face.get("problems") or []
    s = face["summary"]
    print("verdict:", face["verdict"])
    print(face["verdict_line"])
    print("summary:", json.dumps({k: s[k] for k in sorted(s)}, ensure_ascii=False))
    print("problems:", problems if problems else "[]")
    return 0 if not problems else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        face = build(write=True)
        print(face["verdict_line"])
        print("problems:", face["problems"] if face["problems"] else "[]")
        return 0 if not face["problems"] else 1
    if cmd == "check":
        return check()
    if cmd == "check-fast":
        return check_fast()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    print("usage: e568_old_chain_table.py [build|check|check-fast|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())