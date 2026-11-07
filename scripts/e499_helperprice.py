"""E499 -- price the read sites the class delta did not show.

E498 (r1524) re-measured E479's 36 frozen twins with E497's helper arm: 1 twin gained a reader
(class delta 1), but 11 twins that a literal census already called read gained 24 read sites it
could not see.  A site count is not a price.  E483 priced the leg sites by asking what the
asserting block does with the payload -- re-derive a number, pin a field to a constant, only
require the field to be present, or only require the file to exist -- and that three-way split is
exactly what a retirement rule needs: a producer must keep a face alive for a block that
re-derives or pins, and does not have to for a block that only opens it.

This study prices the sites E498 published, and the ones it counted without publishing (the same
read population, split by tier), then recomputes the twins' retirement status twice: once with
every read site counting as a reader (E479's rule) and once with only re-deriving and pinning
sites counting (this study's strict arm).  The delta between those two answers is the price of
the blindness E498 measured.

Two arms beyond E483 are needed, and both are published as their own classes rather than folded
into an existing one:

  * a helper site's payload never appears as a ``load`` call at the site itself -- it appears as
    ``x = _read_json(p)``.  e483.payload_roots() therefore finds no root and returns
    ``reads_the_file_and_reads_no_field_in_this_block`` for every helper site, which would read
    as "nothing consumes it" when in fact the block consumes ``x.get('field')``.  The fix is a
    root extension: if the helper's own definition returns a parsed payload, the name it is
    bound to at the site is a payload root.  The extension is pinned to the shared classifier by
    a selftest leg that proves, on a unit where the extra names are already roots, that this
    module's classify and e483.classify_block() agree exactly.
  * a block that raises when a field is missing is a consumer (the round breaks), but it is
    neither a re-derivation nor a pin.  Published as its own class and counted in a sensitivity
    arm, never merged into the strict arm, because the card names the two it names.

Run:      python scripts/e499_helperprice.py run
Check:    python scripts/e499_helperprice.py check     (tallies re-derive from the face)
Verify:   python scripts/e499_helperprice.py verify    (re-derives from the live tree)
Selftest: python scripts/e499_helperprice.py selftest
"""
import argparse
import ast
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (ROOT, os.path.join(ROOT, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import e483_leg_debt as e483  # noqa: E402
import e497_twindead as e497  # noqa: E402
import e498_helperread as e498  # noqa: E402
import e494_latest_authors as e494  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "helperprice_latest.json"
DATED_PREFIX = "HELPERPRICE"
DATE_STAMP = "2026-11-07"
CARD = "E499-PRICE-THE-READ-SITES-THE-CLASS-DELTA-DID-NOT-SHOW"

PARENT_FACE = "helperread_latest.json"          # E498
RESIDUE_FACE = "twinread_latest.json"           # E479 (members / bytes / retirement split)

D_RAISES = "raises_a_fault_when_the_payload_lacks_a_field"
D_REPUBLISH = "reads_payload_fields_and_asserts_nothing_here"
PRICE_VOCAB = tuple(e483.DEBT_VOCAB) + (D_RAISES, D_REPUBLISH)

# the card's strict rule: only these two classes are what a producer must keep a face alive for
COUNTS_AS_A_READER = (e483.D_REDERIVE, e483.D_PIN)
# published sensitivity arms, never merged into the strict count
COUNTS_WITH_FAULTING = COUNTS_AS_A_READER + (D_RAISES,)
COUNTS_WITH_REPUBLISHING = COUNTS_AS_A_READER + (D_RAISES, D_REPUBLISH, e483.D_PRESENCE)

V_MOVES = "counting_only_rederiving_and_pinning_sites_as_readers_moves_twins_to_retirable"
V_NONE = "no_twin_changes_retirement_status_when_only_rederiving_and_pinning_sites_count"
V_EMPTY = "no_read_site_in_the_population_could_be_priced"
VERDICT_VOCAB = (V_MOVES, V_NONE, V_EMPTY)

PAYLOAD_READS = tuple(e483.NEW_NAMES) + tuple(e483.TEXT_READS)


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime())


def _load_json(path):
    return json.load(io.open(path, "r", encoding="utf-8"))


# ------------------------------------------------------------------------------- helpers
def helper_info(tree, name):
    """What the module's own definition of ``name`` returns.

    returns_payload   the function hands back a value it parsed (load/loads) -- so the name it is
                      bound to at a call site carries payload fields
    returns_text      it hands back the file's text/bytes (or a digest of them) -- no field is
                      reachable, so a block that compares two of these compares copies
    """
    info = {"found": False, "line": 0, "returns_payload": False, "returns_text": False}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name != name:
            continue
        info["found"] = True
        info["line"] = getattr(node, "lineno", 0)
        parsed = set()
        texts = set()
        for sub in ast.walk(node):
            if isinstance(sub, ast.Assign) and len(sub.targets) == 1 and \
                    isinstance(sub.targets[0], ast.Name):
                for call in ast.walk(sub.value):
                    if not isinstance(call, ast.Call):
                        continue
                    tail = e494._func_tail(call.func)
                    if tail in e483.NEW_NAMES:
                        parsed.add(sub.targets[0].id)
                    elif tail in e483.TEXT_READS:
                        texts.add(sub.targets[0].id)
        for sub in ast.walk(node):
            if not isinstance(sub, ast.Return) or sub.value is None:
                continue
            for call in ast.walk(sub.value):
                tail = e494._func_tail(call.func) if isinstance(call, ast.Call) else ""
                if tail in e483.NEW_NAMES:
                    info["returns_payload"] = True
                elif tail in e483.TEXT_READS:
                    info["returns_text"] = True
                elif isinstance(call, ast.Call) and e494._func_tail(call.func) in texts:
                    info["returns_text"] = True
            for nm in ast.walk(sub.value):
                if isinstance(nm, ast.Name) and nm.id in parsed:
                    info["returns_payload"] = True
                if isinstance(nm, ast.Name) and nm.id in texts:
                    info["returns_text"] = True
        break
    return info


def call_tails(unit):
    tails = {}
    for node in ast.walk(unit):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            tails[node.func.id] = tails.get(node.func.id, 0) + 1
    return tails


def roots_from_a_parsing_helper(unit, tree):
    """Names bound to a call of a helper whose own body parses the file it is given."""
    names = {}
    for node in ast.walk(unit):
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1 and
                isinstance(node.targets[0], ast.Name)):
            continue
        call = node.value
        if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name):
            continue
        info = helper_info(tree, call.func.id)
        if info["found"] and info["returns_payload"]:
            names[node.targets[0].id] = {"helper": call.func.id,
                                         "helper_line": info["line"]}
    return names


