"""E384 -- which published keys come from a site that never opens a face?

The keying helpers (E350's ``_face_bindings``, E383's ``_dump_rows``) take face-shaped strings out of
a source.  A string in a source is not a decision to open a file: the same literal can feed a log
line, a caption, a comparison or a ``Path`` that is never read.  Every such literal still enters the
census as a "key", which inflates the population E391/E397 price.

So ask it per key, on the population the census itself publishes:

  * the site list E383 already keeps (``keyed_sites``) is the population -- key -> (source, line, role);
  * each site is classified by the CALL that contains the literal, not by the key's spelling:
    LOAD (``open``/``read_*``/``load``/``read_csv``/...), DUMP (``dump``/``to_*``/``write_*``/
    ``savefig``/...), or OTHER (path construction, print, compare, a bare literal);
  * a key whose every site lands in OTHER is named by something that never opens a file;
  * the consequence is measured, not asserted: each such key is looked up in the published census
    faces and the number of faces that carry it is published beside it.  No face is rewritten and no
    name is renamed -- the bill is the list plus the sentence a reader needs.

Usage:
  python scripts/e384_never_opened_key.py run       # build the face
  python scripts/e384_never_opened_key.py verify    # re-derive every published row from the tree
  python scripts/e384_never_opened_key.py selftest  # offline fixture legs
"""
from __future__ import annotations

import ast
import io
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e350_field_branch_census as e350  # noqa: E402
import e383_shared_key_collision as e383  # noqa: E402

TODAY = "2026-11-03"
FACE = "NEVEROPENED-%s.json" % TODAY
LATEST = "neveropened_latest.json"
PUBLISHED_DIR = os.path.join(ROOT, "results", "state_tilt")
STUDY = "E384_never_opened_key"
SELF_REL = "scripts/e384_never_opened_key.py"
OWN_FILES = (FACE, LATEST)
MAX_ROWS = 300

SITE_LOAD = "load"
SITE_DUMP = "dump"
SITE_OTHER = "other"

# Callee names that mean "this call opens a file and reads it".  ``json.loads`` / ``json.dumps`` are
# deliberately absent: they take strings, not paths, so a literal feeding them is not an open.
LOAD_CALLS = frozenset((
    "read", "readline", "readlines", "read_text", "read_bytes", "read_csv", "read_parquet",
    "read_json", "read_table", "read_excel", "load", "loadtxt", "load_workbook", "isfile", "exists",
))
# ``open`` is mode-dependent: ``open(p)`` / ``open(p, "r")`` reads, ``open(p, "w")`` dumps.
OPEN_CALL = "open"
DUMP_CALLS = frozenset((
    "write", "writelines", "write_text", "write_bytes", "dump", "savetxt", "save", "savefig",
    "to_csv", "to_parquet", "to_json", "to_excel", "touch",
))

CLASS_OPENED = "a_site_that_opens_a_file"
CLASS_CONSTRUCTED = "named_only_by_sites_that_never_open_a_file"
CLASS_NO_SITE = "no_site_in_the_corpus"

V_ALL_OPENED = ("every_published_key_has_at_least_one_site_that_actually_opens_or_dumps_a_file_so_"
                "the_key_population_is_not_inflated_by_bare_literals")
V_SOME_BARE = ("some_published_keys_are_named_only_by_sites_that_never_open_a_file_and_the_published_"
               "face_count_that_carries_each_one_is_printed_beside_it")
V_EMPTY = "no_key_was_sited_so_no_claim_is_made"


def say(message):
    print(message, flush=True)


# --------------------------------------------------------------------------- site classification

def callee_name(node):
    """The last name of a call's callee: ``Path(...).read_text`` -> ``read_text``."""
    func = getattr(node, "func", None)
    if func is None:
        return ""
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return ""


def open_mode(node):
    """``open``'s mode argument, read from the positional args and the keyword if present."""
    mode = "r"
    args = list(getattr(node, "args", []) or [])
    for arg in args[1:2]:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            mode = arg.value
    for kw in (getattr(node, "keywords", []) or []):
        if kw.arg == "mode" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
            mode = kw.value.value
    return mode


def classify_call(name, node=None):
    if name == OPEN_CALL and node is not None:
        return SITE_DUMP if any(ch in open_mode(node) for ch in "wax") else SITE_LOAD
    if name in LOAD_CALLS:
        return SITE_LOAD
    if name in DUMP_CALLS:
        return SITE_DUMP
    return SITE_OTHER


