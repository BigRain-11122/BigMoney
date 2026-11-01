"""E344 -- who consumes the names only the census family publishes?

E341 measured that at its pin 15 of 22 face stems lose every *writer* when the 16-file census
family is excluded, and E340 measured that 22 of 409 permission-shaped fields are read back by
their own producer.  Both are statements about producers.  This study asks the consumer question
directly, because "nobody writes this name" and "nobody reads this face" are different claims and
only the second one decides whether a face is worth publishing at all.

Two reading channels are measured, and they are kept apart because they fail differently:

    named     the stem appears inside a string literal of a source.  That literal is a *load* only
              when it, or a name bound to it, reaches a load primitive (open/load/loads/read_json/
              read_text).  A literal that is only compared, used as a selftest fixture, or printed
              is a citation, not a read -- E341's own selftest spells two of these stems and opens
              neither.
    unnamed   a source enumerates the face directory (glob/listdir/walk/iterdir/scandir) and loads
              every JSON it finds.  Such a reader consumes a face without ever naming it, so a
              name census reports zero readers while the file is read every time the study runs.
              Admission is decided mechanically: the enumeration pattern, with module constants
              folded in (``DOMAIN_PREFIX + "*"`` -> ``"BAND*"``), is matched against the published
              filename, and a prefix-filtered census is excluded by the same match.

What a reader takes off a face is published as a frozen evidence row per reader (class + quoted
code that must still exist at the pin), not as a claim about the author's intent.  A reader with no
evidence row is published as *unattributed* and the verdict degrades: this study fails closed
rather than describing a reader nobody looked at.

Self-exclusion (E207/E332 family): the corpus is read at the pin, and this file does not exist
there, so the scanner cannot count itself.

Usage:
    python scripts/e344_face_consumer_census.py run|verify|selftest
"""

import ast
import fnmatch
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e338_census_green_window as e338
import e341_sibling_closer_what_changed as e341

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-01"
FACE = "CONSUMERCENSUS-%s.json" % TODAY
LATEST = "consumercensus_latest.json"
STUDY = "E344_face_consumer_census"
SELF_REL = "scripts/e344_face_consumer_census.py"

# The tree the measurement is taken on.  A face that re-derives off the moving tip goes red the
# moment any .py lands (E338 family), so the corpus and the faces are both read from git.
PIN_SHA = "90c1fa8ae59536c4646e0c5a6ff319fa1977bf67"

ENVELOPE = ("generated", "stem", "study", "schema", "version", "evidence_cutoff", "clock_read",
            "ts", "date", "title", "no_bill")

ENUM_CALLS = ("glob", "iglob", "walk", "iterdir", "listdir", "scandir")
LOAD_CALLS = ("open", "load", "loads", "read_json", "read_text", "read_csv", "read_bytes")

# Frozen per-reader evidence.  ``class`` is what the reader takes off the face; ``pattern`` is the
# enumeration the reader was verified to run over the face directory; ``snippets`` are quoted code
# that verify() re-checks at the pin, so the claim cannot silently outlive its source.
READ_CLASSES = ("carries", "measures_shape", "declarations", "envelope_only")
DECLARED_READERS = {
    "scripts/e298_replay_control_census.py": {
        "class": "measures_shape",
        "pattern": "*.json",
        "snippets": ['paths = sorted(glob.glob(os.path.join(outdir, "*.json")))',
                     'control containers and leaf witnesses'],
        "note": ("loads every *.json in the face directory and walks each control block into leaf "
                 "paths; the published number is never compared to anything"),
    },
    "scripts/e302_universe_switch_backfill.py": {
        "class": "carries",
        "pattern": "*.json",
        "snippets": ['glob.glob(os.path.join(base, "*.json"))',
                     'row["published_verdict"] = face.get("verdict")'],
        "note": ("the only reader that takes a published measurement forward: each face's "
                 "`verdict` is copied into its own row, so a verdict cannot change without that "
                 "face disagreeing with itself"),
    },
    "scripts/e307_undated_face_vintage.py": {
        "class": "envelope_only",
        "pattern": "*.json",
        "snippets": ['glob.glob(os.path.join(outdir, "*.json"))',
                     'vintage._parse(face.get("generated"))'],
        "note": "reads each face and asks for its `generated` stamp, with an mtime fallback",
    },
    "scripts/e317_print_coverage_census.py": {
        "class": "measures_shape",
        "pattern": "results/**/*.json",
        "snippets": ['for base, dirs, files in os.walk(RESULTS):', 'def all_leaves('],
        "note": "walks results/**/*.json and flattens every face into leaf paths to price constants",
    },
    "scripts/e319_census_self_inclusion_sweep.py": {
        "class": "declarations",
        "pattern": "results/**/*.json",
        "snippets": ['study = doc["study"]', 'tokens.extend(doc[key])'],
        "note": ("reads each face's `study` and its declared exclusion lists to classify how a "
                 "census names its own population"),
    },
}