def classify_roots(unit, info, roots):
    """e483.classify_block() with the payload roots supplied from outside.

    The body below is the shared classifier's, driven by a root set this module may have widened;
    the selftest pins the equivalence on a unit whose roots need no widening.
    """
    bound = e483.derive_bindings(unit, roots)
    built = e483.building_names(unit, info)
    value = presence = rederive = bytes_only = externally = computed = 0
    for node in ast.walk(unit):
        tests = []
        if isinstance(node, ast.Compare):
            tests = [node]
        elif isinstance(node, ast.If):
            tests = [node.test]
        for test in tests:
            if isinstance(test, ast.Compare):
                sides = [test.left] + list(test.comparators)
                pure = [x for x in sides
                        if e483.is_pure_read_side(x, roots, bound, built, info)]
                builders = [x for x in sides if e483.is_builder_side(x, built, info)]
                if any(e483.computes_from_the_payload(x, roots, bound) for x in sides):
                    computed += 1
                if not pure and not builders:
                    continue
                if builders:
                    rederive += 1
                elif len(pure) > 1:
                    bytes_only += 1
                elif all(e483.is_literal_side(x) for x in sides
                         if not any(x is p for p in pure)):
                    value += 1
                else:
                    externally += 1
            elif e483.payload_ish(test, roots, bound):
                presence += 1
    counts = {"roots": sorted(roots), "value": value, "presence": presence,
              "rederive": rederive, "bytes_only": bytes_only,
              "externally_derived": externally,
              "comparisons_that_count_the_payload": computed}
    if rederive:
        return e483.D_REDERIVE, counts
    if value or externally:
        return e483.D_PIN, counts
    if bytes_only:
        return e483.D_BYTES, counts
    if presence:
        return e483.D_PRESENCE, counts
    return e483.D_EXISTS, counts