def site_class(tree, line):
    """Classify the literal on ``line`` by its innermost enclosing call that is a load or a dump.

    An outer load wins over an inner path construction: ``json.load(open("x.json"))`` sites the
    literal under both ``open`` (load) and ``json.load`` (other), and the literal does open a file.
    """
    best = SITE_OTHER
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not (getattr(node, "lineno", 0) <= line <= getattr(node, "end_lineno", 0) or False):
            continue
        klass = classify_call(callee_name(node), node)
        if klass == SITE_LOAD:
            return SITE_LOAD
        if klass == SITE_DUMP and best == SITE_OTHER:
            best = SITE_DUMP
    return best


def io_map(sources):
    """(relpath, line) -> site class for every line covered by a call.

    Classified by the call that surrounds the SITE, not by the line the literal sits on: a key is
    usually declared as a module constant and opened elsewhere (``data = json.load(open(FACE))``),
    so the helper's site line is the call's line while the face-shaped literal is up at the
    constant.  Reading the literal's own line would call 90% of a healthy population "never opened".
    """
    out = {}
    parsed = 0
    failed = 0
    for relpath, text in sources:
        try:
            tree = ast.parse(text)
        except SyntaxError:
            failed += 1
            continue
        parsed += 1
        stack = [(tree, SITE_OTHER)]
        while stack:
            node, inherited = stack.pop()
            klass = inherited
            if isinstance(node, ast.Call):
                own = classify_call(callee_name(node), node)
                if own == SITE_LOAD:
                    klass = SITE_LOAD
                elif own == SITE_DUMP and klass == SITE_OTHER:
                    klass = SITE_DUMP
                start = getattr(node, "lineno", 0)
                end = getattr(node, "end_lineno", start) or start
                for line in range(start, end + 1):
                    key = (relpath, line)
                    prev = out.get(key)
                    if prev == SITE_LOAD:
                        continue
                    out[key] = SITE_LOAD if klass == SITE_LOAD else (
                        SITE_DUMP if klass == SITE_DUMP or prev == SITE_DUMP else klass)
            for child in ast.iter_child_nodes(node):
                stack.append((child, klass))
    return out, parsed, failed


# --------------------------------------------------------------------------- population

def population(sources=None):
    """Every key the keying helpers publish, with the sites that named it."""
    if sources is None:
        sources = e350._sources()
    keyed = e383.keyed_sites(sources)
    return {
        "sources": sources,
        "keyed": keyed["keyed"],
        "parsed": keyed.get("parsed"),
        "read_rows": keyed.get("read_rows"),
        "write_rows": keyed.get("write_rows"),
    }


def key_row(key, sites, io):
    """One key's class: does any site that named it actually open or dump a file?"""
    rows = []
    for site in sorted(sites, key=lambda s: (s["source"], s["line"])):
        rel, line, role = site["source"], site["line"], site["role"]
        klass = io.get((rel, line), SITE_OTHER)
        rows.append({"source": rel, "line": line, "role": role, "site": klass})
    loads = sum(1 for r in rows if r["site"] == SITE_LOAD)
    dumps = sum(1 for r in rows if r["site"] == SITE_DUMP)
    others = sum(1 for r in rows if r["site"] == SITE_OTHER)
    if not rows:
        klass = CLASS_NO_SITE
    elif loads or dumps:
        klass = CLASS_OPENED
    else:
        klass = CLASS_CONSTRUCTED
    return {
        "key": key,
        "n_sites": len(rows),
        "n_load": loads,
        "n_dump": dumps,
        "n_other": others,
        "class": klass,
        "sites": rows[:8],
        "sites_truncated": max(0, len(rows) - 8),
    }


def is_own(name):
    """Is this published face one of ours?  A face that lists a bare key counts itself otherwise."""
    return name in OWN_FILES


def published_face_index(keys):
    """Which published census faces name each key -- the consequence, measured not asserted.

    This study's own faces are skipped: a face that lists a bare key in ``never_opened`` would
    otherwise count itself as a carrier (the E180/E207 self-inclusion family).
    """
    index = {k: [] for k in keys}
    faces = 0
    for name, data in e383.published_faces():
        if is_own(name):
            continue
        faces += 1
        text = json.dumps(data, ensure_ascii=False)
        for key in keys:
            if key and key in text:
                index[key].append(name)
    return index, faces