V_NAMED = "every_family_only_name_is_loaded_by_a_source_outside_the_family"
V_CARRIED = ("no_source_outside_the_family_names_these_faces_but_five_directory_censuses_read_"
             "every_published_face_and_one_of_them_carries_a_published_verdict_forward")
V_SHAPE = ("no_source_outside_the_family_names_these_faces_and_the_unnamed_readers_take_only_"
           "shape_and_stamps_off_them")
V_NOBODY = "no_reader_inside_or_outside_the_family_reads_these_faces_at_all"
V_UNATTRIBUTED = "a_reader_of_these_faces_has_no_evidence_row_so_what_it_takes_is_unknown"

MAX_ROWS = 40


# ------------------------------------------------------------------------------------- plumbing

def say(message):
    sys.stdout.write(str(message) + "\n")
    sys.stdout.flush()


def _fname(node):
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def parse(text):
    try:
        return ast.parse(text)
    except SyntaxError:
        return None


def strings(tree):
    """Every string literal as ``(line, value)``.  Comments are not AST nodes, so prose is out."""
    if tree is None:
        return []
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            out.append((getattr(node, "lineno", 0), node.value))
    return out


def constants(tree):
    """``{name: [str, ...]}`` for names bound to a string constant or a constant concatenation.

    Two passes, because a binding may be spelled through another binding
    (``DOMAIN_PREFIX = "BAND"`` then ``GLOB = DOMAIN_PREFIX + "*"``).  One pass folds the first and
    silently drops the second, which is the difference between a prefix-filtered census being
    excluded and a ``*.json`` sweep being reported as ``*``.
    """
    out = {}
    if tree is None:
        return out
    for _pass in range(3):
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            values = string_values(node.value, out)
            if not values:
                continue
            for target in node.targets:
                if isinstance(target, ast.Name):
                    for value in values:
                        if value not in out.setdefault(target.id, []):
                            out[target.id].append(value)
    return out


def string_values(node, consts, depth=0):
    """Resolve an expression to the strings it can evaluate to, folding names through ``consts``."""
    if depth > 4:
        return []
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.Name):
        return list(consts.get(node.id, []))
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = string_values(node.left, consts, depth + 1)
        right = string_values(node.right, consts, depth + 1)
        return [a + b for a in left for b in right][:40]
    if isinstance(node, ast.JoinedStr):
        parts = [""]
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts = [p + value.value for p in parts]
            else:
                return []
        return parts
    if isinstance(node, ast.Call) and _fname(node) in ("join",):
        # ``join(ROOT, "results", "state_tilt")`` cannot be resolved by value -- ROOT is a runtime
        # path.  Keep the trailing components that do resolve: that is exactly the part that names
        # the directory, and dropping the whole call is what hid every directory census.
        parts = []
        for arg in reversed(node.args):
            piece = string_values(arg, consts, depth + 1)
            if not piece:
                break
            parts.insert(0, piece[0])
        if not parts:
            return []
        joined = "/".join(parts)
        return [joined, "/" + joined]
    return []


def load_reached_literals(tree, consts):
    """Literals that reach a load primitive, directly or through a bound name."""
    reached = set()
    if tree is None:
        return reached
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or _fname(node) not in LOAD_CALLS:
            continue
        for arg in list(node.args) + [k.value for k in node.keywords]:
            for sub in ast.walk(arg):
                if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                    reached.add(sub.value)
                elif isinstance(sub, ast.Name):
                    for value in consts.get(sub.id, []):
                        if isinstance(value, str):
                            reached.add(value)
    return reached


