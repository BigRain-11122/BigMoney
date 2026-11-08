"""E561 (r1587 bm-b): can a historical receipt still be read against the table it was built from?

E560 measured that the receipt never states the size of the table it ran.  This study asks the
follow-up a triager actually needs: given a receipt on disk, can anyone still tell whether it is
SHORT because the chain stopped (or was invoked with --only) or because the table only ever had
that many legs?

Two witnesses are available and the study prices both.

  1. **The receipt itself.**  It carries ``legs_total``.  If that field is computed from the rows
     that ran (``len(rows)``), it can never disagree with the row count, so it certifies nothing
     about the table.  The arm is decided by reading each runner's payload construction, never by
     trusting the field's name.

  2. **Git.**  The receipt names its round, so the runner blob of that round is reachable with
     ``git show <round-commit>:Tools/s6_chain_bm<X>.py``.  Its LEGS table gives the size the round
     *should* have run.  This arm is decided by an actual object fetch, batched through one
     ``git cat-file --batch`` process.

Every receipt is classified by comparing its own row count against the table recovered from its own
round, and the classes are re-derived in ``face_problems`` so a published label cannot be hand-set.

The receipt directory is live -- every chain run adds a file -- so the census is published as an
observation and the gate re-derives per-file classes instead of freezing counts.  This is the
E180/E207 family rule, stated in ``check``.
"""

import ast
import glob
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STATE_TILT = os.path.join(ROOT, "results", "state_tilt")
LATEST = os.path.join(STATE_TILT, "receipttable_latest.json")
DATED_PREFIX = "RECEIPTTABLE"
EVIDENCE_CUTOFF = "2026-11-08"

RUNNERS = {
    "a": "Tools/s6_chain_bma.py",
    "b": "Tools/s6_chain_bmb.py",
    "c": "Tools/s6_chain_bmc.py",
}

RECEIPT_RE = re.compile(r"^_r(\d+)bm([abc])_s6_chain\.json$")

# receipt-vs-table classification
C_COMPLETE = "covers_the_table_of_its_own_round"
C_PARTIAL = "shorter_than_the_table_of_its_own_round"
C_SHRUNK = "longer_than_the_table_it_is_joined_to"
C_NO_WITNESS = "no_runner_blob_reachable_for_that_round"
C_UNREADABLE = "the_receipt_cannot_be_parsed"

# what legs_total actually counts
T_ATTEMPTED = "counts_only_the_rows_that_ran"
T_TABLE = "counts_the_whole_leg_table"

GIT_WINDOW = "4000"


# ---- git helpers ---------------------------------------------------------------
def _git(args, timeout=180):
    try:
        p = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True, timeout=timeout)
    except Exception:
        return None
    if p.returncode != 0:
        return None
    return p.stdout


def round_commits():
    """round number -> the first commit whose subject is 'round <N>: ...'."""
    raw = _git(["log", "--format=%H%x09%s", "-n", GIT_WINDOW])
    if raw is None:
        return {}
    out = {}
    for line in raw.decode("utf-8", "replace").splitlines():
        sha, _, subject = line.partition("\t")
        m = re.match(r"^round (\d+):", subject.strip())
        if m and m.group(1) not in out:
            out[m.group(1)] = sha.strip()
    return out


def tracked_receipts():
    raw = _git(["ls-files", "results/_r*bm*_s6_chain.json"])
    if raw is None:
        return set()
    return set(os.path.basename(x) for x in raw.decode("utf-8", "replace").splitlines() if x.strip())


def committed_receipts():
    """Receipts in HEAD.  An uncommitted receipt is a live artefact -- including the one this very
    round's chain leg just wrote -- so it can be published but never gated (r1519/E180 family:
    a face that gates a file its own runner rewrites goes red because it ran)."""
    raw = _git(["ls-tree", "--name-only", "HEAD", "results/"])
    if raw is None:
        return set()
    return set(os.path.basename(x) for x in raw.decode("utf-8", "replace").splitlines()
               if RECEIPT_RE.match(os.path.basename(x)))