def decide(summary):
    if not summary.get("keys_sited"):
        return V_EMPTY
    if summary.get("keys_named_only_by_sites_that_never_open_a_file"):
        return V_SOME_BARE
    return V_ALL_OPENED


# --------------------------------------------------------------------------- build / verify

def build(write_face=True, sources=None):
    say("keying the corpus")
    pop = population(sources)
    keyed = pop["keyed"]
    say("keys=%d read_rows=%s write_rows=%s" % (len(keyed), pop["read_rows"], pop["write_rows"]))

    say("classifying literal sites")
    io, parsed, failed = io_map(pop["sources"])
    say("call-covered lines=%d parsed=%d skipped=%d" % (len(io), parsed, failed))

    rows = [key_row(k, v["sites"], io) for k, v in sorted(keyed.items())]
    bare = [r for r in rows if r["class"] in (CLASS_CONSTRUCTED, CLASS_NO_SITE)]

    say("checking %d bare keys against the published faces" % len(bare))
    index, faces = published_face_index([r["key"] for r in bare])
    for row in bare:
        carriers = index.get(row["key"], [])
        row["published_faces_carrying_it"] = carriers[:6]
        row["n_published_faces_carrying_it"] = len(carriers)

    by_class = {}
    for row in rows:
        by_class[row["class"]] = by_class.get(row["class"], 0) + 1

    carried = [r for r in bare if r["n_published_faces_carrying_it"]]
    summary = {
        "keys_total": len(rows),
        "keys_sited": sum(1 for r in rows if r["n_sites"]),
        "keys_opened_by_a_load_or_dump": by_class.get(CLASS_OPENED, 0),
        "keys_named_only_by_sites_that_never_open_a_file": by_class.get(CLASS_CONSTRUCTED, 0),
        "keys_with_no_site_in_the_corpus": by_class.get(CLASS_NO_SITE, 0),
        "bare_keys_carried_by_a_published_face": len(carried),
        "published_faces_scanned": faces,
        "by_site": {
            "sites_total": sum(r["n_sites"] for r in rows),
            "load": sum(r["n_load"] for r in rows),
            "dump": sum(r["n_dump"] for r in rows),
            "other": sum(r["n_other"] for r in rows),
        },
        "corpus_parsed": parsed,
        "corpus_skipped": failed,
        "by_class": by_class,
        "classes_sum_to_the_population": sum(by_class.values()) == len(rows),
    }
    summary["verdict"] = decide(summary)
    bare_n = summary["keys_named_only_by_sites_that_never_open_a_file"]
    if not summary["keys_total"]:
        answer = "no key was sited, so no claim is made"
    elif not bare_n:
        answer = ("every published key has a site that opens or dumps a file, so the key census is "
                  "not inflated by bare literals in this tree")
    elif carried:
        answer = ("%d of %d published keys are named only by sites that never open a file, and %d of "
                  "them are carried by at least one published census face (of %d scanned), so a "
                  "reader counting keys there counts names the corpus never opens"
                  % (bare_n, summary["keys_total"], len(carried), faces))
    else:
        answer = ("%d of %d published keys is named only by a site this call table does not "
                  "recognise as an open, and none of them is carried by any of the %d published "
                  "census faces, so no published count moves -- the census is not inflated by bare "
                  "literals here, and the residue is a project-local reader the table cannot see"
                  % (bare_n, summary["keys_total"], faces))
    face = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": SELF_REL,
        "summary": summary,
        "verdict": summary["verdict"],
        "answer": answer,
        "never_opened": [
            {"key": r["key"], "n_sites": r["n_sites"], "sites": r["sites"],
             "n_published_faces_carrying_it": r["n_published_faces_carrying_it"],
             "published_faces_carrying_it": r["published_faces_carrying_it"]}
            for r in sorted(carried, key=lambda x: (-x["n_published_faces_carrying_it"], x["key"]))
        ][:MAX_ROWS],
        "never_opened_uncarried": [
            {"key": r["key"], "n_sites": r["n_sites"], "sites": r["sites"]}
            for r in bare if not r["n_published_faces_carrying_it"]
        ][:MAX_ROWS],
        "bounds": {
            "measured": ("each key's sites classified by the innermost enclosing call family; the "
                         "carrier count is a substring test on each published census face's JSON"),
            "not_measured": ("whether a reader of a carrier face treats the key as a population "
                             "member (E383's consumer table); literals inside f-strings are not "
                             "Constant nodes here"),
            "no_rewrites": "no published face is edited and no key is renamed",
        },
    }
    say("verdict: %s" % summary["verdict"])
    say(face["answer"])
    if write_face:
        _write(face)
    return face


