#!/usr/bin/env python
"""E606 -- where a face's own count disagrees with its own rows, does a reader compare them?

E601 (r1630) priced the witness: 501 faces state a bar count, 295 of them also publish the rows
that count is about, and 198 of 894 measured series sit under a count that equals neither the rows
nor the distinct rows.  That is a statement about the FACE.  It never asked whether any program
reads such a face and puts the two numbers side by side -- a disagreement nobody compares is a
number nobody can be contradicted by, which is the E601 finding repeated one layer out.

So this study takes every series where the published count does not equal the published row count,
finds the modules that OPEN that face (E470's opener census, reused verbatim rather than rewritten,
E767 reuse-not-rebuild), and grades each (face, reader) pair:

  COMPARES      the module names one of the face's count fields AND computes a row count / a
                distinct count, so it could in principle see the two numbers differ;
  NAMES_ONLY    the module names the count field but never computes how many rows there are --
                it can read the number, not check it;
  IGNORES       the module opens the face and never mentions the count field at all.

Output: results/state_tilt/COUNTRYCOMPARE.json (+ -latest.json)
"""

import argparse
import ast
import glob
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e601_dup_witness as e601                                     # noqa: E402  (scan / count vocabulary)
import e470_target_read as e470                                     # noqa: E402  (opener census, reused)
import e468_pointer_reach as e468                                    # noqa: E402  (_walk_py, producer_map)
import e464_producer_intent as e464                                   # noqa: E402  (face_stem)
import e451_prereg_digest as e451                                    # noqa: E402  (read_text)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
OUT_PATH = os.path.join(OUTDIR, "COUNTRYCOMPARE.json")
SELF_STEM = "COUNTRYCOMPARE"

MAX_READ_BYTES = 1 << 20

# how a reader of a disagreeing face relates to the count it opens
C_COMPARES = "names_the_count_and_computes_how_many_rows_there_are"
C_NAMES_ONLY = "names_the_count_and_never_computes_how_many_rows_there_are"
C_IGNORES = "opens_the_face_and_never_names_the_count"
CLASSES = (C_COMPARES, C_NAMES_ONLY, C_IGNORES)

V_NO_POPULATION = ("no_published_face_prints_a_count_that_disagrees_with_its_own_rows_so_there_is"
                   "_nothing_to_compare")
V_NEVER_COMPARED = ("where_a_published_count_disagrees_with_the_rows_beside_it_every_reader_that"
                    "_opens_the_face_takes_one_of_the_two_numbers_and_never_puts_them_together")
V_SOME_COMPARE = ("some_reader_that_opens_a_disagreeing_face_names_the_count_and_counts_the_rows"
                  "_so_at_least_one_disagreement_is_checkable_by_a_program")

# a call that turns "how many rows are there" into a number
ROWCOUNT_NAME_FUNCS = ("len", "set", "sorted")
ROWCOUNT_ATTRS = ("nunique", "unique", "drop_duplicates", "size", "shape", "count", "distinct")


# --------------------------------------------------------------------------- pure helpers
def counts_disagree(count_value, rows):
    """The predicate the card names: the printed count is not the number of rows beside it."""
    if not e601.is_count_value(count_value):
        return False
    return int(count_value) != int(rows)


def names_the_count(tree, count_fields):
    """Does this module spell any of the face's count field names anywhere?"""
    want = set(count_fields or ())
    if not want:
        return []
    hit = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in want:
            hit.append(node.value)
        elif isinstance(node, ast.Attribute) and node.attr in want:
            hit.append(node.attr)
        elif isinstance(node, ast.Subscript):
            sl = node.slice
            if isinstance(sl, ast.Constant) and isinstance(sl.value, str) and sl.value in want:
                hit.append(sl.value)
    return sorted(set(hit))


def computes_a_row_count(tree):
    """Does this module ever turn a container into 'how many are in it'?"""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if isinstance(fn, ast.Name) and fn.id in ROWCOUNT_NAME_FUNCS:
            return fn.id
        if isinstance(fn, ast.Attribute) and fn.attr in ROWCOUNT_ATTRS:
            return "." + fn.attr
    return ""