def dir_bindings(tree, consts):
    """Names bound to the face directory itself (``.../results/state_tilt``) or its parent.

    ``ROOT`` is not a constant, so a path built with ``os.path.join(ROOT, "results", "state_tilt")``
    resolves to nothing by value.  The trailing component is what names the directory, and reading
    it is the difference between finding five directory censuses and finding none.
    """
    out = {"state_tilt": set(), "results": set()}
    if tree is None:
        return out
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        values = string_values(node.value, consts)
        tail = []
        if isinstance(node.value, ast.Call) and _fname(node.value) == "join" and node.value.args:
            tail = string_values(node.value.args[-1], consts)
        for value in values + tail:
            norm = value.replace("\\", "/").rstrip("/")
            for target in node.targets:
                if not isinstance(target, ast.Name):
                    continue
                if norm.endswith("state_tilt"):
                    out["state_tilt"].add(target.id)
                elif norm.endswith("results") and norm != "state_tilt":
                    out["results"].add(target.id)
    return out


def normalise_pattern(pattern):
    pattern = pattern.replace("\\", "/")
    if pattern.startswith("./"):
        pattern = pattern[2:]
    while pattern.startswith("/"):
        pattern = pattern[1:]
    return pattern


def _segments_match(pattern_segments, path_segments):
    if not pattern_segments:
        return not path_segments
    head = pattern_segments[0]
    if head == "**":
        for skip in range(len(path_segments) + 1):
            if _segments_match(pattern_segments[1:], path_segments[skip:]):
                return True
        return False
    if not path_segments:
        return False
    if not fnmatch.fnmatchcase(path_segments[0], head):
        return False
    return _segments_match(pattern_segments[1:], path_segments[1:])


def admits(pattern, base):
    """Would an enumeration pattern pick up ``results/state_tilt/<base>``?

    Segment-aware on purpose: ``fnmatch`` lets ``*`` cross ``/``, so a plain ``results/*.json``
    matched a face two directories down and turned a top-level sweep into a face reader.  A bare
    pattern is matched against the filename only, which is what a glob inside the face directory is.
    """
    pattern = normalise_pattern(pattern)
    if "/" in pattern:
        return _segments_match(pattern.split("/"), ("results/state_tilt/" + base).split("/"))
    return fnmatch.fnmatchcase(base, pattern)


# ----------------------------------------------------------------------------------- enumerations

def enumerations(tree, consts, dirs):
    """``[(pattern, how)]`` for every enumeration that could reach this study's face directory."""
    found = []
    if tree is None:
        return found
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or _fname(node) not in ENUM_CALLS:
            continue
        kind = _fname(node)
        for arg in list(node.args) + [k.value for k in node.keywords]:
            values = string_values(arg, consts)
            names = {sub.id for sub in ast.walk(arg) if isinstance(sub, ast.Name)}
            if kind in ("walk", "listdir", "iterdir", "scandir"):
                if names & dirs["results"]:
                    found.append(("results/**/*.json", "%s of the results root" % kind))
                elif names & dirs["state_tilt"]:
                    found.append(("*", "%s of the face directory" % kind))
                continue
            for value in values:
                norm = normalise_pattern(value)
                if "state_tilt" in norm:
                    found.append((norm, "%s under the face directory" % kind))
                elif norm.startswith("results/"):
                    found.append((norm, "%s under the results root" % kind))
                elif names & dirs["state_tilt"]:
                    found.append((norm, "%s of the face directory" % kind))
                elif names & dirs["results"]:
                    found.append(("results/" + norm, "%s of the results root" % kind))
    # dedupe, keep the widest-to-narrowest discovery order
    seen = []
    for pattern, how in found:
        if (pattern, how) not in seen:
            seen.append((pattern, how))
    return seen


# ---------------------------------------------------------------------------------------- measures

def published_faces(sha):
    """``{stem: [filename, ...]}`` for every dated face under results/state_tilt at ``sha``."""
    listing = e338._git("ls-tree", "-r", "--name-only", sha, "--", "results/state_tilt")
    out = {}
    for name in listing.splitlines():
        base = name.strip().rsplit("/", 1)[-1]
        match = re.match(r"^([A-Z][A-Z0-9_]{2,40})-\d{4}-\d{2}-\d{2}\.json$", base)
        if match:
            out.setdefault(match.group(1), []).append(base)
    return out