def _write(face):
    os.makedirs(PUBLISHED_DIR, exist_ok=True)
    for name in (FACE, LATEST):
        path = os.path.join(PUBLISHED_DIR, name)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    say("wrote %s and %s" % (FACE, LATEST))


def verify():
    problems = []
    path = os.path.join(PUBLISHED_DIR, FACE)
    if not os.path.exists(path):
        say("verify problems=['face is absent']")
        return ["face is absent"]
    with io.open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    summary = face["summary"]
    if face.get("evidence_cutoff") != TODAY:
        problems.append("evidence_cutoff moved")
    by_class = summary.get("by_class") or {}
    if sum(by_class.values()) != summary.get("keys_total"):
        problems.append("classes sum to %d but the population is %d"
                        % (sum(by_class.values()), summary.get("keys_total")))
    if (summary.get("keys_named_only_by_sites_that_never_open_a_file")
            + summary.get("keys_with_no_site_in_the_corpus")
            + summary.get("keys_opened_by_a_load_or_dump")) != summary.get("keys_total"):
        problems.append("the three site classes do not sum to the published population")
    if decide(summary) != face.get("verdict"):
        problems.append("the decision gate does not re-derive the published verdict")
    for row in (face.get("never_opened") or []) + (face.get("never_opened_uncarried") or []):
        if not row["sites"]:
            continue
        for site in row["sites"]:
            if site["site"] != SITE_OTHER:
                problems.append("%s/%s: site %s is %s, not other"
                                % (row["key"], site["source"], site["line"], site["site"]))
    say("verify problems=%s" % (problems or "[]"))
    return problems


# --------------------------------------------------------------------------- selftest

FIXT_LOAD = '''
import json
def read_it():
    with open("results/trial_labor_w1/judge_state.json", "r") as fh:
        return json.load(fh)
'''

FIXT_DUMP = '''
import json
def write_it(face):
    with open("results/trial_labor_w1/verdict_face.json", "w") as fh:
        json.dump(face, fh)
'''

FIXT_BARE = '''
CAPTION = "results/trial_labor_w1/judge_state.json"
def show():
    print("writing results/trial_labor_w1/verdict_face.json now")
'''

FIXT_CONST = '''
import json
FACE = "results/trial_labor_w1/verdict_face.json"
def read_it():
    with open(FACE, "r") as fh:
        return json.load(fh)
'''