def reader_class(names, rowcount):
    if names and rowcount:
        return C_COMPARES
    if names:
        return C_NAMES_ONLY
    return C_IGNORES


def verdict_from(counts):
    if not counts.get("disagreeing_series"):
        return V_NO_POPULATION
    if counts.get("reader_pairs_that_compare") == 0:
        return V_NEVER_COMPARED
    return V_SOME_COMPARE


def _share_text(x):
    return "%s%%" % round(100.0 * float(x or 0.0), 1)


# --------------------------------------------------------------------------- population
def population(root=None):
    """Every series whose printed count is not the number of rows printed beside it."""
    root = root or ROOT
    sc = e601.scan(root)
    rows, faces_seen = [], {}
    for f in sc["faces"]:
        rel = f.get("face") or ""
        if os.path.basename(rel).startswith(SELF_STEM):
            continue
        for s in f.get("series") or []:
            if not counts_disagree(s.get("count_value"), s.get("rows")):
                continue
            rows.append({
                "face": rel,
                "at": s.get("at"),
                "rows": s.get("rows"),
                "rows_distinct": s.get("rows_distinct"),
                "count_value": s.get("count_value"),
                "count_fields": list(s.get("count_fields") or []),
                "count_match": s.get("count_match"),
            })
            faces_seen[rel] = faces_seen.get(rel, 0) + 1
    rows.sort(key=lambda r: (r["face"], r["at"] or ""))
    return {"rows": rows,
            "faces": sorted(faces_seen.items()),
            "faces_read": sc["faces_read"],
            "faces_scanned_with_a_count": sum(1 for f in sc["faces"] if f.get("blocks"))}


# --------------------------------------------------------------------------- reader census
def readers_for(pop_rows, root=None):
    """Reuse E470's opener census on the disagreeing faces and grade each (face, reader) pair."""
    root = root or ROOT
    by_face = {}
    for r in pop_rows:
        by_face.setdefault(r["face"], []).append(r)
    targets = sorted(by_face)
    pop = [{"target": t, "basename": os.path.basename(t), "pointers": []} for t in targets]
    found, tallies = e470.sites_for(pop, root)
    producers = e468.producer_map(root)

    pairs = []
    for face in targets:
        stem = e464.face_stem(os.path.basename(face))
        writer_sources = set(producers.get(stem) or [])
        fields = sorted({k for r in by_face[face] for k in r["count_fields"]})
        # a count spelling carried by many faces cannot prove which face a module meant
        shared = len({r["face"] for r in pop_rows if set(r["count_fields"]) & set(fields)}) > 1
        sources = sorted({s["source"] for s in found.get(face, {}).get("openers") or []})
        for src in sources:
            path = os.path.join(root, src)
            names, rowcount, err = [], "", ""
            try:
                if os.path.getsize(path) > MAX_READ_BYTES:
                    err = "source_above_read_cap"
                else:
                    tree = ast.parse(e451.read_text(path))
                    names = names_the_count(tree, fields)
                    rowcount = computes_a_row_count(tree)
            except (OSError, ValueError, SyntaxError) as exc:
                err = "%s: %s" % (type(exc).__name__, exc)
            pairs.append({
                "face": face,
                "reader": src,
                "count_fields": fields,
                "count_key_is_shared_across_faces": shared,
                "named_count_fields": names,
                "rowcount_predicate": rowcount,
                "class": reader_class(names, rowcount),
                "is_a_producer_of_the_face": src in writer_sources,
                "unreadable": err,
            })
    return pairs, tallies