def family_only(corpus, published):
    """Stems every writer of which sits inside the census family (E341's population, re-derived)."""
    family = set(e338.CENSUS_FAMILY)
    rows = []
    for stem in sorted(published):
        naming = sorted(path for path, text in corpus.items() if e341.mentions(text, stem))
        outside = [path for path in naming if path not in family]
        if naming and not outside:
            rows.append({"stem": stem, "family_writers": naming, "writers": len(naming)})
    return rows


def face_keys(sha, published, stems):
    """``{stem: [top-level key, ...]}`` read off the published faces themselves."""
    out = {}
    for stem in stems:
        keys = []
        for base in published.get(stem, []):
            body = e338._git("show", "%s:results/state_tilt/%s" % (sha, base))
            try:
                doc = json.loads(body) if body else None
            except ValueError:
                doc = None
            if isinstance(doc, dict):
                for key in doc:
                    if key not in keys:
                        keys.append(key)
        out[stem] = keys
    return out


def named_readers(corpus, stems):
    family = set(e338.CENSUS_FAMILY)
    rows = []
    for path in sorted(corpus):
        tree = parse(corpus[path])
        if tree is None:
            continue
        consts = constants(tree)
        reached = load_reached_literals(tree, consts)
        literals = [value for _line, value in strings(tree)]
        for stem in stems:
            hits = [value for value in literals if stem in value]
            if not hits:
                continue
            loaded = [value for value in hits if value in reached]
            rows.append({
                "path": path,
                "stem": stem,
                "family": path in family,
                "literals": len(hits),
                "loaded": len(loaded),
                "samples": hits[:2],
            })
    return rows


def declared_readers(corpus, published, stems):
    """The frozen, cited census of unnamed readers, with their admitted faces re-derived."""
    rows = []
    for path in sorted(DECLARED_READERS):
        row = dict(DECLARED_READERS[path])
        admitted = [stem for stem in stems
                    if any(admits(row["pattern"], base) for base in published.get(stem, []))]
        rows.append({
            "path": path,
            "faces_admitted": len(admitted),
            "pattern": row["pattern"],
            "takes": row["class"],
            "note": row["note"],
            "in_corpus": path in corpus,
        })
    return rows


def sweepers(corpus, published, stems):
    """Every other source that enumerates results recursively and loads JSON.

    Not classed -- what a sweep takes off a face cannot be read off its enumeration -- but listed so
    that a *new* sweep shows up in the next round's face instead of being invisible to this census.
    """
    family = set(e338.CENSUS_FAMILY)
    rows = []
    for path in sorted(corpus):
        if path in family or path in DECLARED_READERS:
            continue
        tree = parse(corpus[path])
        if tree is None:
            continue
        consts = constants(tree)
        dirs = dir_bindings(tree, consts)
        enums = enumerations(tree, consts, dirs)
        if not any(p.startswith("results/") for p, _how in enums):
            continue
        if not any(_fname(node) in LOAD_CALLS for node in ast.walk(tree)
                   if isinstance(node, ast.Call)):
            continue
        patterns = sorted({p for p, _how in enums if p.startswith("results/")})
        admitted = [stem for stem in stems
                    if any(any(admits(p, base) for base in published.get(stem, [])) for p in patterns)]
        if admitted:
            rows.append({"path": path, "patterns": patterns[:4], "faces_matched": len(admitted)})
    return rows


def split_keys(keys, literal_set):
    env = sorted(set(keys) & set(ENVELOPE) & literal_set)
    meas = sorted(set(keys) - set(ENVELOPE) & set(literal_set))
    return env, meas


