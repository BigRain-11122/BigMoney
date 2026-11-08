"""E538 -- where does the parcel that kept moving actually land?

E535 followed E534's six handed-on sites one hop out and found exactly one still moving:
``_resolve_module_chain`` returns ``_resolve_chain_text(...)`` at ``scripts/e398_latest_family.py:410``.
Three sites consume that return (440, 445, 646) and E535 published all three as "hands the value
on again" -- which is a statement about the consumer, not about where the value ends.

This study takes the third hop.  For each of the three consumer sites it reads the consumer's own
body and publishes what happens to the value there:

  D_CYCLE     the consumer returns the value straight back into the resolver family it came from
              (440 and 445 both call ``_resolve_module_chain``), so the "chain" E535 saw moving is
              a call-graph knot -- ``_resolve_module_chain`` -> ``_resolve_chain_text`` ->
              ``_resolve_module_chain`` -- and no value ever leaves it through those two sites;
  D_FIELD     the consumer binds the value, tests it, and places it in a named field of a payload
              it returns (646: ``found = _resolve_module_chain(...)`` then ``dict(evidence,
              family_dir=found, ...)``);
  D_TESTED / D_STOPS / D_DISCARDS / D_UNDEFINED / D_UNRESOLVED are the remaining shapes, published
  as themselves rather than folded into a zero.

The field is then priced against the census face E398 actually writes: how many published read
sites carry a family directory that this arm produced, and what class do they carry it as.  A row
counted as ``family_stated_at_the_site`` whose family came from an imported constant resolved
three functions away is the interesting bill -- the label says the site states the family.

Nothing is rewritten, nothing is executed but this measurement.

Usage:
  python scripts/e538_third_hop.py run
  python scripts/e538_third_hop.py check
  python scripts/e538_third_hop.py verify
  python scripts/e538_third_hop.py selftest
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

CARD = ("E538-WHICH-CONSUMER-THREE-HOPS-OUT-WRITES-A-PAYLOAD-WITH-THE-SENTINEL-THAT-KEPT-MOVING")
STUDY = "E538_third_hop"
DATE_STAMP = "2026-11-08"
FACE_NAME = "parcellanding_latest.json"
DATED_PREFIX = "PARCELLANDING"

UPSTREAM_FACE = "results/state_tilt/nextconsumer_latest.json"
# The census face the classified field ends up in; this is the price, not the population.
PRICE_FACE = "results/state_tilt/latestfamily_latest.json"
PRICE_ARM = "an imported constant names the directory"

S_FORWARDED = "the_next_consumer_hands_the_value_on_again"

D_CYCLE = ("the_consumer_returns_the_value_to_the_resolver_it_came_from_so_the_chain_is_a_call_"
           "graph_knot")
D_FIELD = "the_consumer_places_the_value_in_a_named_field_of_a_payload_it_returns"
D_FIELD_NO_PAYLOAD = "the_consumer_names_a_field_for_the_value_but_returns_no_payload"
D_TESTED = "the_consumer_only_tests_the_value_for_truthiness"
D_STOPS = "the_value_stops_inside_the_consumer"
D_DISCARDS = "the_consumer_discards_the_value"
D_UNDEFINED = "the_receiving_callee_is_not_defined_in_this_corpus"
D_UNRESOLVED = "the_consumer_site_could_not_be_read_statically"
DISPOSITION_VOCAB = (D_CYCLE, D_FIELD, D_FIELD_NO_PAYLOAD, D_TESTED, D_STOPS, D_DISCARDS,
                     D_UNDEFINED, D_UNRESOLVED)
EXIT_DISPOSITIONS = (D_FIELD, D_FIELD_NO_PAYLOAD)

V_ONE_EXIT = ("the_parcel_leaves_the_resolver_at_exactly_one_consumer_and_lands_in_a_named_field_"
              "of_a_written_payload_while_the_other_consumers_are_a_recursive_knot")
V_NO_EXIT = "the_parcel_never_leaves_the_resolver_family"
V_MULTI_EXIT = "the_parcel_leaves_the_resolver_family_at_more_than_one_consumer"
V_EMPTY = "the_upstream_face_carries_no_site_that_is_still_being_forwarded"
VERDICT_VOCAB = (V_ONE_EXIT, V_NO_EXIT, V_MULTI_EXIT, V_EMPTY)


def _now():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _rel(path, root=None):
    root = root or ROOT
    return os.path.relpath(path, root).replace("\\", "/")


def load_upstream(root=None):
    path = os.path.join(root or ROOT, UPSTREAM_FACE)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh), _sha256_file(path)


def population(face):
    """Every consumer site of every E535 row that is still being forwarded."""
    rows = []
    for site in face.get("sites") or []:
        if site.get("disposition") != S_FORWARDED:
            continue
        family = [n for n in (site.get("function"), site.get("next_consumer"),
                              site.get("callee"), site.get("reader_function")) if n]
        seen = []
        for name in family:
            if name not in seen:
                seen.append(name)
        for consumer in site.get("consumer_sites") or []:
            rows.append({
                "reader_function": site.get("reader_function") or site.get("function"),
                "reader_site_line": site.get("site_line"),
                "resolver_family": seen,
                "module": consumer.get("module"),
                "line": consumer.get("line"),
                "caller": consumer.get("caller"),
                "upstream_disposition": consumer.get("disposition"),
            })
    return rows


# --------------------------------------------------------------------------- static reading

def _parse(rel, root=None):
    path = os.path.join(root or ROOT, rel)
    with open(path, encoding="utf-8") as fh:
        return ast.parse(fh.read(), filename=rel)


def _body_of(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    return None


def _stmt_at(fn, line):
    hits = [n for n in ast.walk(fn) if getattr(n, "lineno", None) == line]
    if not hits:
        return None
    order = (ast.Return, ast.Assign, ast.AnnAssign, ast.Expr, ast.If)
    for kind in order:
        for node in hits:
            if isinstance(node, kind):
                return node
    return hits[0]


def _call_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _call_to(node, names):
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call) and _call_name(sub.func) in names:
            return sub
    return None


def _truth_test(fn, name):
    for node in ast.walk(fn):
        if isinstance(node, ast.If) and isinstance(node.test, ast.Name) and node.test.id == name:
            return node.test.lineno
    return None


def _field_for(fn, name):
    """(field, line, returns_it) for a dict(...) keyword or a dict literal key bound to ``name``."""
    for node in ast.walk(fn):
        if isinstance(node, ast.Call) and _call_name(node.func) == "dict":
            for kw in node.keywords:
                if isinstance(kw.value, ast.Name) and kw.value.id == name:
                    return kw.arg, getattr(kw, "lineno", node.lineno), True
        if isinstance(node, ast.Dict):
            for key, val in zip(node.keys, node.values):
                if isinstance(val, ast.Name) and val.id == name:
                    label = key.value if isinstance(key, ast.Constant) else None
                    return label, getattr(val, "lineno", node.lineno), True
    return None, None, False


def _discarded(fn, name):
    """True when the only other uses of the name are bare statement reads or overwrites."""
    uses = 0
    for node in ast.walk(fn):
        if isinstance(node, ast.Name) and node.id == name:
            uses += 1
    return uses == 0


def classify_site(tree, row):
    fn = _body_of(tree, row.get("caller") or "")
    if fn is None:
        return D_UNDEFINED, {}, None
    stmt = _stmt_at(fn, row["line"])
    if stmt is None:
        return D_UNRESOLVED, {}, None
    family = set(row.get("resolver_family") or [])
    detail = {"statement": type(stmt).__name__}

    # a consumer that returns straight into the resolver family is a knot, not a hand-off
    call = _call_to(stmt, family)
    if isinstance(stmt, ast.Return) and call is not None:
        callee = _call_name(call.func)
        detail["returns_into"] = callee
        detail["is_the_reader_itself"] = callee == row.get("reader_function")
        return D_CYCLE, detail, None

    # a consumer that binds the value and then names a field for it
    if isinstance(stmt, (ast.Assign, ast.AnnAssign)) and call is not None:
        target = None
        names = []
        if isinstance(stmt, ast.Assign):
            for t in stmt.targets:
                if isinstance(t, ast.Name):
                    names.append(t.id)
            target = names[0] if names else None
        elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            target = stmt.target.id
        detail["bound_name"] = target
        if target:
            field, field_line, returned = _field_for(fn, target)
            tested = _truth_test(fn, target)
            detail["field"] = field
            detail["field_line"] = field_line
            detail["truth_tested_at"] = tested
            if field:
                return (D_FIELD if returned else D_FIELD_NO_PAYLOAD), detail, field
            if tested:
                return D_TESTED, detail, None
            if _discarded(fn, target):
                return D_DISCARDS, detail, None
            return D_STOPS, detail, None
        return D_UNRESOLVED, detail, None

    if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Name):
        detail["returns_name"] = stmt.value.id
        return D_STOPS, detail, None
    if isinstance(stmt, ast.Expr) and call is not None:
        return D_DISCARDS, detail, None
    return D_UNRESOLVED, detail, None


def module_writes_a_payload(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in ("dump", "dumps") \
                and _call_name(node.func.value) == "json":
            return node.lineno
    return None


def price(price_face):
    """How many published read sites carry a family directory produced by the field arm."""
    rows = price_face.get("read_sites") or []
    carried = []
    for row in rows:
        ev = row.get("evidence") or {}
        if ev.get("how") != PRICE_ARM:
            continue
        carried.append({"site": row.get("site"), "class": row.get("class"),
                        "constant": ev.get("constant"), "family_dir": ev.get("family_dir")})
    classes = sorted({r["class"] for r in carried})
    files = sorted({(r["site"] or "").split(":")[0] for r in carried})
    return {
        "read_sites_total": len(rows),
        "rows_carrying_the_field": len(carried),
        "share_of_read_sites": round(len(carried) / len(rows), 4) if rows else None,
        "classes_those_rows_carry": classes,
        "files": files,
        "rows": carried,
    }


# --------------------------------------------------------------------------- build

def analyse(trees, rows):
    out = []
    for row in rows:
        tree = trees.get(row.get("module") or "")
        if tree is None:
            out.append(dict(row, disposition=D_UNDEFINED, detail={"module_missing": True},
                            field=None, payload_write_line=None))
            continue
        disposition, detail, field = classify_site(tree, row)
        out.append(dict(row, disposition=disposition, detail=detail, field=field,
                        payload_write_line=module_writes_a_payload(tree)
                        if disposition in EXIT_DISPOSITIONS else None))
    return out


def _count(rows, key, vocab):
    counter = {name: 0 for name in vocab}
    for row in rows:
        value = row.get(key)
        if value in counter:
            counter[value] += 1
    return counter


def _verdict(summary):
    if summary["consumer_sites"] == 0:
        return V_EMPTY
    exits = sum(summary["by_disposition"][name] for name in EXIT_DISPOSITIONS)
    if exits == 0:
        return V_NO_EXIT
    if exits > 1:
        return V_MULTI_EXIT
    return V_ONE_EXIT


def build(root=None, write=True, rows=None, upstream_sha=None, price_data=None):
    root = root or ROOT
    if rows is None:
        face, upstream_sha = load_upstream(root)
        rows = population(face)
    modules = sorted({r["module"] for r in rows if r.get("module")})
    trees, failures = {}, []
    for rel in modules:
        try:
            trees[rel] = _parse(rel, root)
        except (OSError, SyntaxError):
            failures.append(rel)
    analysed = analyse(trees, rows)
    if price_data is None:
        with open(os.path.join(root, PRICE_FACE), encoding="utf-8") as fh:
            price_data = price(json.load(fh))
    summary = {
        "upstream_rows": len(rows),
        "consumer_sites": len(analysed),
        "distinct_modules": len(modules),
        "by_disposition": _count(analysed, "disposition", DISPOSITION_VOCAB),
        "knot_consumers": sum(1 for r in analysed if r["disposition"] == D_CYCLE),
        "exits": sum(1 for r in analysed if r["disposition"] in EXIT_DISPOSITIONS),
        "fields_named": sorted({r["field"] for r in analysed if r.get("field")}),
        "payload_write_line": next((r["payload_write_line"] for r in analysed
                                    if r.get("payload_write_line")), None),
        "dispositions_sum_to_the_sites": sum(_count(
            analysed, "disposition", DISPOSITION_VOCAB).values()) == len(analysed),
        "price_rows_carrying_the_field": price_data["rows_carrying_the_field"],
        "price_read_sites_total": price_data["read_sites_total"],
    }
    return {
        "card": CARD,
        "study": STUDY,
        "question": ("where does the value E535 still saw moving land: do the consumers three hops "
                     "out write it into a payload, return it into the resolver they came from, or "
                     "drop it?"),
        "evidence_cutoff": DATE_STAMP,
        "generated": _now(),
        "population_source": ("%s::population() -- every consumer site of an E535 row whose "
                              "disposition is still being forwarded" % os.path.basename(__file__)),
        "upstream_face": UPSTREAM_FACE,
        "upstream_sha256": upstream_sha,
        "price_face": PRICE_FACE,
        "disposition_vocab": list(DISPOSITION_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "summary": summary,
        "verdict": _verdict(summary),
        "price": price_data,
        "sites": analysed,
        "sources_read": modules,
        "parse_failures": failures,
        "method_limits": [
            "one hop further than E535: a consumer that returns the value is classified by the "
            "callee name only; two functions that share a name across modules would be read as "
            "the same knot",
            "a field is named only when it is a dict(...) keyword or a dict-literal key whose "
            "value is the bound name; a field assembled in a separate statement is published as "
            "D_STOPS rather than guessed",
            "the price is read off the census face as it is published on disk; that face is "
            "written by another study at its own cutoff, so the count is a joined reading and is "
            "published with the face name rather than asserted as this study's own measurement",
            "nothing is executed and no source is rewritten",
        ],
    }


def write_face(face, root=None):
    root = root or ROOT
    out_dir = os.path.join(root, "results", "state_tilt")
    os.makedirs(out_dir, exist_ok=True)
    dated = os.path.join(out_dir, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP))
    latest = os.path.join(out_dir, FACE_NAME)
    payload = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    # A published face name is owned by one study.  The first run of this study wrote into
    # E530's ``thirdhop_latest.json`` and clobbered it (the same-name-different-meaning classroom
    # from r1292/r1315); restoring it needed a git checkout.  The guard is cheap: read what is
    # there and refuse if it belongs to someone else.
    for path in (latest, dated):
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as fh:
                    owner = json.load(fh).get("study")
            except (OSError, ValueError):
                owner = None
            if owner != STUDY:
                raise SystemExit("%s is owned by study %r, refusing to write" % (
                    _rel(path, root), owner))
    for path in (dated, latest):
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(payload + "\n")
    return _rel(dated, root), _rel(latest, root)


def load_face(root=None, name=None):
    path = os.path.join(root or ROOT, "results", "state_tilt", name or FACE_NAME)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def face_problems(face, fresh=None):
    problems = []
    if face.get("study") != STUDY:
        problems.append("study is %r" % (face.get("study"),))
    for key in ("card", "question", "evidence_cutoff", "population_source", "summary",
                "verdict", "sites", "method_limits"):
        if key not in face:
            problems.append("missing key %s" % key)
    if problems:
        return problems
    summary = face["summary"]
    sites = face["sites"]
    counts = _count(sites, "disposition", DISPOSITION_VOCAB)
    if counts != summary["by_disposition"]:
        problems.append("by_disposition does not re-derive from the sites")
    if sum(counts.values()) != len(sites):
        problems.append("a site carries a disposition outside the vocabulary")
    if summary["consumer_sites"] != len(sites):
        problems.append("consumer_sites does not equal the site rows")
    if summary["knot_consumers"] != counts[D_CYCLE]:
        problems.append("knot_consumers does not equal the D_CYCLE rows")
    exits = sum(counts[name] for name in EXIT_DISPOSITIONS)
    if summary["exits"] != exits:
        problems.append("exits does not equal the field rows")
    if face["verdict"] != _verdict(summary):
        problems.append("verdict does not re-derive from the summary")
    if face["verdict"] not in VERDICT_VOCAB:
        problems.append("verdict is outside the vocabulary")
    for row in sites:
        if row.get("disposition") not in DISPOSITION_VOCAB:
            problems.append("site %s carries %r" % (row.get("line"), row.get("disposition")))
        elif row.get("disposition") == D_CYCLE and row.get("field"):
            problems.append("a consumer published as a knot also names a field at line %s"
                            % row.get("line"))
        elif row.get("disposition") in EXIT_DISPOSITIONS and not row.get("field"):
            problems.append("a consumer published as an exit names no field at line %s"
                            % row.get("line"))
    if fresh is not None:
        if fresh.get("verdict") != face.get("verdict"):
            problems.append("a rebuild reaches a different verdict")
        if fresh["summary"]["by_disposition"] != summary["by_disposition"]:
            problems.append("a rebuild reaches different dispositions")
        if fresh["summary"]["price_rows_carrying_the_field"] != \
                summary["price_rows_carrying_the_field"]:
            problems.append("a rebuild reaches a different price")
    return problems


def check(root=None, face=None):
    root = root or ROOT
    face = face or load_face(root)
    fresh = build(root, write=False)
    problems = face_problems(face, fresh)
    print(json.dumps({"study": STUDY, "problems": problems[:10],
                      "sites": len(face.get("sites") or []),
                      "verdict": face.get("verdict")}, ensure_ascii=False))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    face = load_face(root)
    fresh = build(root, write=False)
    problems = face_problems(face, fresh)
    same = json.dumps({k: v for k, v in face.items() if k != "generated"},
                      sort_keys=True) == json.dumps(
        {k: v for k, v in fresh.items() if k != "generated"}, sort_keys=True)
    print(json.dumps({"study": STUDY, "problems": problems[:10], "rebuild_identical": same},
                     ensure_ascii=False))
    return 0 if (not problems and same) else 1


# --------------------------------------------------------------------------- fixtures

FIXTURE = '''\
import json


def _resolve_module_chain(site, chain, depth=0):
    if not chain:
        return None
    expr = CONSTS.get(chain[0])
    if expr:
        return _resolve_chain_text(site, expr, chain[1:], depth + 1)
    return None


def _resolve_chain_text(site, text, attrs, depth=0):
    if not attrs:
        return None
    return _resolve_module_chain(site, [text] + list(attrs), depth + 1)


def _attr_static_dir(site, module_name, attr):
    return _resolve_module_chain(site, [module_name, attr])


def classify(node, site):
    found = _resolve_module_chain(site, ["D", "LIVE_DIR"])
    if found:
        evidence = {"expr": node}
        return "static", dict(evidence, family_dir=found, constant="D.LIVE_DIR")
    return "unsupplied", {"expr": node}


def build():
    klass, evidence = classify("D.LIVE_DIR / 'latest.json'", "scripts/x.py")
    rows = [evidence]
    face = {"read_sites": rows}
    with open("face.json", "w") as fh:
        json.dump(face, fh)
    return face


def discard(node, site):
    _resolve_module_chain(site, ["D", "LIVE_DIR"])


def test_only(node, site):
    found = _resolve_module_chain(site, ["D", "LIVE_DIR"])
    if found:
        return "yes"
    return "no"
'''

FIXTURE_PRICE = {
    "read_sites": [
        {"site": "a.py:1", "class": "family_stated_at_the_site",
         "evidence": {"how": "an imported constant names the directory", "constant": "D.LIVE_DIR",
                      "family_dir": "data/live"}},
        {"site": "b.py:2", "class": "family_not_supplied_anywhere",
         "evidence": {"how": "no literal, constant, parameter or prior write"}},
    ]
}


def _fixture_rows():
    family = ["_resolve_module_chain", "_resolve_chain_text"]
    base = {"reader_function": "_resolve_module_chain", "reader_site_line": 6,
            "resolver_family": family, "module": "scripts/x.py",
            "upstream_disposition": S_FORWARDED}
    return [
        dict(base, line=16, caller="_resolve_chain_text"),
        dict(base, line=20, caller="_attr_static_dir"),
        dict(base, line=24, caller="classify"),
        dict(base, line=41, caller="discard"),
        dict(base, line=45, caller="test_only"),
        dict(base, line=99, caller="a_module_that_is_not_here"),
    ]


def selftest():
    fails = []
    tree = ast.parse(FIXTURE)
    trees = {"scripts/x.py": tree}
    rows = analyse(trees, _fixture_rows())
    got = [r["disposition"] for r in rows]
    want = [D_CYCLE, D_CYCLE, D_FIELD, D_DISCARDS, D_TESTED, D_UNDEFINED]
    if got != want:
        fails.append("fixture dispositions %r != %r" % (got, want))
    field_row = rows[2]
    if field_row.get("field") != "family_dir":
        fails.append("named field is %r" % (field_row.get("field"),))
    if field_row.get("payload_write_line") is None:
        fails.append("the fixture module writes a payload and none was found")
    if rows[0]["detail"].get("is_the_reader_itself") is not True:
        fails.append("the knot arm did not recognise the reader itself")

    priced = price(FIXTURE_PRICE)
    if priced["rows_carrying_the_field"] != 1 or priced["read_sites_total"] != 2:
        fails.append("price reads %r" % (priced,))

    summary = {
        "consumer_sites": 3,
        "by_disposition": dict({name: 0 for name in DISPOSITION_VOCAB},
                               **{D_CYCLE: 2, D_FIELD: 1}),
        "price_rows_carrying_the_field": 1,
        "price_read_sites_total": 2,
    }
    if _verdict(summary) != V_ONE_EXIT:
        fails.append("one exit arm reached %r" % (_verdict(summary),))
    summary_cycle = dict(summary, by_disposition=dict({name: 0 for name in DISPOSITION_VOCAB},
                                                      **{D_CYCLE: 3}), exits=0)
    if _verdict(summary_cycle) != V_NO_EXIT:
        fails.append("cycle-only arm reached %r" % (_verdict(summary_cycle),))
    if _verdict({"consumer_sites": 0, "by_disposition": {}}) != V_EMPTY:
        fails.append("empty arm did not reach V_EMPTY")

    # a face whose verdict was written by hand, and one whose counts do not re-derive, must fail
    good = {
        "card": CARD, "study": STUDY, "question": "q", "evidence_cutoff": DATE_STAMP,
        "population_source": "p", "method_limits": [], "sites": rows,
        "summary": {
            "consumer_sites": len(rows),
            "by_disposition": _count(rows, "disposition", DISPOSITION_VOCAB),
            "knot_consumers": sum(1 for r in rows if r["disposition"] == D_CYCLE),
            "exits": sum(1 for r in rows if r["disposition"] in EXIT_DISPOSITIONS),
            "price_rows_carrying_the_field": 1, "price_read_sites_total": 2,
        },
    }
    good["verdict"] = _verdict(good["summary"])
    if face_problems(good):
        fails.append("a clean fixture face was refused: %r" % (face_problems(good),))
    doctored = [("verdict", dict(good, verdict=V_MULTI_EXIT)),
                ("counts", dict(good, summary=dict(good["summary"], exits=3))),
                ("vocabulary", dict(good, sites=[dict(rows[0], disposition="made_up")])),
                ("missing", {k: v for k, v in good.items() if k != "method_limits"})]
    for label, face in doctored:
        if not face_problems(face):
            fails.append("the %s doctored face was accepted" % label)

    print(json.dumps({"study": STUDY, "fails": fails, "arms": len(rows),
                      "doctored_faces_refused": len(doctored)}, ensure_ascii=False))
    return 0 if not fails else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        face = build()
        dated, latest = write_face(face)
        print(json.dumps({"face": dated, "latest": latest, "verdict": face["verdict"],
                          "summary": face["summary"], "price": {
                              k: v for k, v in face["price"].items() if k != "rows"}},
                         ensure_ascii=False))
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    print("usage: e538_third_hop.py [run|check|verify|selftest]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())