def compares_two_copies(unit, tree):
    """A block that compares two calls to the same non-parsing helper (a digest, a text read).

    Only claimed when the helper reaches the file's bytes and reads no field -- otherwise the
    comparison could be of two payload facts and belongs to the shared classifier.
    """
    for node in ast.walk(unit):
        if not isinstance(node, ast.Compare):
            continue
        sides = [node.left] + list(node.comparators)
        calls = [s for s in sides if isinstance(s, ast.Call) and isinstance(s.func, ast.Name)]
        if len(sides) < 2 or not calls:
            continue
        names = {c.func.id for c in calls}
        for nm in names:
            info = helper_info(tree, nm)
            if info["found"] and info["returns_text"] and not info["returns_payload"]:
                return {"helper": nm, "helper_line": info["line"]}
    return None


def raises_on_the_payload(unit, roots):
    """An If whose test touches the payload and whose body raises: the round breaks if it is gone."""
    bound = e483.derive_bindings(unit, roots)
    for node in ast.walk(unit):
        if not isinstance(node, ast.If) or not e483.payload_ish(node.test, roots, bound):
            continue
        for sub in ast.walk(ast.Module(body=node.body, type_ignores=[])):
            if isinstance(sub, ast.Raise):
                return True
    return False


def block_at_line(tree, par, line):
    """The asserting block for a line that is not itself an opener call.

    e483.asserting_block() climbs from the open call, which is right for a literal read site and
    useless for a helper site: the line is ``x = _read_json(p)``, no opener is near it, and the
    block that owns the price would be the whole module.  A module scope is not an assertion
    scope -- every assert in the file would answer for one site -- so the chain is built from the
    line itself and the shared two rules are applied to it.
    """
    chain = []
    for node in ast.walk(tree):
        end = getattr(node, "end_lineno", None)
        start = getattr(node, "lineno", None)
        if start is None or end is None:
            continue
        if start <= line <= end:
            chain.append(node)
    chain.sort(key=lambda n: (n.lineno, -(n.end_lineno or 0)))
    for node in reversed(chain):
        if isinstance(node, e483.BLOCK_TYPES) and node is not tree and \
                e483.has_assertion(node):
            return node
    for node in reversed(chain):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return node
    return tree


def fields_read_in(unit, roots):
    """How many payload fields this block reads at all (``x.get(...)``, ``x["k"]``).

    e483's classifier only looks at Compare/If, so a block that publishes the payload's fields
    into another face reads fields and asserts nothing -- which its own vocabulary would have to
    call "reads the file and reads no field", a claim that is false about the code.
    """
    if not roots:
        return 0
    bound = e483.derive_bindings(unit, roots)
    n = 0
    for node in ast.walk(unit):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and \
                node.func.attr in e483.PAYLOAD_METHODS and \
                e483.payload_ish(node.func.value, roots, bound, 1):
            n += 1
        elif isinstance(node, ast.Subscript) and \
                e483.payload_ish(node.value, roots, bound, 1):
            n += 1
    return n