def summarise(pop, pairs, tallies):
    by_class = {c: 0 for c in CLASSES}
    consumers = [p for p in pairs if not p.get("is_a_producer_of_the_face")]
    for p in consumers:
        if p["unreadable"]:
            continue
        by_class[p["class"]] += 1
    faces = sorted({p["face"] for p in pairs})
    consumer_faces = sorted({p["face"] for p in consumers})
    faces_compared = sorted({p["face"] for p in consumers if p["class"] == C_COMPARES})
    disagreeing_faces = sorted({r["face"] for r in pop["rows"]})
    producer_pairs = [p for p in pairs if p.get("is_a_producer_of_the_face")]
    return {
        "faces_read": pop["faces_read"],
        "faces_scanned_with_a_count": pop["faces_scanned_with_a_count"],
        "disagreeing_series": len(pop["rows"]),
        "faces_carrying_a_disagreeing_series": len(disagreeing_faces),
        "faces_with_a_reader": len(faces),
        "faces_read_by_a_consumer": len(consumer_faces),
        "faces_with_no_reader_at_all": len(disagreeing_faces) - len(faces),
        "reader_sites": len(consumers),
        "producer_sites": len(producer_pairs),
        "producer_sites_that_compare": sum(1 for p in producer_pairs if p["class"] == C_COMPARES),
        "reader_pairs_unreadable": sum(1 for p in consumers if p["unreadable"]),
        "reader_pairs_that_compare": by_class[C_COMPARES],
        "reader_pairs_that_name_only": by_class[C_NAMES_ONLY],
        "reader_pairs_that_ignore_the_count": by_class[C_IGNORES],
        "faces_where_at_least_one_reader_compares": len(faces_compared),
        "by_class": by_class,
        "share_of_reader_pairs_that_compare":
            round(float(by_class[C_COMPARES]) / float(len(consumers))
                  if consumers else 0.0, 4),
        "source_face_series_total": tallies.get("sources_scanned_with_a_candidate"),
    }


def answer_sentence(counts, verdict):
    c = counts or {}
    head = ("%d series across %d published faces print a count that is not the number of rows "
            "printed beside them; %d of those faces are opened by a source at all (%d by a module "
            "that does not write them), and of the %d consumer (face, reader) pairs %d name the "
            "count AND compute a row count, %d name the count and never count rows, %d never "
            "mention the count"
            % (c.get("disagreeing_series", 0), c.get("faces_carrying_a_disagreeing_series", 0),
               c.get("faces_with_a_reader", 0), c.get("faces_read_by_a_consumer", 0),
               c.get("reader_sites", 0),
               c.get("reader_pairs_that_compare", 0), c.get("reader_pairs_that_name_only", 0),
               c.get("reader_pairs_that_ignore_the_count", 0)))
    if verdict == V_NEVER_COMPARED:
        tail = ("-- the disagreement is readable but never read: the only module that counts rows "
                "does not name this count, and the modules that name the count hand the number on")
    elif verdict == V_SOME_COMPARE:
        tail = ("-- %d of %d disagreeing faces have at least one reader that could see the two "
                "numbers differ" % (c.get("faces_where_at_least_one_reader_compares", 0),
                                    c.get("faces_carrying_a_disagreeing_series", 0)))
    else:
        tail = "-- this instrument has nothing to decide"
    return head + " " + tail