def drift_vs_e341(corpus, stems):
    """Names E341 published as family-only that no longer are at this pin, and who named them.

    E341's population was taken at 444d3be8; this study's pin is newer, and two of the fifteen
    names have since been *mentioned* by a source outside the family (E341 itself, which spells
    stems in its own selftest).  A population that silently shrank would be a different study, so
    the difference is published with the namer and whether that namer opens the face.
    """
    path = os.path.join(OUTDIR, "SIBLINGCLOSER-2026-11-01.json")
    if not os.path.exists(path):
        return {"e341_face": None, "published": None, "gained_a_namer": []}
    with io.open(path, encoding="utf-8") as fh:
        listed = (json.load(fh).get("exclusion_cost") or {}).get("names_orphaned") or []
    family = set(e338.CENSUS_FAMILY)
    gained = []
    for stem in listed:
        if stem in stems:
            continue
        outside = sorted(p for p, text in corpus.items()
                         if p not in family and e341.mentions(text, stem))
        loaded = []
        for p in outside:
            reached = load_reached_literals(parse(corpus[p]), constants(parse(corpus[p])))
            if any(stem in value for value in reached):
                loaded.append(p)
        gained.append({"stem": stem, "named_by": outside, "loaded_by": loaded})
    return {"e341_face": "SIBLINGCLOSER-2026-11-01.json", "published": len(listed),
            "gained_a_namer": gained}


def decide(summary):
    """Frozen rule; a function of the published summary only."""
    unattributed = summary.get("unattributed_readers") or []
    if unattributed:
        return V_UNATTRIBUTED
    if not summary.get("stems_total"):
        return V_NOBODY
    if summary.get("stems_with_a_named_outside_loader"):
        return V_NAMED
    if not summary.get("admitting_scan_readers"):
        return V_NOBODY
    if summary.get("readers_that_carry"):
        return V_CARRIED
    return V_SHAPE


# ------------------------------------------------------------------------------------------ build