def price_site(source, line):
    """One read site's price: what its block does with the payload it opened."""
    got = e483.source_tree(source)
    base = {"source": source, "line": line, "role": e483.role_of(source)}
    if got is None or "error" in got:
        return dict(base, price=e483.D_UNREADABLE, block=None, payload_roots=[],
                    roots_from_helpers={}, evidence="the source is absent or does not parse")
    tree, par = got["tree"], got["par"]
    if e483.open_call_near(tree, line) is not None:
        unit = e483.asserting_block(tree, par, line)
        resolution = "from_the_opener_call_on_this_line"
    else:
        unit = block_at_line(tree, par, line)
        resolution = "from_the_line_itself"
    roots0 = e483.payload_roots(unit)
    extra = roots_from_a_parsing_helper(unit, tree)
    roots = set(roots0) | set(n for n in extra if n not in roots0)
    if roots == roots0:
        price, counts = e483.classify_block(unit, got.get("info"))
    else:
        price, counts = classify_roots(unit, got.get("info"), roots)
    evidence = {"roots": sorted(roots0), "roots_from_helpers": extra,
                "counts": counts}
    touched = fields_read_in(unit, roots)
    evidence["fields_read"] = touched
    if price in (e483.D_EXISTS, e483.D_NO_FIELD):
        copies = compares_two_copies(unit, tree)
        if copies:
            price = e483.D_BYTES
            evidence["bytes_evidence"] = copies
        elif raises_on_the_payload(unit, roots):
            price = D_RAISES
            evidence["raises_evidence"] = "an If on a payload field raises"
        elif touched:
            price = D_REPUBLISH
            evidence["republish_evidence"] = ("%d payload field access(es) and no assertion in "
                                              "this block" % touched)
    return dict(base, price=price,
                block={"kind": type(unit).__name__,
                       "start": getattr(unit, "lineno", 0),
                       "end": getattr(unit, "end_lineno", 0),
                       "resolution": resolution},
                payload_roots=sorted(roots),
                roots_from_helpers=extra, evidence=evidence)


# ------------------------------------------------------------------------------- measure
def measure(root=None):
    root = root or ROOT
    parent = _load_json(os.path.join(root, "results", "state_tilt", PARENT_FACE))
    members, keep, toks = e498.apply_arm(root)
    # a scanner must not count its own sources (E180/E207 family): e498.apply_arm() excludes
    # e498's files because they are ITS population's readers, and this module's own scripts and its
    # standalone leg runner would otherwise enter the tree and move the source count under the face
    # it just published (E455: a census over a growing tree re-reds one round after republish).
    e497.SELF_PREFIX = tuple(e497.SELF_PREFIX) + ("e499_", "run_e499", "_e499")
    try:
        sites, meta = e497.scan(members, root=root)
    finally:
        e498.restore(keep)
    baseline = {r.get("twin"): r for r in (parent.get("rows") or [])}
    rows = []
    for m in members:
        twin = m["member"]
        got = sites.get(twin) or []
        reads = [s for s in got if s.get("mode") == e483.M_READ]
        priced = []
        for s in reads:
            row = price_site(s.get("source"), s.get("line"))
            row["tier"] = s.get("tier")
            row["helper"] = s.get("helper")
            row["literal"] = s.get("literal")
            row["mode_evidence"] = s.get("mode_evidence")
            priced.append(row)
        b = baseline.get(twin) or {}
        rows.append({
            "twin": twin,
            "family_dir": m["family_dir"],
            "members": m["members"],
            "bytes_on_disk": m["bytes_on_disk"],
            "baseline_read_sites": b.get("baseline_read_sites") or 0,
            "parent_read_sites": b.get("read_sites") or 0,
            "parent_helper_read_sites": b.get("helper_read_sites") or 0,
            "priced_read_sites": len(priced),
            "sites": priced,
        })
    return rows, meta, toks, parent


def _classes(sites):
    out = {}
    for s in sites:
        out[s["price"]] = out.get(s["price"], 0) + 1
    return out