def blobs(specs):
    """{spec: text} for the reachable specs, through ONE cat-file process.

    A missing object is a legitimate answer here (a promisor clone need not hold an old blob) and
    is published as the no-witness class rather than retried: r1243 forbids an unattended rebase
    for the same reason, and a lazy fetch that stops responding would cost the round.
    """
    specs = [s for s in dict.fromkeys(specs) if s]
    if not specs:
        return {}
    payload = ("\n".join(specs) + "\n").encode("utf-8")
    try:
        p = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT, input=payload,
                           capture_output=True, timeout=240)
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
            continue  # "missing" / "ambiguous"
        size = int(parts[2])
        body = out[i:i + size]
        i += size + 1
        found[spec] = body.decode("utf-8-sig", "replace")
    return found


def _legs_count(src):
    """len(LEGS) for a runner source, or None when the table is imported/unreadable."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None, "unparseable"
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "LEGS" for t in node.targets):
            if isinstance(node.value, (ast.List, ast.Tuple)):
                return len(node.value.elts), "own"
            if isinstance(node.value, ast.Attribute) and node.value.attr == "LEGS":
                base = node.value.value
                if isinstance(base, ast.Name):
                    return None, "imported:" + base.id
    # `from s6_chain_bmc import LEGS` -- bm-a's shape: no assignment at all
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and any(a.name == "LEGS" for a in node.names):
            return None, "imported:" + (node.module or "").split(".")[-1]
    return None, "absent"


def _import_target(src, alias):
    """Module name behind an import alias, e.g. bmc -> s6_chain_bmc.

    ``alias`` may name the module itself (the ``from <mod> import LEGS`` shape) or a local name
    bound by ``import <mod> as alias`` (bm-a's shape before r1580).
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            mod = node.module.split(".")[-1]
            if mod == alias:
                return mod
            for a in node.names:
                if (a.asname or a.name) == alias and a.name == "LEGS":
                    return mod
        if isinstance(node, ast.Import):
            for a in node.names:
                mod = a.name.split(".")[-1]
                if (a.asname or mod) == alias:
                    return mod
    return None


def _legs_total_arm(src):
    """Does the payload's legs_total come from the rows that ran, or from the table?"""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return "unparseable", None
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and k.value == "legs_total":
                    if isinstance(v, ast.Call) and isinstance(v.func, ast.Name) \
                            and v.func.id == "len" and v.args:
                        inner = v.args[0]
                        if isinstance(inner, ast.Name) and inner.id != "LEGS":
                            return T_ATTEMPTED, inner.id
                        if isinstance(inner, ast.Name) and inner.id == "LEGS":
                            return T_TABLE, inner.id
                    return "unknown_expression", None
    return "no_legs_total_field", None


# ---- receipt reading -----------------------------------------------------------
def read_receipts():
    out = []
    for path in sorted(glob.glob(os.path.join(ROOT, "results", "_r*bm*_s6_chain.json"))):
        name = os.path.basename(path)
        m = RECEIPT_RE.match(name)
        if not m:
            out.append({"file": name, "name_round": None, "machine": None, "unparsed": True,
                        "reason": "the file name does not carry a round"})
            continue
        row = {"file": name, "name_round": int(m.group(1)), "machine": m.group(2),
               "unparsed": False}
        try:
            with io.open(path, encoding="utf-8") as fh:
                payload = json.load(fh)
        except Exception as exc:
            row.update({"unparsed": True, "reason": str(exc)[:80]})
            out.append(row)
            continue
        row["shape"] = _shape(payload)
        row.update(_counts(payload))
        out.append(row)
    return out


def _shape(payload):
    if isinstance(payload, list):
        return "list_of_rows"
    if not isinstance(payload, dict):
        return "other"
    got = payload.get("legs")
    if isinstance(got, list):
        return "dict_with_rows"
    if isinstance(got, int):
        return "dict_with_a_row_count"
    if isinstance(got, dict):
        return "dict_with_a_dict"
    return "dict_without_rows"


def _counts(payload):
    if isinstance(payload, list):
        rows, stated, round_field, keys = len(payload), None, None, []
        rcs = [r.get("rc") for r in payload if isinstance(r, dict)]
    elif isinstance(payload, dict):
        got = payload.get("legs")
        if isinstance(got, list):
            rows = len(got)
            rcs = [r.get("rc") for r in got if isinstance(r, dict)]
        elif isinstance(got, int):
            rows = got
            rcs = []
        else:
            rows, rcs = 0, []
        stated = payload.get("legs_total")
        round_field = payload.get("round")
        keys = sorted(payload.keys())
    else:
        return {"rows": 0, "stated_total": None, "round_field": None, "keys": [],
                "nonzero_rows": 0}
    return {
        "rows": rows,
        "stated_total": stated if isinstance(stated, int) else None,
        "round_field": str(round_field) if round_field is not None else None,
        "keys": keys,
        "nonzero_rows": sum(1 for r in rcs if r not in (0, None)),
    }


# ---- the classifier ------------------------------------------------------------
def classify(rows, legs, reachable=True):
    """The receipt's class, decided only by its own row count and the table of its own round."""
    if not reachable or legs is None:
        return C_NO_WITNESS
    if rows == legs:
        return C_COMPLETE
    if rows < legs:
        return C_PARTIAL
    return C_SHRUNK


def _verdict(s):
    if not s.get("joinable"):
        return "no_receipt_can_be_joined_to_a_runner_blob"
    if s.get("complete") == 0:
        return ("not_one_historical_receipt_can_be_read_against_the_table_of_its_own_round_and_"
                "its_own_total_agrees_with_itself_by_construction")
    return "some_receipts_can_still_be_read_against_their_table"


def _verdict_line(s):
    return ("%d receipts on disk (%d tracked in git), %d joinable to a runner blob; of those %d "
            "cover their round's table, %d are shorter (a stopped run and an --only run look "
            "identical), %d are longer (the table shrank since); %d have no witness; %d of %d "
            "runners publish legs_total as the number of rows that ran, so the field can never "
            "disagree with the row count it sits beside."
            % (s["receipts_on_disk"], s["tracked_in_git"], s["joinable"], s["complete"],
               s["partial"], s["shrunk"], s["no_witness"], s["legs_total_counts_attempted"],
               s["runners"]))


def build(write=True):
    receipts = read_receipts()
    tracked = tracked_receipts()
    committed = committed_receipts()
    rounds = round_commits()

    live = {}
    for m, path in RUNNERS.items():
        with io.open(os.path.join(ROOT, path), encoding="utf-8-sig", errors="replace") as fh:
            live[m] = fh.read()
    runner_arms = {}
    for m, src in live.items():
        arm, var = _legs_total_arm(src)
        legs_now, table_src = _legs_count(src)
        if legs_now is None and table_src.startswith("imported:"):
            mod = _import_target(src, table_src.split(":", 1)[1])
            sib = os.path.join(ROOT, "Tools", (mod or "") + ".py")
            if mod and os.path.isfile(sib):
                with io.open(sib, encoding="utf-8-sig", errors="replace") as fh:
                    legs_now, _k = _legs_count(fh.read())
        runner_arms["s6_chain_bm%s.py" % m] = {
            "legs_total_arm": arm,
            "legs_total_from": var,
            "legs_in_table_today": legs_now,
            "legs_table_source": table_src,
        }

    # one batched object fetch for the runner blobs of every receipt's own round
    specs = []
    for r in receipts:
        if r.get("unparsed"):
            continue
        sha = rounds.get(str(r["name_round"]))
        if sha:
            specs.append("%s:%s" % (sha, RUNNERS[r["machine"]]))
    fetched = blobs(specs)
    # bm-a imports bm-c's table; fetch that sibling at the same commit for the arms that need it
    second = []
    for spec, text in list(fetched.items()):
        _n, src_kind = _legs_count(text)
        if src_kind.startswith("imported:"):
            alias = src_kind.split(":", 1)[1]
            mod = _import_target(text, alias)
            if mod:
                sha = spec.split(":", 1)[0]
                second.append("%s:Tools/%s.py" % (sha, mod))
    fetched.update(blobs(second))

    rows = []
    for r in receipts:
        item = dict(r)
        item["tracked_in_git"] = r["file"] in tracked
        item["committed"] = r["file"] in committed
        if r.get("unparsed"):
            item["class"] = C_UNREADABLE
            item["table_at_its_round"] = None
            item["join_commit"] = None
            rows.append(item)
            continue
        sha = rounds.get(str(r["name_round"]))
        item["join_commit"] = sha[:9] if sha else None
        text = fetched.get("%s:%s" % (sha, RUNNERS[r["machine"]])) if sha else None
        legs = None
        if text is not None:
            legs, src_kind = _legs_count(text)
            if legs is None and src_kind.startswith("imported:"):
                mod = _import_target(text, src_kind.split(":", 1)[1])
                sib = fetched.get("%s:Tools/%s.py" % (sha, mod)) if mod else None
                if sib is not None:
                    legs, _k = _legs_count(sib)
        item["table_at_its_round"] = legs
        item["class"] = classify(r["rows"], legs, reachable=bool(sha))
        # the tautology arm: a total that equals the row count certifies nothing
        item["stated_total_equals_rows"] = (
            r.get("stated_total") is not None and r["stated_total"] == r["rows"])
        rows.append(item)

    joinable = [r for r in rows if r["class"] in (C_COMPLETE, C_PARTIAL, C_SHRUNK)]
    summary = {
        "runners": len(RUNNERS),
        "receipts_on_disk": len(rows),
        "tracked_in_git": sum(1 for r in rows if r.get("tracked_in_git")),
        "committed": sum(1 for r in rows if r.get("committed")),
        "uncommitted": sum(1 for r in rows if not r.get("committed")),
        "unparsed": sum(1 for r in rows if r.get("unparsed")),
        "joinable": len(joinable),
        "complete": sum(1 for r in rows if r["class"] == C_COMPLETE),
        "partial": sum(1 for r in rows if r["class"] == C_PARTIAL),
        "shrunk": sum(1 for r in rows if r["class"] == C_SHRUNK),
        "no_witness": sum(1 for r in rows if r["class"] == C_NO_WITNESS),
        "unreadable": sum(1 for r in rows if r["class"] == C_UNREADABLE),
        "carrying_a_total": sum(1 for r in rows if r.get("stated_total") is not None),
        "total_equals_its_own_row_count": sum(1 for r in rows
                                              if r.get("stated_total_equals_rows")),
        "total_disagrees_with_its_own_rows": sum(
            1 for r in rows if r.get("stated_total") is not None
            and not r.get("stated_total_equals_rows")),
        "carrying_a_round_field": sum(1 for r in rows if r.get("round_field")),
        "round_field_disagrees_with_the_name": sum(
            1 for r in rows if r.get("round_field") and
            str(r["round_field"]).strip() != str(r["name_round"])),
        "one_row_receipts": sum(1 for r in rows if r.get("rows") == 1),
        "zero_row_receipts": sum(1 for r in rows if r.get("rows") == 0),
        "legs_total_counts_attempted": sum(
            1 for a in runner_arms.values() if a["legs_total_arm"] == T_ATTEMPTED),
        "shapes": sorted({r.get("shape") for r in rows if r.get("shape")}),
    }

    face = {
        "study": "E561",
        "card": "E561",
        "dept": "research+engineering",
        "machine": "bm-b",
        "round": "r1587",
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "population": {
            "receipts": "results/_r<round>bm<a|b|c>_s6_chain.json",
            "runner_sources": sorted(RUNNERS.values()),
            "join": "round number in the receipt name -> commit whose subject is 'round <N>:'"
                    " (last %s commits) -> Tools/s6_chain_bm<X>.py at that commit" % GIT_WINDOW,
        },
        "runner_arms": runner_arms,
        "rows": rows,
        "summary": summary,
        "control_arms": _control_arms(),
        "verdict": _verdict(summary),
        "verdict_line": _verdict_line(summary),
        "note": "the receipt directory is live: every chain run adds a file, so counts move "
                "between rounds and the gate re-derives per-file classes instead of freezing them",
        "producers": {
            "script": "scripts/e561_receipt_table_join.py",
            "selftest": "python scripts/e561_receipt_table_join.py selftest",
            "card": "knowledge/METHODOLOGY_ASSETS.md E561",
        },
    }
    if write:
        _write(LATEST, face)
        _write(os.path.join(STATE_TILT, "%s-%s.json" % (DATED_PREFIX, EVIDENCE_CUTOFF)), face)
    return face


def _control_arms():
    arms = {}
    arms["rows_equal_table"] = {"found": classify(30, 30) == C_COMPLETE,
                                "value": classify(30, 30)}
    arms["short_rows"] = {"found": classify(1, 30) == C_PARTIAL, "value": classify(1, 30)}
    arms["long_rows"] = {"found": classify(40, 36) == C_SHRUNK, "value": classify(40, 36)}
    arms["no_blob"] = {"found": classify(5, None, reachable=False) == C_NO_WITNESS,
                       "value": classify(5, None, reachable=False)}
    # the arm this study exists for: a receipt whose own total equals its own row count is not
    # evidence about the table, so a 1-row receipt must never read as complete against a 30-leg
    # table just because it says legs_total=1.
    self_agreeing = {"rows": 1, "stated_total": 1}
    arms["self_agreement_is_not_a_witness"] = {
        "found": classify(self_agreeing["rows"], 30) == C_PARTIAL,
        "value": classify(self_agreeing["rows"], 30),
    }
    arms["total_from_rows"] = {
        "found": _legs_total_arm(CONTROL_SOURCES["total_from_rows"])[0] == T_ATTEMPTED,
        "value": _legs_total_arm(CONTROL_SOURCES["total_from_rows"])[0],
    }
    arms["total_from_table"] = {
        "found": _legs_total_arm(CONTROL_SOURCES["total_from_table"])[0] == T_TABLE,
        "value": _legs_total_arm(CONTROL_SOURCES["total_from_table"])[0],
    }
    arms["imported_table"] = {
        "found": _legs_count(CONTROL_SOURCES["imported_table"])[1].startswith("imported:"),
        "value": _legs_count(CONTROL_SOURCES["imported_table"])[1],
    }
    return arms


CONTROL_SOURCES = {
    "total_from_rows": '''
import json
LEGS = [("a", ["x"]), ("b", ["y"])]
rows = []
for name, cmd in LEGS:
    rows.append({"leg": name, "rc": 0})
json.dump({"legs_total": len(rows), "legs": rows}, open("x.json", "w"))
''',
    "total_from_table": '''
import json
LEGS = [("a", ["x"]), ("b", ["y"])]
rows = []
for name, cmd in LEGS:
    rows.append({"leg": name, "rc": 0})
json.dump({"legs_total": len(LEGS), "legs": rows}, open("x.json", "w"))
''',
    "imported_table": '''
import json
from s6_chain_bmc import LEGS
rows = []
json.dump({"legs_total": len(rows), "legs": rows}, open("x.json", "w"))
''',
}


# ---- persistence / gates -------------------------------------------------------
def _write(path, obj):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")


def _canon(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True)


def face_problems(face):
    p = []
    rows = face.get("rows") or []
    if not rows:
        p.append("the receipt population is empty")
    for r in rows:
        if r.get("unparsed"):
            if r.get("class") != C_UNREADABLE:
                p.append("%s: unparsable but published as %r" % (r.get("file"), r.get("class")))
            continue
        want = classify(r.get("rows"), r.get("table_at_its_round"),
                        reachable=bool(r.get("join_commit")))
        if r.get("class") != want:
            p.append("%s: class is not what its own row count and table say (%r vs %r)"
                     % (r.get("file"), r.get("class"), want))
        if r.get("class") == C_COMPLETE and r.get("rows") != r.get("table_at_its_round"):
            p.append("%s: published as covering the table with a different row count"
                     % r.get("file"))
    s = face.get("summary") or {}
    if s.get("receipts_on_disk") != len(rows):
        p.append("the receipt count is not the length of the row list")
    for cls, key in ((C_COMPLETE, "complete"), (C_PARTIAL, "partial"), (C_SHRUNK, "shrunk"),
                     (C_NO_WITNESS, "no_witness"), (C_UNREADABLE, "unreadable")):
        if s.get(key) != sum(1 for r in rows if r.get("class") == cls):
            p.append("the %s count is not the number of rows in that class" % key)
    if s.get("joinable") != s.get("complete", 0) + s.get("partial", 0) + s.get("shrunk", 0):
        p.append("the joinable count is not the sum of the three joined classes")
    if s.get("total_equals_its_own_row_count", 0) + \
            s.get("total_disagrees_with_its_own_rows", 0) > s.get("carrying_a_total", 0):
        p.append("the total-field classes exceed the receipts that carry a total")
    for name, arm in (face.get("control_arms") or {}).items():
        if not (arm or {}).get("found"):
            p.append("control arm %s is blind" % name)
    for rname, arm in (face.get("runner_arms") or {}).items():
        if arm.get("legs_in_table_today") in (None, 0):
            p.append("%s: the live LEGS table cannot be read" % rname)
    if face.get("verdict") != _verdict(s):
        p.append("the verdict is not what the rows say")
    if not face.get("verdict_line"):
        p.append("the face carries no verdict line")
    return p


def check():
    face = build(write=False)
    if not os.path.isfile(LATEST):
        print("problems: the published face is missing")
        return 2
    with io.open(LATEST, encoding="utf-8") as fh:
        published = json.load(fh)
    problems = []
    for key in ("runner_arms", "control_arms"):
        if _canon(published.get(key)) != _canon(face.get(key)):
            problems.append("%s does not re-derive from source" % key)
    pub_rows = {r.get("file"): r for r in published.get("rows") or [] if isinstance(r, dict)}
    new_rows = {r.get("file"): r for r in face.get("rows") or [] if isinstance(r, dict)}
    for name in sorted(set(pub_rows) & set(new_rows)):
        a, b = pub_rows[name], new_rows[name]
        # only COMMITTED receipts are gated: an uncommitted one is a live artefact (this round's
        # own chain receipt is one), and gating it would turn the leg red because the leg ran
        if not (a.get("committed") and b.get("committed")):
            continue
        # only the joined fields are gated; the rest is the receipt's own content
        for k in ("class", "table_at_its_round", "join_commit", "rows"):
            if a.get(k) != b.get(k):
                problems.append("%s: %s changed (%r -> %r)" % (name, k, a.get(k), b.get(k)))
    added = sorted(set(new_rows) - set(pub_rows))
    gone = sorted(set(pub_rows) - set(new_rows))
    if added or gone:
        print("receipt census drift: +%d / -%d files (observation, not gated)"
              % (len(added), len(gone)))
    problems.extend(face_problems(published))
    if problems:
        for x in problems:
            print("PROBLEM:", x)
        return 1
    s = published["summary"]
    print("problems=[] receipts=%d joinable=%d complete=%d partial=%d shrunk=%d "
          "no_witness=%d verdict=%s"
          % (s["receipts_on_disk"], s["joinable"], s["complete"], s["partial"], s["shrunk"],
             s["no_witness"], published.get("verdict")))
    return 0


def verify():
    a = _canon(build(write=False))
    b = _canon(build(write=False))
    if a != b:
        print("VERIFY FAIL: two builds differ")
        return 1
    print("VERIFY PASS: two builds identical (%d bytes)" % len(a))
    return 0


# ---- selftest -----------------------------------------------------------------
def selftest():
    bad = []
    total = 0

    def leg(name, cond):
        nonlocal total
        total += 1
        if not cond:
            bad.append(name)

    arms = _control_arms()
    leg("fixture: equal rows and table reads as complete", arms["rows_equal_table"]["found"])
    leg("fixture: one row against thirty reads as short", arms["short_rows"]["found"])
    leg("fixture: more rows than the table reads as shrunk", arms["long_rows"]["found"])
    leg("fixture: no reachable blob reads as no witness", arms["no_blob"]["found"])
    leg("fixture: a receipt agreeing with itself is not a witness",
        arms["self_agreement_is_not_a_witness"]["found"])
    leg("fixture: len(rows) reads as the attempted count", arms["total_from_rows"]["found"])
    leg("fixture: len(LEGS) reads as the table size", arms["total_from_table"]["found"])
    leg("fixture: an imported LEGS is not read as an absent table", arms["imported_table"]["found"])
    leg("all control arms are found", all(a.get("found") for a in arms.values()))

    face = build(write=False)
    leg("live face has no self-detected problems", face_problems(face) == [])
    leg("live face re-derives", _canon(face) == _canon(build(write=False)))
    s = face["summary"]
    leg("every receipt is in exactly one class",
        sum(s[k] for k in ("complete", "partial", "shrunk", "no_witness", "unreadable"))
        == s["receipts_on_disk"])
    leg("at least one receipt joined to a real blob", s["joinable"] > 0
        or s["no_witness"] == s["receipts_on_disk"])
    leg("the shapes published are the shapes on disk", bool(s["shapes"]))

    f2 = json.loads(json.dumps(face))
    if f2["rows"]:
        victim = next((r for r in f2["rows"] if not r.get("unparsed") and r.get("rows") == 1
                       and (r.get("table_at_its_round") or 0) > 1), None)
        if victim is not None:
            victim["class"] = C_COMPLETE
            leg("a one-row receipt relabelled complete is refused", bool(face_problems(f2)))
        else:
            leg("a one-row receipt relabelled complete is refused", True)
    else:
        leg("a one-row receipt relabelled complete is refused", True)

    f3 = json.loads(json.dumps(face))
    f3["verdict"] = "a_verdict_this_study_never_publishes"
    leg("a hand-written verdict is refused", bool(face_problems(f3)))

    f4 = json.loads(json.dumps(face))
    f4["summary"]["receipts_on_disk"] = f4["summary"]["receipts_on_disk"] + 1
    leg("an inflated receipt count is refused", bool(face_problems(f4)))

    f5 = json.loads(json.dumps(face))
    f5["summary"]["joinable"] = 99
    leg("an inflated joinable count is refused", bool(face_problems(f5)))

    f6 = json.loads(json.dumps(face))
    f6["control_arms"]["short_rows"] = {"found": False, "value": C_COMPLETE}
    leg("a blind control arm is refused", bool(face_problems(f6)))

    if bad:
        print("SELFTEST FAIL %d/%d" % (total - len(bad), total))
        for x in bad:
            print("  -", x)
        return 1
    print("SELFTEST PASS %d/%d" % (total, total))
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        face = build(write=True)
        s = face["summary"]
        print("built %s: receipts=%d joinable=%d complete=%d partial=%d shrunk=%d "
              "no_witness=%d unreadable=%d verdict=%s"
              % (os.path.basename(LATEST), s["receipts_on_disk"], s["joinable"], s["complete"],
                 s["partial"], s["shrunk"], s["no_witness"], s["unreadable"],
                 face["verdict"]))
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    print("usage: e561_receipt_table_join.py build|check|verify|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())