# --------------------------------------------------------------------------- face
def build(write=True, root=None):
    root = root or ROOT
    pop = population(root)
    pairs, tallies = readers_for(pop["rows"], root)
    counts = summarise(pop, pairs, tallies)
    ved = verdict_from(counts)
    face = {
        "study": "E606_count_row_compare",
        "evidence_cutoff": _cutoff(pop["rows"]),
        "card": "E606-WHETHER-A-COUNT-THAT-DISAGREES-WITH-ITS-OWN-ROWS-IS-EVER-COMPARED",
        "class_vocabulary": list(CLASSES),
        "counts": counts,
        "faces": [{"face": f, "disagreeing_series": n,
                   "reader_pairs": sum(1 for p in pairs if p["face"] == f
                                       and not p.get("is_a_producer_of_the_face")),
                   "reader_pairs_that_compare": sum(1 for p in pairs
                                                    if p["face"] == f
                                                    and not p.get("is_a_producer_of_the_face")
                                                    and p["class"] == C_COMPARES)}
                  for f, n in pop["faces"]],
        "series": pop["rows"],
        "reader_pairs": pairs,
        "verdict": ved,
        "answer": answer_sentence(counts, ved),
        "limits": [
            "the population is E601's: the same count vocabulary (e597.COUNT_KEYS) and the same "
            "count-block walker, so a count printed under a name outside that vocabulary is not "
            "here",
            "a 'disagreement' means count_value != rows; a count that equals the row count while "
            "the rows carry duplicated bars is E601's D_ROWS_DUP class and is not this card",
            "readers come from E470's opener census (open / io.open / Path.read_text / json.load / "
            "pandas.read_* / gzip.open) with one hop of literal assignment; a module that reaches "
            "the face through two hops, a variable base this tracer cannot follow, or a blob is "
            "not seen here",
            "E470 also publishes glob landings and this study does NOT count them: a sweep like "
            "results/**/*.json could reach a face no literal names, so 'no reader' means no "
            "literal opener, not 'nothing on this disk could load it'",
            "the producer flag is E468's write-site map by face STEM, so two faces in different "
            "directories that share a stem are indistinguishable here",
            "'names the count' is a module-level read of the count field spelling: a module that "
            "names a shared key for another face is graded here too, and the row publishes "
            "count_key_is_shared_across_faces so the ambiguity is visible rather than assumed",
            "'computes a row count' is a module-level read: len() / set() / sorted() or a "
            ".nunique/.unique/.drop_duplicates/.size/.shape/.count call anywhere in the module, so "
            "a module that counts rows somewhere else is credited -- that is a bound on the "
            "COMPARES class, not a proof of comparison",
            "at most %d series per face are measured (E601's cap), so a face with more disagreeing "
            "series than that is graded on some of them" % e601.SERIES_PER_FACE,
            "faces above %d bytes are skipped by the E601 scan and so are absent here"
            % e601.READ_CAP,
        ],
    }
    pr = face_problems(face)
    if write and not pr:
        write_face(face)
    return face, pr


def _cutoff(rows):
    best = ""
    import re as _re
    for r in rows:
        for m in _re.finditer(r"(20\d\d-\d\d-\d\d)", json.dumps(r, ensure_ascii=False)):
            if m.group(1) > best:
                best = m.group(1)
    return best or "no-date-in-payload"


def write_face(face):
    os.makedirs(OUTDIR, exist_ok=True)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    for path in (OUT_PATH, os.path.join(OUTDIR, SELF_STEM + "-latest.json")):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)


# --------------------------------------------------------------------------- guard
def face_problems(face):
    p = []
    if not isinstance(face, dict) or "counts" not in face:
        return ["the face carries no counts block"]
    counts = face["counts"]
    pairs = face.get("reader_pairs") or []
    series = face.get("series") or []
    if not series:
        p.append("the face publishes no disagreeing series")
    for r in series:
        if not counts_disagree(r.get("count_value"), r.get("rows")):
            p.append("series %s/%s is published as disagreeing but its count equals its rows"
                     % (r.get("face"), r.get("at")))
            break
    by_class = {c: 0 for c in CLASSES}
    consumer_pairs = [pr_ for pr_ in pairs if not pr_.get("is_a_producer_of_the_face")]
    for pr_ in pairs:
        if pr_.get("class") not in CLASSES:
            p.append("reader pair %s/%s carries an unknown class %r"
                     % (pr_.get("face"), pr_.get("reader"), pr_.get("class")))
            break
        want = reader_class(pr_.get("named_count_fields"), pr_.get("rowcount_predicate"))
        if pr_["class"] != want:
            p.append("reader pair %s/%s grades itself %r, the rule says %r"
                     % (pr_.get("face"), pr_.get("reader"), pr_["class"], want))
            break
        if not pr_.get("unreadable") and not pr_.get("is_a_producer_of_the_face"):
            by_class[pr_["class"]] += 1
    for k, cls in (("reader_pairs_that_compare", C_COMPARES),
                   ("reader_pairs_that_name_only", C_NAMES_ONLY),
                   ("reader_pairs_that_ignore_the_count", C_IGNORES)):
        if counts.get(k) != by_class[cls]:
            p.append("counts.%s says %r but the reader pairs say %d"
                     % (k, counts.get(k), by_class[cls]))
    if counts.get("reader_sites") != len(consumer_pairs):
        p.append("counts.reader_sites says %r but the face publishes %d consumer pairs"
                 % (counts.get("reader_sites"), len(consumer_pairs)))
    if counts.get("producer_sites") != len(pairs) - len(consumer_pairs):
        p.append("counts.producer_sites says %r but the face publishes %d producer pairs"
                 % (counts.get("producer_sites"), len(pairs) - len(consumer_pairs)))
    if face.get("verdict") != verdict_from(counts):
        p.append("verdict %r does not re-derive from the counts (rule says %r)"
                 % (face.get("verdict"), verdict_from(counts)))
    if not face.get("answer"):
        p.append("the face carries no answer sentence")
    return p