def retirement_of(rows, counting, residue, label=""):
    """Which twins stay alive under ``counting`` and what rides on the answer.

    ``members``/``bytes`` come from E479's own row for the twin -- the family it points at, which
    is what a retirement decision takes away, not the twin file's size.
    """
    by_twin = {r.get("twin"): r for r in (residue.get("rows") or [])}
    keep, retire = [], []
    for r in rows:
        res = by_twin.get(r["twin"]) or {}
        row = {"twin": r["twin"],
               "members": res.get("members", r["members"]),
               "bytes": res.get("bytes", r["bytes_on_disk"]),
               "read_sites": r["priced_read_sites"],
               "counting_sites": len([s for s in r["sites"] if s["price"] in counting])}
        (keep if row["counting_sites"] else retire).append(row)
    return {"label": label,
            "counting_classes": list(counting),
            "twins_kept": len(keep),
            "twins_retirable": len(retire),
            "members_behind_the_retirable_twins": sum(x["members"] or 0 for x in retire),
            "bytes_behind_the_retirable_twins": sum(x["bytes"] or 0 for x in retire),
            "retirable": [x["twin"] for x in retire],
            "kept": [x["twin"] for x in keep]}


def summary_of(rows, meta, residue):
    sites = [s for r in rows for s in r["sites"]]
    counting = [s for s in sites if s["price"] in COUNTS_AS_A_READER]
    any_site = tuple(sorted(set(s["price"] for s in sites))) if sites else ()
    tiers = [
        retirement_of(rows, COUNTS_AS_A_READER, residue,
                      "only_rederiving_and_pinning (the card's rule)"),
        retirement_of(rows, COUNTS_WITH_FAULTING, residue, "plus_faulting_blocks"),
        retirement_of(rows, COUNTS_WITH_REPUBLISHING, residue,
                      "plus_any_block_that_reads_or_asserts_a_payload_field"),
        retirement_of(rows, any_site, residue,
                      "every_read_site_counts_as_a_reader (E479's rule)"),
    ]
    wide, narrow, broad, parent_rule = tiers[0], tiers[1], tiers[2], tiers[3]
    status_quo = [r for r in rows if (r.get("parent_read_sites") or 0)]
    moved = [r["twin"] for r in rows
             if (r.get("parent_read_sites") or 0) and
             not any(s["price"] in COUNTS_AS_A_READER for s in r["sites"])]
    helper_sites = [s for s in sites if s.get("tier") == e497.T_HELPER]
    return {
        "twins_in_the_population": len(rows),
        "read_sites_priced": len(sites),
        "read_sites_by_tier": {e497.T_DIRECT: len([s for s in sites
                                                  if s.get("tier") == e497.T_DIRECT]),
                               e497.T_HELPER: len(helper_sites)},
        "prices": _classes(sites),
        "sites_that_count_as_a_reader": len(counting),
        "sites_that_do_not": len(sites) - len(counting),
        "helper_sites_that_count_as_a_reader": len([s for s in helper_sites
                                                   if s["price"] in COUNTS_AS_A_READER]),
        "twins_with_a_read_site_under_the_parent_arm": len(status_quo),
        "twins_with_no_counting_reader": len(moved),
        "twins_that_move_to_retirable": len(moved),
        "twins_moving": moved,
        "retirement_under_the_parent_rule": parent_rule,
        "retirement_when_only_rederiving_and_pinning_count": wide,
        "retirement_when_faulting_blocks_also_count": narrow,
        "retirement_when_republishing_fields_also_counts": broad,
        "retirement_ladder": tiers,
        "twins_that_would_stay_alive_if_presence_or_republishing_counted":
            sorted(set(wide["retirable"]) - set(broad["retirable"])),
        "bytes_left_undefended_by_the_strict_rule": wide["bytes_behind_the_retirable_twins"],
        "sources_scanned_with_a_tree": meta.get("sources_scanned_with_a_tree"),
    }


def verdict_of(summary):
    if not summary["read_sites_priced"]:
        return V_EMPTY
    if summary["twins_that_move_to_retirable"]:
        return V_MOVES
    return V_NONE