def selftest():
    legs = []

    def leg(name, ok, note=""):
        legs.append((name, bool(ok), note))

    # 1. the callee name is read off the call, not off the key
    tree = ast.parse(FIXT_LOAD)
    leg("load_call_is_named", site_class(tree, 4) == SITE_LOAD)
    tree = ast.parse(FIXT_DUMP)
    leg("dump_call_is_named", site_class(tree, 4) == SITE_DUMP)
    tree = ast.parse(FIXT_BARE)
    leg("a_bare_caption_is_other", site_class(tree, 2) == SITE_OTHER)
    leg("a_print_mention_is_other", site_class(tree, 4) == SITE_OTHER)

    # 2. json.loads/dumps are not file opens (they take strings)
    leg("loads_is_not_an_open", classify_call("loads") == SITE_OTHER)
    leg("dumps_is_not_an_open", classify_call("dumps") == SITE_OTHER)
    leg("json_load_is_an_open", classify_call("load") == SITE_LOAD)
    # ``open`` is mode-dependent -- a write-mode open sites a dump, not a load
    dump_open = [n for n in ast.walk(ast.parse(FIXT_DUMP)) if isinstance(n, ast.Call)
                 and callee_name(n) == OPEN_CALL][0]
    load_open = [n for n in ast.walk(ast.parse(FIXT_LOAD)) if isinstance(n, ast.Call)
                 and callee_name(n) == OPEN_CALL][0]
    leg("write_mode_open_is_a_dump",
        classify_call(OPEN_CALL, dump_open) == SITE_DUMP, open_mode(dump_open))
    leg("read_mode_open_is_a_load", classify_call(OPEN_CALL, load_open) == SITE_LOAD,
        open_mode(load_open))

    # 3. the io map covers exactly the face-shaped literals in the corpus
    io, parsed, failed = io_map([("fixtures/a.py", FIXT_LOAD), ("fixtures/b.py", FIXT_BARE)])
    leg("io_map_parses_every_source", parsed == 2 and failed == 0)
    leg("io_map_sees_the_load", io.get(("fixtures/a.py", 4)) == SITE_LOAD,
        str(io))
    leg("io_map_sees_the_caption", io.get(("fixtures/b.py", 2), SITE_OTHER) == SITE_OTHER)
    # a constant declared on its own line and opened later must resolve by the CALL's line, not by
    # the constant's -- the first burn read 793 of 883 keys as "never opened" on exactly this bug
    fidx, _fp, _ff = io_map([("fixtures/c.py", FIXT_CONST)])
    open_line = [n.lineno for n in ast.walk(ast.parse(FIXT_CONST))
                 if isinstance(n, ast.Call) and callee_name(n) == OPEN_CALL][0]
    const_line = [n.lineno for n in ast.walk(ast.parse(FIXT_CONST))
                  if isinstance(n, ast.Assign)][0]
    leg("a_constant_opened_later_sites_the_call", fidx.get(("fixtures/c.py", open_line)) == SITE_LOAD,
        str(sorted(fidx)))
    leg("a_constant_declaration_is_not_a_site",
        fidx.get(("fixtures/c.py", const_line), SITE_OTHER) == SITE_OTHER)

    # 4. one key's class is a function of its sites
    sites = [{"source": "fixtures/a.py", "line": 4, "role": e383.ROLE_READ, "value": "k.json"}]
    row = key_row("k.json", sites, io)
    leg("a_load_site_opens_the_key", row["class"] == CLASS_OPENED and row["n_load"] == 1)
    row = key_row("k.json", [{"source": "fixtures/b.py", "line": 2,
                              "role": e383.ROLE_READ, "value": "k.json"}], io)
    leg("an_all_other_key_is_bare", row["class"] == CLASS_CONSTRUCTED and row["n_load"] == 0)
    row = key_row("k.json", [{"source": "fixtures/nowhere.py", "line": 9,
                              "role": e383.ROLE_WRITE, "value": "k.json"}], io)
    leg("an_unknown_site_is_other_not_opened", row["class"] == CLASS_CONSTRUCTED)
    row = key_row("k.json", [], io)
    leg("no_site_is_its_own_class", row["class"] == CLASS_NO_SITE)

    # 5. a mixed key opens: the load side wins over a caption on the same name
    mixed = [{"source": "fixtures/a.py", "line": 4, "role": e383.ROLE_READ, "value": "k.json"},
             {"source": "fixtures/b.py", "line": 2, "role": e383.ROLE_READ, "value": "k.json"}]
    row = key_row("k.json", mixed, io)
    leg("a_mixed_key_counts_as_opened", row["class"] == CLASS_OPENED
        and row["n_load"] == 1 and row["n_other"] == 1)

    # 6. the decision gate is a function of the summary
    leg("decide_all_opened", decide({"keys_sited": 10}) == V_ALL_OPENED)
    leg("decide_some_bare", decide({"keys_sited": 10,
                                    "keys_named_only_by_sites_that_never_open_a_file": 2}) == V_SOME_BARE)
    leg("decide_empty", decide({}) == V_EMPTY)

    # 7. own files are named so the published-face scan cannot read its own output back in
    leg("own_files_named", FACE in OWN_FILES and LATEST in OWN_FILES)
    leg("own_faces_are_skipped_as_carriers", is_own(FACE) and is_own(LATEST)
        and not is_own("WALKAMBIG-2026-11-03.json"))

    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, note in legs:
        say("  %-44s %s%s" % (name, "PASS" if ok else "FAIL", ("  " + note) if note and not ok else ""))
    say("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        face = build()
        s = face["summary"]
        say("of %d keys: %d opened by a load or dump, %d named only by non-opening sites, %d with no "
            "site; %d of the bare ones are carried by a published face"
            % (s["keys_total"], s["keys_opened_by_a_load_or_dump"],
               s["keys_named_only_by_sites_that_never_open_a_file"],
               s["keys_with_no_site_in_the_corpus"],
               s["bare_keys_carried_by_a_published_face"]))
        return 0
    if cmd == "verify":
        return 0 if not verify() else 1
    if cmd == "selftest":
        return selftest()
    say("usage: e384_never_opened_key.py [run|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))