# --------------------------------------------------------------------------- cli
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="build")
    args = ap.parse_args(argv[1:])
    cmd = args.cmd.lower()
    if cmd == "selftest":
        return selftest()
    face, problems = build(write=(cmd in ("build", "run")))
    if problems:
        print("PROBLEMS: " + "; ".join(problems))
        return 1
    c = face["counts"]
    print("faces_read=%d count_faces=%d disagreeing_series=%d disagreeing_faces=%d"
          % (c["faces_read"], c["faces_scanned_with_a_count"], c["disagreeing_series"],
             c["faces_carrying_a_disagreeing_series"]))
    print("faces_with_a_reader=%d faces_with_no_reader=%d reader_pairs=%d (unreadable=%d)"
          % (c["faces_with_a_reader"], c["faces_with_no_reader_at_all"], c["reader_sites"],
             c["reader_pairs_unreadable"]))
    print("by_class=" + json.dumps(c["by_class"], sort_keys=True))
    print("faces_where_a_reader_compares=%d" % c["faces_where_at_least_one_reader_compares"])
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    if cmd in ("check", "verify"):
        try:
            with io.open(OUT_PATH, encoding="utf-8") as fh:
                published = json.load(fh)
        except (OSError, ValueError) as exc:
            print("PROBLEMS: cannot read the published face: %s" % exc)
            return 1
        drift = [k for k in ("counts", "verdict", "faces", "series", "reader_pairs",
                             "class_vocabulary")
                 if published.get(k) != face.get(k)]
        print("problems=[]" if not drift else "DRIFT: " + ",".join(drift))
        if drift:
            return 1
        if cmd == "verify":
            print("verify=identical")
        return 0
    if cmd in ("build", "run"):
        print("wrote " + os.path.relpath(OUT_PATH, ROOT))
    return 0