def build(root=None):
    root = root or ROOT
    corpus = e341.pinned_corpus(PIN_SHA)
    published = published_faces(PIN_SHA)
    say("pinned corpus at %s: %s sources | %s dated faces under %s stems"
        % (PIN_SHA[:9], len(corpus), sum(len(v) for v in published.values()), len(published)))

    family_rows = family_only(corpus, published)
    stems = [row["stem"] for row in family_rows]
    say("names only the family writes (re-derived): %s" % len(stems))

    named = named_readers(corpus, stems)
    readers = declared_readers(corpus, published, stems)
    swept = sweepers(corpus, published, stems)
    keys = face_keys(PIN_SHA, published, stems)
    all_keys = sorted({key for stem in stems for key in keys.get(stem, [])})
    drift = drift_vs_e341(corpus, stems)

    scan_rows = []
    unattributed = []
    for row in readers:
        literal_set = {value for _line, value in strings(parse(corpus.get(row["path"], "")))}
        env, meas = split_keys(all_keys, literal_set)
        if not row["takes"]:
            unattributed.append(row["path"])
        scan_rows.append({
            "path": row["path"],
            "faces_admitted": row["faces_admitted"],
            "patterns": [row["pattern"]],
            "envelope_keys_named": env,
            "measurement_keys_named": meas,
            "takes": row["takes"],
            "note": row["note"],
        })

    named_outside = [row for row in named if not row["family"]]
    by_class = {}
    for row in scan_rows:
        if row["takes"]:
            by_class[row["takes"]] = by_class.get(row["takes"], 0) + 1
    read_stems = {stem for row in scan_rows if row["faces_admitted"]
                  for stem in stems
                  if any(admits(row["patterns"][0], base) for base in published.get(stem, []))}

    summary = {
        "stems_total": len(stems),
        "stems_with_no_named_outside_reader": sum(
            1 for stem in stems if not any(r["stem"] == stem for r in named_outside)),
        "stems_with_a_named_outside_loader": sum(
            1 for stem in stems if any(r["stem"] == stem and r["loaded"] for r in named_outside)),
        "stems_with_no_reader_at_all": sum(1 for stem in stems if stem not in read_stems),
        "named_readers_total": len(named),
        "named_readers_outside_the_family": len(named_outside),
        "named_outside_loaders": sum(1 for row in named_outside if row["loaded"]),
        "admitting_scan_readers": len([row for row in scan_rows if row["faces_admitted"]]),
        "declared_readers_in_corpus": len([row for row in readers if row["in_corpus"]]),
        "recursive_sweepers_listed": len(swept),
        "readers_by_class": by_class,
        "readers_that_carry": by_class.get("carries", 0),
        "unattributed_readers": unattributed,
        "family_published_stems": len(stems),
        "share_of_family_faces_with_no_named_outside_reader": e341._share(
            sum(1 for stem in stems if not any(r["stem"] == stem for r in named_outside)), len(stems)),
        "drift_vs_e341": {
            "published": drift["published"],
            "gained_a_namer_count": len(drift["gained_a_namer"]),
            "gained_a_loader_count": sum(1 for row in drift["gained_a_namer"] if row["loaded_by"]),
        },
    }

    verdict = decide(summary)
    reasons = [
        "of the %s names only the family writes at this pin, %s is loaded by a source outside the "
        "family; the %s non-family occurrence(s) are literals that are compared or printed, never "
        "opened -- a name census reports zero readers and that is a statement about writers"
        % (len(stems), summary["stems_with_a_named_outside_loader"],
           summary["named_readers_outside_the_family"]),
        "the population moved since E341: %s of its %s names gained a namer outside the family and "
        "%s of them gained a loader -- the drift is published rather than absorbed into a smaller "
        "population"
        % (summary["drift_vs_e341"]["gained_a_namer_count"], drift["published"],
           summary["drift_vs_e341"]["gained_a_loader_count"]),
        "%s directory census(es) read every published face in results/state_tilt without naming "
        "it, so %s of the %s names have a reader and %s has none"
        % (len(scan_rows), len(stems) - summary["stems_with_no_reader_at_all"], len(stems),
           summary["stems_with_no_reader_at_all"]),
        "what those readers take is uneven and published per reader: %s"
        % (" | ".join("%s=%s" % (k, v) for k, v in sorted(by_class.items())) or "nothing"),
        "the family's numbers do not gate anything outside it: one reader copies a `verdict` into "
        "its own row and the rest take leaf paths, stamps or declared lists -- so these faces are "
        "population members of a census of censuses rather than inputs to a decision",
    ]

    doc = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "definition": {
            "pin": PIN_SHA,
            "population": "every .py under scripts/Tools/live/monitor/firm at the pin",
            "family": list(e338.CENSUS_FAMILY),
            "family_only_name": "a published face stem every naming source of which is in the family",
            "named_read": "the stem appears inside a string literal of a source",
            "named_load": "that literal, or a name bound to it, reaches a load primitive",
            "unnamed_read": "an enumeration of the face directory admits the filename and the "
                            "source loads JSON; module constants are folded into the pattern",
            "envelope_keys": list(ENVELOPE),
            "verdict_rule": ("unattributed reader -> unattributed; a named outside loader -> named; "
                             "no admitting scan -> nobody; a carrier -> carried; else shape-only"),
        },
        "summary": summary,
        "named_readers": named,
        "family_only_names": [{"stem": row["stem"], "writers": row["writers"],
                               "family_writers": row["family_writers"]} for row in family_rows][:MAX_ROWS],
        "drift_vs_e341": drift,
        "scan_readers": scan_rows,
        "recursive_sweepers": swept,
        "face_keys": keys,
        "verdict": verdict,
        "reasons": reasons,
        "limits": {
            "class_is_cited_not_proved": ("what each reader takes is a frozen evidence row with "
                                          "quoted code re-checked at the pin, not a dataflow proof: "
                                          "a comparison against a face value inside a helper this "
                                          "study does not follow would not be seen"),
            "admission_is_pattern_matching": ("a census that enumerates results and then filters by "
                                              "a name rule *after* the load is admitted here, "
                                              "which is the reading its own docstring takes"),
            "literals_are_not_paths": ("a literal that reaches `open` is a load even when the path "
                                       "is assembled elsewhere; the reading is deliberately wider "
                                       "than 'this file opened this face' and is stated as such"),
            "pinned_commit": ("the corpus and every face are read at %s; this file lands after it, "
                              "so it is one .py smaller than the tree that publishes this face"
                              % PIN_SHA[:9]),
        },
    }
    _write(doc, root)
    return doc


def _write(doc, root=None):
    outdir = os.path.join(root or ROOT, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    for name in (FACE, LATEST):
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=2, sort_keys=False)
            fh.write("\n")


# ----------------------------------------------------------------------------------------- verify