def build(root=None):
    root = root or ROOT
    rows, meta, toks, parent = measure(root)
    residue = _load_json(os.path.join(root, "results", "state_tilt", RESIDUE_FACE))
    summary = summary_of(rows, meta, residue)
    return {
        "study": "E499",
        "card": CARD,
        "title": ("Price the read sites the class delta did not show -- what each of E498's read "
                  "sites does with the payload, and what that does to the twins' retirement"),
        "generated": _now(),
        "evidence_cutoff": DATE_STAMP,
        "source_faces": {"population": "results/state_tilt/%s (E498)" % PARENT_FACE,
                         "residue_and_retirement": "results/state_tilt/%s (E479)" % RESIDUE_FACE,
                         "price_vocabulary": "scripts/e483_leg_debt.py (E483)",
                         "arm": "scripts/e497_twindead.py (E497)"},
        "population_meta": {
            "rule": ("the read sites E498's helper arm attributes to E479's 36 frozen twins, "
                     "both the ones it published and the literal ones it counted"),
            "size": summary["twins_in_the_population"],
            "bound": ("a price describes the block that owns the site, not the twin; a twin with "
                      "no counting site is one whose readers do nothing a producer must preserve "
                      "-- it is not thereby declared dead"),
        },
        "price_meta": {
            "counting_classes": list(COUNTS_AS_A_READER),
            "sensitivity_classes": {"with_faulting_blocks": list(COUNTS_WITH_FAULTING),
                                    "with_republishing_blocks": list(
                                        COUNTS_WITH_REPUBLISHING)},
            "vocabulary": list(PRICE_VOCAB),
            "helper_arm": ("a helper site's payload is the name bound to the helper call; the "
                           "helper's own definition decides whether that name carries fields"),
            "block_scope": ("a site whose line is not an opener is priced at the asserting block "
                            "found from the line itself; a module scope is never used as an "
                            "assertion scope for a line inside a function"),
            "candidate_tokens": toks,
        },
        "verdict": verdict_of(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "summary": summary,
        "rows": rows,
        "moved": [{"twin": r["twin"],
                   "parent_read_sites": r["parent_read_sites"],
                   "prices": _classes(r["sites"]),
                   "members": r["members"]}
                  for r in rows if r["twin"] in summary["twins_moving"]],
        "reading": ("E498 measured how many readers a literal census misses; this measures what "
                    "those readers do.  The strict rule is the one the card names: a site keeps a "
                    "face alive when it re-derives a number or pins a field, and a site that only "
                    "opens the file does not."),
    }


def _write(face, root=None):
    root = root or ROOT
    os.makedirs(os.path.join(root, "results", "state_tilt"), exist_ok=True)
    dated = os.path.join(root, "results", "state_tilt",
                         "%s-%s.json" % (DATED_PREFIX, DATE_STAMP.replace("-", "")))
    latest = os.path.join(root, "results", "state_tilt", FACE_NAME)
    for path in (dated, latest):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    return dated, latest


# ------------------------------------------------------------------------------- check
def tally_problems(face):
    problems = []
    rows = face.get("rows") or []
    summary = face.get("summary") or {}
    sites = [s for r in rows for s in (r.get("sites") or [])]
    if summary.get("twins_in_the_population") != len(rows):
        problems.append("the population size does not equal the row count")
    if summary.get("read_sites_priced") != len(sites):
        problems.append("the priced-site count does not re-derive from the rows")
    if (summary.get("prices") or {}) != _classes(sites):
        problems.append("the price tally does not re-derive from the rows")
    counting = [s for s in sites if s.get("price") in COUNTS_AS_A_READER]
    if summary.get("sites_that_count_as_a_reader") != len(counting):
        problems.append("the counting-site count does not re-derive from the rows")
    moved = [r["twin"] for r in rows
             if (r.get("parent_read_sites") or 0) and
             not any(s.get("price") in COUNTS_AS_A_READER for s in (r.get("sites") or []))]
    if summary.get("twins_that_move_to_retirable") != len(moved):
        problems.append("the moved-twin count does not re-derive from the rows")
    if sorted(summary.get("twins_moving") or []) != sorted(moved):
        problems.append("the moved-twin list does not re-derive from the rows")
    wide = summary.get("retirement_when_only_rederiving_and_pinning_count") or {}
    if wide.get("twins_kept", 0) + wide.get("twins_retirable", 0) != len(rows):
        problems.append("the strict retirement split does not add up to the population")
    broad = summary.get("retirement_when_republishing_fields_also_counts") or {}
    if broad.get("twins_kept", 0) + broad.get("twins_retirable", 0) != len(rows):
        problems.append("the republishing retirement split does not add up to the population")
    if (broad.get("twins_kept") or 0) < (wide.get("twins_kept") or 0):
        problems.append("a wider counting set retired a twin the strict set kept")
    if sorted(summary.get("twins_that_would_stay_alive_if_presence_or_republishing_counted")
              or []) != sorted(set(wide.get("retirable") or [])
                               - set(broad.get("retirable") or [])):
        problems.append("the rescue list does not re-derive from the two splits")
    for r in rows:
        if r.get("priced_read_sites") != len(r.get("sites") or []):
            problems.append("%s: the priced count does not equal its site list" % r.get("twin"))
        for s in r.get("sites") or []:
            if s.get("price") not in PRICE_VOCAB:
                problems.append("%s: %s is outside the price vocabulary"
                                % (r.get("twin"), s.get("price")))
    if face.get("verdict") != verdict_of(summary):
        problems.append("the verdict does not re-derive from the summary")
    return problems


def check(face=None, root=None):
    root = root or ROOT
    if face is None:
        face = _load_json(os.path.join(root, "results", "state_tilt", FACE_NAME))
    problems = tally_problems(face)
    print(json.dumps({"problems": problems, "rows": len(face.get("rows") or [])},
                     ensure_ascii=False))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    stored = _load_json(os.path.join(root, "results", "state_tilt", FACE_NAME))
    fresh = build(root)
    problems = []
    for key in ("verdict", "summary", "rows", "moved"):
        if stored.get(key) != fresh.get(key):
            problems.append("%s does not re-derive" % key)
    problems.extend(tally_problems(fresh))
    print(json.dumps({"problems": problems,
                      "verdict": fresh["verdict"],
                      "priced": fresh["summary"]["read_sites_priced"],
                      "moved": fresh["summary"]["twins_that_move_to_retirable"]},
                     ensure_ascii=False))
    return 0 if not problems else 1


# ------------------------------------------------------------------------------- selftest
def _fixture_tree():
    """A two-twin world: one twin read through a parsing helper and actually pinned, one read
    through a digest helper and only compared with a copy of itself."""
    import tempfile
    tmp = tempfile.mkdtemp(prefix="e499_")
    for rel in ("results/state_tilt", "data/famA", "data/famB"):
        os.makedirs(os.path.join(tmp, rel.replace("/", os.sep)))
    for rel in ("data/famA/a_latest.json", "data/famB/b_latest.json"):
        with io.open(os.path.join(tmp, rel.replace("/", os.sep)), "w", encoding="utf-8") as fh:
            fh.write("{}\n")
    reader = (
        "import json\n"
        "import hashlib\n"
        "PATH_A = 'data/famA/a_latest.json'\n"
        "PATH_B = 'data/famB/b_latest.json'\n"
        "def _read_json(p):\n"
        "    with open(p, encoding='utf-8') as fh:\n"
        "        return json.load(fh)\n"
        "def sha(p):\n"
        "    with open(p, 'rb') as fh:\n"
        "        return hashlib.sha256(fh.read()).hexdigest()\n"
        "def use_a():\n"
        "    face = _read_json(PATH_A)\n"
        "    assert face['summary']['n'] == 7\n"
        "def use_b():\n"
        "    assert sha(PATH_B) == sha(PATH_B + '.copy')\n")
    with io.open(os.path.join(tmp, "reader.py"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(reader)
    return tmp


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append({"leg": name, "ok": bool(ok), "detail": detail})

    # ---- the arm is inherited, not reimplemented
    tmp = _fixture_tree()
    kept_root, kept_cache = e483.ROOT, dict(e483._cache)
    try:
        e483.ROOT = tmp
        e483._cache.clear()
        a = price_site("reader.py", 13)
        b = price_site("reader.py", 15)
    finally:
        e483.ROOT = kept_root
        e483._cache.clear()
        e483._cache.update(kept_cache)
    leg("fixture: a helper that parses its file makes the bound name a payload root",
        a["roots_from_helpers"].get("face", {}).get("helper") == "_read_json",
        json.dumps(a["roots_from_helpers"]))
    leg("fixture: a pinned field through a parsing helper prices as a pin",
        a["price"] == e483.D_PIN, a["price"])
    leg("fixture: a digest compared with a copy prices as a bytes comparison",
        b["price"] == e483.D_BYTES, b["price"])

    # ---- the widened classifier must agree with the shared one when no widening is needed
    unit = ast.parse("import json\n"
                     "with open(P) as fh:\n"
                     "    d = json.load(fh)\n"
                     "assert d['summary']['n'] == 7\n")
    roots = e483.payload_roots(unit)
    mine, _c = classify_roots(unit, e483.module_names(unit), roots)
    theirs, _c2 = e483.classify_block(unit, e483.module_names(unit))
    leg("no-widening equivalence: this module's classify equals e483.classify_block",
        mine == theirs and roots, "%s vs %s" % (mine, theirs))

    # a widened root that is NOT a payload root must not be invented
    leg("a helper that only returns text is not a payload root",
        not helper_info(ast.parse("def sha(p):\n    return open(p,'rb').read()\n"),
                        "sha")["returns_payload"])

    # ---- the live face
    good = build()
    leg("face builds", good.get("verdict") in VERDICT_VOCAB)
    leg("check on the stored face is clean", check() == 0)
    leg("tallies re-derive", tally_problems(good) == [])
    s = good["summary"]
    leg("every twin in the population carries a row",
        s["twins_in_the_population"] == len(good["rows"]))
    leg("the parent arm's read sites are all priced",
        s["read_sites_priced"] >= len([x for r in good["rows"]
                                       for x in r["sites"] if x.get("tier") == e497.T_HELPER]),
        "%d priced, %d helper" % (s["read_sites_priced"],
                                  s["read_sites_by_tier"][e497.T_HELPER]))

    bad = json.loads(json.dumps(good))
    if bad["rows"]:
        bad["rows"][0]["priced_read_sites"] = (bad["rows"][0].get("priced_read_sites") or 0) + 1
    leg("a doctored site count is caught", bool(tally_problems(bad)))

    bad2 = json.loads(json.dumps(good))
    bad2["verdict"] = (V_NONE if good["verdict"] != V_NONE else V_MOVES)
    leg("a doctored verdict is caught", bool(tally_problems(bad2)))

    bad3 = json.loads(json.dumps(good))
    if bad3["rows"] and bad3["rows"][0].get("sites"):
        bad3["rows"][0]["sites"][0]["price"] = "reads_it_somehow"
    leg("a price outside the vocabulary is caught", bool(tally_problems(bad3)))

    passed = len([l for l in legs if l["ok"]])
    print(json.dumps({"selftest": "%d/%d" % (passed, len(legs)),
                      "legs": legs}, ensure_ascii=False))
    return 0 if passed == len(legs) else 1


# ------------------------------------------------------------------------------- entry
def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "verify", "selftest", "show"])
    args = ap.parse_args(argv)
    if args.cmd == "run":
        face = build()
        dated, _latest = _write(face)
        print(json.dumps({"face": os.path.relpath(dated, ROOT).replace("\\", "/"),
                          "verdict": face["verdict"],
                          "summary": {k: v for k, v in face["summary"].items()
                                      if not isinstance(v, (list, dict))},
                          "prices": face["summary"]["prices"]},
                         ensure_ascii=False))
        return 0
    if args.cmd == "check":
        return check()
    if args.cmd == "verify":
        return verify()
    if args.cmd == "selftest":
        return selftest()
    face = _load_json(os.path.join(OUTDIR, FACE_NAME))
    print(json.dumps(face.get("summary"), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())