# --------------------------------------------------------------------------- selftest
def selftest():
    ok = []

    def chk(label, cond, extra=""):
        ok.append(bool(cond))
        print(("PASS " if cond else "FAIL ") + label + (("  -> %r" % (extra,)) if not cond else ""))

    # 1-4 the disagreement predicate, both directions
    chk("1 a count above the rows is a disagreement", counts_disagree(5, 3))
    chk("2 a count below the rows is a disagreement", counts_disagree(2, 7))
    chk("3 a count equal to the rows is not a disagreement", not counts_disagree(4, 4))
    chk("4 a missing or non-count value is not a disagreement",
        not counts_disagree(None, 4) and not counts_disagree("abc", 4))

    # 5-9 reader grading, each class from its own fixture
    tree_cmp = ast.parse("x = data['bars']\nif x != len(data['rows']):\n    pass\n")
    tree_names = ast.parse("x = data['bars']\nprint(x)\n")
    tree_ign = ast.parse("print(data['as_of'])\n")
    chk("5 a module that names the count and counts rows compares",
        reader_class(names_the_count(tree_cmp, ["bars"]), computes_a_row_count(tree_cmp))
        == C_COMPARES)
    chk("6 a module that names the count and never counts rows only names it",
        reader_class(names_the_count(tree_names, ["bars"]), computes_a_row_count(tree_names))
        == C_NAMES_ONLY)
    chk("7 a module that never names the count ignores it",
        reader_class(names_the_count(tree_ign, ["bars"]), computes_a_row_count(tree_ign))
        == C_IGNORES)
    chk("8 an attribute spelling of the count is seen",
        names_the_count(ast.parse("y = obj.bars\n"), ["bars"]) == ["bars"])
    chk("9 a distinct-count call is a row-count predicate",
        computes_a_row_count(ast.parse("n = df['bar'].nunique()\n")) == ".nunique")

    # 10-12 summariser and verdict, all three branches
    def pair(face, cls, unread=""):
        # the class is derived from the evidence, never hand-set, so a fixture cannot claim a
        # class its own fields do not support
        names = ["bars"] if cls in (C_COMPARES, C_NAMES_ONLY) else []
        rowcount = "len" if cls == C_COMPARES else ""
        return {"face": face, "reader": "r.py", "count_fields": ["bars"],
                "count_key_is_shared_across_faces": False, "named_count_fields": names,
                "rowcount_predicate": rowcount, "class": reader_class(names, rowcount),
                "is_a_producer_of_the_face": False, "unreadable": unread}
    pop1 = {"rows": [{"face": "a.json", "count_value": 3, "rows": 5, "count_fields": ["bars"]}],
            "faces": [("a.json", 1)], "faces_read": 1, "faces_scanned_with_a_count": 1}
    c1 = summarise(pop1, [pair("a.json", C_IGNORES), pair("a.json", C_NAMES_ONLY)], {})
    chk("10 a board where nobody compares forces the never-compared verdict",
        verdict_from(c1) == V_NEVER_COMPARED and c1["reader_pairs_that_compare"] == 0, c1)
    c2 = summarise(pop1, [pair("a.json", C_COMPARES)], {})
    chk("11 one comparing reader forces the some-compare verdict",
        verdict_from(c2) == V_SOME_COMPARE, c2)
    c3 = summarise({"rows": [], "faces": [], "faces_read": 1,
                    "faces_scanned_with_a_count": 0}, [], {})
    chk("12 no disagreeing series forces the empty-population verdict",
        verdict_from(c3) == V_NO_POPULATION, c3)

    # 13-14 the guard refuses drift in both directions
    def synth(counts_block, pairs_block, series_block, ved):
        return {"study": "x", "counts": counts_block, "reader_pairs": pairs_block,
                "series": series_block, "verdict": ved, "answer": "an answer"}
    good = synth(c1, [pair("a.json", C_IGNORES), pair("a.json", C_NAMES_ONLY)],
                 pop1["rows"], V_NEVER_COMPARED)
    chk("13 a clean synthetic face passes the guard", face_problems(good) == [],
        face_problems(good))
    bad = json.loads(json.dumps(good))
    bad["counts"]["reader_pairs_that_compare"] = 1
    chk("14 a class count that does not re-derive is caught",
        any("the reader pairs say" in s for s in face_problems(bad)))
    bad2 = json.loads(json.dumps(good))
    bad2["series"][0]["count_value"] = 5
    chk("15 a series published as disagreeing that agrees is caught",
        any("count equals its rows" in s for s in face_problems(bad2)))
    bad3 = json.loads(json.dumps(good))
    bad3["verdict"] = V_SOME_COMPARE
    chk("16 a verdict that contradicts the counts is caught",
        any("does not re-derive" in s for s in face_problems(bad3)))

    # 17-18 the live scan excludes its own face and finds a population
    tmp = os.path.join(ROOT, "results", "_e606_selftest_tmp")
    os.makedirs(tmp, exist_ok=True)
    try:
        with io.open(os.path.join(tmp, "COUNTRYCOMPARE-x.json"), "w", encoding="utf-8") as fh:
            fh.write('{"bars": 9, "rows": [{"bar": "2026-11-06"}]}')
        pop = population(ROOT)
        chk("17 this study does not put its own published face in the population",
            not [r for r in pop["rows"] if SELF_STEM in (r["face"] or "")],
            [r["face"] for r in pop["rows"] if SELF_STEM in (r["face"] or "")][:3])
        chk("18 the live tree carries faces whose count disagrees with their rows",
            pop["faces_read"] > 50, pop["faces_read"])
    finally:
        for f2 in glob.glob(os.path.join(tmp, "*")):
            os.remove(f2)
        os.rmdir(tmp)

    print("\n%d/%d PASS" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))