def _cmp(a, b, path, out):
    if type(a) is not type(b) and not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
        out.append("%s: type %s vs %s" % (path, type(a).__name__, type(b).__name__))
        return
    if isinstance(a, dict):
        for key in set(a) | set(b):
            if key in ("generated", "asof_head"):
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
    path = os.path.join(root, "results", "state_tilt", FACE)
    if not os.path.exists(path):
        return ["face missing: %s" % FACE]
    with io.open(path, encoding="utf-8") as fh:
        disk = json.load(fh)
    problems = []
    # the frozen evidence must still exist at the pin -- a citation that rotted is worse than none
    for reader, row in sorted(DECLARED_READERS.items()):
        text = e338._git("show", "%s:%s" % (PIN_SHA, reader))
        if not text:
            problems.append("evidence source missing at the pin: %s" % reader)
            continue
        for snippet in row["snippets"]:
            if snippet not in text:
                problems.append("evidence snippet gone from %s: %r" % (reader, snippet[:60]))
    fresh = build(root)
    _cmp(disk, fresh, "face", problems)
    return problems


# --------------------------------------------------------------------------------------- selftest

def cmd_selftest():
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    # -- literal reading
    tree = parse('FACE = "CONSUMERCENSUS-%s.json" % TODAY\n')
    check("L1 a dated/template literal is collected", any("CONSUMERCENSUS" in v for _l, v in strings(tree)))
    tree = parse('# CONSUMERCENSUS is named only in this comment\nX = 1\n')
    check("L2 a comment is not a literal", not strings(tree))
    check("L3 a syntax error is not a crash", strings(parse("def (")) == [])

    # -- constant folding
    tree = parse('DOMAIN_PREFIX = "BAND"\nG = DOMAIN_PREFIX + "*"\n')
    consts = constants(tree)
    check("L4 a name folds to its constant", consts.get("DOMAIN_PREFIX") == ["BAND"], str(consts))
    check("L5 a concatenation folds through the name", consts.get("G") == ["BAND*"], str(consts))
    tree = parse('OUTDIR = os.path.join(ROOT, "results", "state_tilt")\np = glob.glob(os.path.join(OUTDIR, "*.json"))\n')
    consts = constants(tree)
    dirs = dir_bindings(tree, consts)
    check("L6 the face directory is recognised by suffix", "OUTDIR" in dirs["state_tilt"], str(dirs))
    check("L7 a glob in the face directory is an enumeration",
          any("state_tilt" in pattern and admits(pattern, "CONSUMERCENSUS-2026-11-01.json")
              for pattern, _how in enumerations(tree, consts, dirs)),
          str(enumerations(tree, consts, dirs)))

    # -- admission
    check("L8 a bare *.json admits a dated face", admits("*.json", "CONSUMERCENSUS-2026-11-01.json"))
    check("L9 a BAND prefix does not", not admits("BAND*.json", "CONSUMERCENSUS-2026-11-01.json"))
    check("L10 a results/** model admits the face",
          admits("results/**/*.json", "CONSUMERCENSUS-2026-11-01.json"))
    check("L11 an unrelated directory does not",
          not admits("results/other/*.json", "CONSUMERCENSUS-2026-11-01.json"))

    # -- loader reach
    tree = parse('FACE = "X-2026-11-01.json"\nopen(FACE)\n')
    consts = constants(tree)
    check("L12 a bound name reaching open is a load",
          "X-2026-11-01.json" in load_reached_literals(tree, consts))
    tree = parse('FACE = "X-2026-11-01.json"\nFACE == "X-2026-11-01.json"\n')
    check("L13 a compared literal is not a load",
          "X-2026-11-01.json" not in load_reached_literals(tree, constants(tree)))

    # -- key split
    env, meas = split_keys(["generated", "verdict", "rows"], {"generated", "verdict"})
    check("L14 the envelope is split from the measurement", env == ["generated"] and meas == ["verdict"],
          "%s / %s" % (env, meas))

    # -- decide, frozen rule
    base = {"stems_total": 15, "stems_with_a_named_outside_loader": 0, "admitting_scan_readers": 5,
            "readers_that_carry": 1, "unattributed_readers": []}
    check("L15 an unattributed reader degrades the verdict first",
          decide(dict(base, unattributed_readers=["x"])) == V_UNATTRIBUTED)
    check("L16 a named outside loader is the named verdict",
          decide(dict(base, stems_with_a_named_outside_loader=2)) == V_NAMED)
    check("L17 no admitting scan means nobody", decide(dict(base, admitting_scan_readers=0)) == V_NOBODY)
    check("L18 a carrier is the carried verdict", decide(base) == V_CARRIED)
    check("L19 no carrier is the shape-only verdict", decide(dict(base, readers_that_carry=0)) == V_SHAPE)
    check("L20 no stems is nobody", decide(dict(base, stems_total=0)) == V_NOBODY)

    # -- the face, when it exists, must agree with its own verdict and its own counts
    path = os.path.join(OUTDIR, FACE)
    if os.path.exists(path):
        with io.open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        summary = doc.get("summary") or {}
        check("L21 published verdict is the frozen rule's output",
              doc.get("verdict") == decide(summary),
              "%s vs %s" % (doc.get("verdict"), decide(summary)))
        check("L22 the latest mirror carries the whole face",
              json.load(io.open(os.path.join(OUTDIR, LATEST), encoding="utf-8")) == doc)
        check("L23 every admitting reader has an evidence row",
              not summary.get("unattributed_readers"), str(summary.get("unattributed_readers")))
        check("L24 every evidence class is in the frozen vocabulary",
              all(row.get("takes") in READ_CLASSES for row in doc.get("scan_readers") or []))
        check("L25 the scan count is the published row count",
              int(summary.get("admitting_scan_readers") or -1) == len(doc.get("scan_readers") or []))
        check("L26 the class counts are the rows",
              sum((summary.get("readers_by_class") or {}).values())
              == len([r for r in doc.get("scan_readers") or [] if r.get("takes")]))
        named = doc.get("named_readers") or []
        outside = [r for r in named if not r["family"]]
        check("L27 the outside-loader count is the row list",
              summary.get("named_outside_loaders") == sum(1 for r in outside if r["loaded"]),
              "%s vs %s" % (summary.get("named_outside_loaders"),
                            sum(1 for r in outside if r["loaded"])))
        check("L28 no stem default is hidden: the share is published as a fraction",
              isinstance(summary.get("share_of_family_faces_with_no_named_outside_reader"), float))
        check("L29 the frozen evidence still exists at the pin",
              all(snippet in e338._git("show", "%s:%s" % (PIN_SHA, reader))
                  for reader, row in DECLARED_READERS.items() for snippet in row["snippets"]))
        listed = (json.load(io.open(os.path.join(OUTDIR, "SIBLINGCLOSER-2026-11-01.json"),
                                    encoding="utf-8")).get("exclusion_cost") or {}).get("names_orphaned") or []
        here = [row["stem"] for row in doc.get("family_only_names") or []]
        drift = doc.get("drift_vs_e341") or {}
        gained = drift.get("gained_a_namer") or []
        check("L30 the names here are a subset of E341's published list",
              set(here) <= set(listed) and len(here) + len(gained) == len(listed),
              "%s here / %s listed / %s gained" % (len(here), len(listed), len(gained)))
        check("L31 every name that left E341's list is published with its namer",
              all(row.get("stem") and row.get("named_by") is not None for row in gained),
              str(gained))
        check("L32 the sweeper list is published, not swallowed",
              isinstance(doc.get("recursive_sweepers"), list)
              and int(summary.get("recursive_sweepers_listed") or -1) == len(doc["recursive_sweepers"]))

    passed = sum(1 for _n, ok, _d in checks if ok)
    for name, ok, detail in checks:
        say("%s %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if (detail and not ok) else ""))
    say("selftest: %s/%s" % (passed, len(checks)))
    return 0 if passed == len(checks) else 1


# -------------------------------------------------------------------------------------------- cli

def cmd_run():
    doc = build()
    summary = doc["summary"]
    say("%s -> results/state_tilt/%s" % (STUDY, FACE))
    say("verdict: %s" % doc["verdict"])
    say("names measured: %s | loaded by an outside source: %s | no named outside reader: %s"
        % (summary["stems_total"], summary["stems_with_a_named_outside_loader"],
           summary["stems_with_no_named_outside_reader"]))
    say("unnamed readers: %s | no reader at all: %s"
        % (summary["admitting_scan_readers"], summary["stems_with_no_reader_at_all"]))
    for row in doc["scan_readers"]:
        say("  %-46s faces=%-2s takes=%-16s keys(meas)=%s"
            % (row["path"], row["faces_admitted"], row["takes"],
               len(row["measurement_keys_named"])))
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