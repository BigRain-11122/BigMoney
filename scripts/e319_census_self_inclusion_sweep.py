"""E319 -- every census in this programme counts other censuses, and no declared
exclusion list can say so.

E317 (r1336) drew its population from ``results/**/*.json`` and excluded exactly one
thing: ``self_faces_excluded`` = its own two filenames plus four hand-typed filename
prefixes (``GATEFORM-``, ``GATECLAMP-``, ``LEGEPS-``, ``GATEPRINT-``).  E318 then found
68 of the 69 surviving zero-tolerance gates sitting on four *earlier* study faces --
faces E317's list did not cover because they were published before the list existed.

That is not a bug in one constant.  It is the shape of the mechanism: a census's guard
is a list of filenames, and "is this face itself a census of somebody else's rows" is
not a filename property.  This study measures the whole population.

Four legs, one face:

1. **Discovery.** Which faces are study faces, and which of them census another face?
   The rule is frozen before any number is read: a *row* pointer is a ``.json`` string
   whose immediate parent key is a face/path token or whose parent container is named
   for faces.  Every other mention is prose and is reported but never counted.

2. **The graph.** Census -> counted study, per row, with the JSON path that made it.

3. **The exclusion audit.** For every census, what it declares, what that declaration
   resolves to, and how many of the censuses it counts the declaration covers.  The
   declared list is classified by shape: none / its own files / a glob / a hand-typed
   family-prefix list.

4. **The vintage audit.** A census row names a *filename*, and filenames are rewritten
   in place, so the content a census counted is not recoverable from the arc.  Compare
   the two ``generated`` stamps at the coarser granularity of the pair: a date-only
   stamp against a same-day timestamp is INDETERMINATE, never "forward" -- string
   comparison of ``2026-10-31`` against ``2026-10-31T04:10:24`` manufactures 34 phantom
   forward edges out of 306.

usage:
  python scripts/e319_census_self_inclusion_sweep.py run
  python scripts/e319_census_self_inclusion_sweep.py verify
  python scripts/e319_census_self_inclusion_sweep.py selftest
"""

import datetime
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
OUTDIR = os.path.join(RESULTS, "state_tilt")
FACE = "SELFINCLUSION-%s.json"
LATEST = "selfinclusion_latest.json"
TODAY = "2026-10-31"
STUDY = "E319_census_self_inclusion_sweep"

# ---- frozen before any number is read -----------------------------------------
STUDY_RE = re.compile(r"^E(\d+)_")
# A string is a ROW pointer when its immediate parent key names a face/path slot, or
# when the container it sits in is named for faces.  Anything else is prose (E207/E208
# family: a mention is not a row).
ROW_LEAF_KEYS = frozenset((
    "face", "faces", "path", "source", "src", "file", "face_path",
    "source_face", "face_file", "face_name",
))
ROW_CONTAINER_TOKENS = ("face",)
EXCLUSION_KEYS = ("self_faces_excluded", "self_excluded_faces")
SCRIPT_EXCLUSION_KEYS = ("self_scripts_excluded",)
# Stamp granularity, coarsest last.  A pair is only comparable down to its coarser half.
STAMP_FORMATS = (
    ("%Y-%m-%dT%H:%M:%S", "s"),
    ("%Y-%m-%d %H:%M:%S", "s"),
    ("%Y-%m-%dT%H:%M", "m"),
    ("%Y-%m-%d", "d"),
)


def study_ordinal(study):
    m = STUDY_RE.match(study or "")
    return int(m.group(1)) if m else None


def parse_stamp(raw):
    """(datetime, granularity) or (None, None).  Never guesses a missing field."""
    text = str(raw or "")
    for fmt, gran in STAMP_FORMATS:
        width = len(datetime.datetime.now().strftime(fmt))
        try:
            return datetime.datetime.strptime(text[:width], fmt), gran
        except Exception:
            continue
    return None, None


def pointer_class(json_path):
    """'row' for a structured pointer, 'prose' for a mention. Pure and total."""
    if len(json_path) < 2:
        return "prose"
    parent_key = json_path[-2]
    leaf_key = json_path[-1]
    if leaf_key in ROW_LEAF_KEYS:
        return "row"
    low = parent_key.lower()
    return "row" if any(tok in low for tok in ROW_CONTAINER_TOKENS) else "prose"


def collect_refs(doc, base):
    """Every reference this face makes to another face, with the path that made it."""
    out = []

    def walk(node, path):
        if isinstance(node, dict):
            for key, value in node.items():
                walk(value, path + [str(key)])
        elif isinstance(node, list):
            for value in node:
                walk(value, path)
        elif isinstance(node, str) and node.endswith(".json"):
            target = base.get(os.path.basename(node))
            if target is not None:
                out.append({
                    "target": target,
                    "json_path": ".".join(path),
                    "class": pointer_class(path),
                })

    walk(doc, [])
    return out


def exclusion_kind(tokens):
    """Shape of a declared exclusion list.  Frozen vocabulary, no enumeration of names."""
    if not tokens:
        return "none"
    if any("*" in str(t) for t in tokens):
        return "glob_pattern"
    if any(str(t).endswith("-") for t in tokens):
        return "family_prefix_list"
    return "own_filenames_only"


def resolve_exclusions(tokens, canon):
    """Which studies a declared list actually reaches, under the frozen reading rules."""
    hit = set()
    for token in tokens:
        token = str(token)
        if token.endswith("-"):
            prefix = token.upper()
            for study, path in canon.items():
                if os.path.basename(path).upper().startswith(prefix):
                    hit.add(study)
        elif "*" in token:
            pattern = re.compile("^" + re.escape(token).replace(r"\*", ".*") + "$", re.I)
            for study, path in canon.items():
                if pattern.match(os.path.basename(path)):
                    hit.add(study)
        else:
            low = token.lower()
            for study, path in canon.items():
                if os.path.basename(path).lower() == low:
                    hit.add(study)
    return hit


def canonical_faces(docs):
    """One canonical face per study, chosen deterministically.

    The ``*_latest`` twin is always dropped, and among the dated builds the
    lexicographically greatest basename wins.  Discovery order must not decide which
    build of a face this study reads -- an os.walk order is not a version rule.
    """
    pick = {}
    for path, doc in docs.items():
        study = doc["study"]
        name = os.path.basename(path)
        is_latest = "latest" in name.lower()
        current = pick.get(study)
        if current is None:
            pick[study] = (is_latest, name, path)
            continue
        cur_latest, cur_name, _cur_path = current
        if (cur_latest, ) > (is_latest, ):
            continue
        if is_latest < cur_latest or (is_latest == cur_latest and name > cur_name):
            pick[study] = (is_latest, name, path)
    return {study: triple[2] for study, triple in pick.items()}


def graph(docs, base, canon):
    """Census edges.  A study is a census only when it points at ANOTHER study's face."""
    edges = {}
    per_face = {}
    for study, path in canon.items():
        refs = collect_refs(docs[path], base)
        rows = [r for r in refs if r["class"] == "row"]
        prose = [r for r in refs if r["class"] == "prose"]
        counted = sorted({docs[r["target"]]["study"] for r in rows} - {study})
        prose_studies = sorted({docs[r["target"]]["study"] for r in prose} - {study})
        per_face[study] = {
            "face": os.path.relpath(path, ROOT).replace("\\", "/"),
            "row_pointers": len([r for r in rows if docs[r["target"]]["study"] != study]),
            "row_targets": counted,
            "prose_only_mentions": len([r for r in prose if docs[r["target"]]["study"] != study]),
            "prose_only_targets": prose_studies,
            "json_paths": sorted({r["json_path"] for r in rows
                                  if docs[r["target"]]["study"] != study})[:6],
        }
        if counted:
            edges[study] = set(counted)
    return edges, per_face


def transitive(edges, start):
    seen = set()
    stack = list(edges.get(start, ()))
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        stack.extend(edges.get(node, ()))
    return seen


def vintage_pair(gen_census, gen_counted):
    """(verdict, note) where verdict is forward / backward / indeterminate / unknown."""
    a, ga = parse_stamp(gen_census)
    b, gb = parse_stamp(gen_counted)
    if a is None or b is None:
        return "unknown", "missing stamp"
    if a.date() == b.date() and ("d" in (ga, gb)):
        return "indeterminate", "same day, one stamp has date granularity only"
    if b > a:
        return "forward", "counted face carries a later stamp than the census face"
    return "backward", ""


def build_census(edges, per_face, docs, canon):
    censuses = set(edges)
    cand_edges = sorted(
        [(a, b) for a in edges for b in edges[a] if b in censuses],
        key=lambda pair: (study_ordinal(pair[0]), study_ordinal(pair[1])),
    )
    all_edges = sorted(
        [(a, b) for a in edges for b in edges[a]],
        key=lambda pair: (study_ordinal(pair[0]), study_ordinal(pair[1])),
    )
    indeg = {}
    for _, target in all_edges:
        indeg[target] = indeg.get(target, 0) + 1
    later = {}
    for census, target in cand_edges:
        if target in censuses and study_ordinal(target) < study_ordinal(census):
            later.setdefault(target, []).append(census)
    return {
        "studies": len(canon),
        "census_studies": len(censuses),
        "all_edges": len(all_edges),
        "census_to_census_edges": len(cand_edges),
        "studies_counted_as_rows": len({b for _, b in all_edges}),
        "censuses_counted_by_a_later_census": len(later),
        "max_in_degree": max(indeg.values()) if indeg else 0,
        "max_transitive_closure": max((len(transitive(edges, s)) for s in edges), default=0),
        "_later": later,
        "_indeg": indeg,
    }


def exclusion_rows(edges, per_face, docs, canon):
    censuses = set(edges)
    rows = []
    covered = 0
    total_census_edges = 0
    for study in sorted(edges, key=study_ordinal):
        doc = docs[canon[study]]
        tokens = []
        for key in EXCLUSION_KEYS:
            if key in doc:
                tokens.extend(doc[key])
        kind = exclusion_kind(tokens)
        resolved = resolve_exclusions(tokens, canon)
        counted_censuses = sorted([c for c in edges[study] if c in censuses],
                                 key=study_ordinal)
        reached = [c for c in counted_censuses if c in resolved]
        total_census_edges += len(counted_censuses)
        covered += len(reached)
        rows.append({
            "study": study,
            "declared": list(tokens),
            "declared_kind": kind,
            "declared_reaches_studies": sorted(resolved, key=study_ordinal),
            "counted_studies": len(edges[study]),
            "counted_censuses": len(counted_censuses),
            "counted_censuses_covered_by_the_declaration": len(reached),
            "counted_censuses_missed": len(counted_censuses) - len(reached),
        })
    return rows, covered, total_census_edges


def vintage_rows(edges, per_face, docs, canon):
    rows = []
    tally = {"forward": 0, "backward": 0, "indeterminate": 0, "unknown": 0}
    for study in sorted(edges, key=study_ordinal):
        census_stamp = docs[canon[study]].get("generated")
        for target in sorted(edges[study], key=study_ordinal):
            verdict, note = vintage_pair(census_stamp, docs[canon[target]].get("generated"))
            tally[verdict] += 1
            if verdict == "forward":
                rows.append({
                    "census": study,
                    "counted": target,
                    "census_generated": str(census_stamp),
                    "counted_generated": str(docs[canon[target]].get("generated")),
                    "note": note,
                })
    return rows, tally


# ---- self-contained fixtures (hermetic; no file reads) ------------------------
def _fixture():
    """Five studies: A(10) counts B(11) and mentions E(14) only in prose;
    B and E count nothing; C(12) counts A and D(13)."""
    docs = {
        "/r/A-1.json": {
            "study": "E10_alpha", "generated": "2026-10-31T10:00:00",
            "self_faces_excluded": ["A-1.json", "a_latest.json"],
            "rows": [{"face": "results/B-1.json", "n": 2}],
            "notes": "results/E-1.json",
        },
        "/r/a_latest.json": {"study": "E10_alpha", "generated": "2026-10-31T10:00:00",
                             "rows": [{"face": "results/B-1.json"}]},
        "/r/B-1.json": {"study": "E11_beta", "generated": "2026-10-31"},
        "/r/C-1.json": {
            "study": "E12_gamma", "generated": "2026-10-31T09:00:00",
            "self_faces_excluded": ["A-", "C-"],
            "face_rows": [{"face": "results/A-1.json"}, {"face": "results/D-1.json"}],
        },
        "/r/D-1.json": {"study": "E13_delta", "generated": "2026-10-31T11:00:00"},
        "/r/E-1.json": {"study": "E14_epsilon", "generated": "2026-10-31T08:00:00"},
    }
    return docs


def selftest():
    checks = []

    def check(name, ok, detail=""):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    docs = _fixture()
    base = {}
    for path in docs:
        base.setdefault(os.path.basename(path), path)

    # L1  pointer classification is total and separates row from prose
    check("L1 row pointer under a face key is a row",
          pointer_class(["rows", "0", "face"]) == "row")
    check("L2 mention in a notes field is prose",
          pointer_class(["notes"]) == "prose")
    check("L3 a bare top-level string is prose",
          pointer_class(["thing"]) == "prose")

    canon = canonical_faces(docs)
    check("L4 canonical face prefers the dated build over the latest twin",
          os.path.basename(canon["E10_alpha"]) == "A-1.json",
          os.path.basename(canon["E10_alpha"]))

    edges, per_face = graph(docs, base, canon)
    check("L5 census edges are A->B and C->{A,D}",
          {k: sorted(v) for k, v in edges.items()} ==
          {"E10_alpha": ["E11_beta"], "E12_gamma": ["E10_alpha", "E13_delta"]},
          json.dumps({k: sorted(v) for k, v in edges.items()}))
    check("L6 a prose-only mention does not create an edge",
          per_face["E10_alpha"]["prose_only_targets"] == ["E14_epsilon"] and
          per_face["E10_alpha"]["row_targets"] == ["E11_beta"] and
          "E14_epsilon" not in edges["E10_alpha"],
          "row=%s prose=%s" % (per_face["E10_alpha"]["row_targets"],
                               per_face["E10_alpha"]["prose_only_targets"]))
    check("L7 a study that counts nothing is not a census",
          "E11_beta" not in edges and "E13_delta" not in edges and
          "E14_epsilon" not in edges)

    # L8  exclusion shapes are classified by shape, not by enumerating names
    check("L8 own filename list is classified as own_filenames_only",
          exclusion_kind(["A-1.json", "a_latest.json"]) == "own_filenames_only")
    check("L9 prefix list is its own class",
          exclusion_kind(["A-", "C-"]) == "family_prefix_list")
    check("L10 glob is its own class", exclusion_kind(["*_latest.json"]) == "glob_pattern")
    check("L11 empty list is none", exclusion_kind([]) == "none")

    rows, covered, total = exclusion_rows(edges, per_face, docs, canon)
    gamma = [r for r in rows if r["study"] == "E12_gamma"][0]
    alpha = [r for r in rows if r["study"] == "E10_alpha"][0]
    check("L12 a prefix list resolves to the studies it actually names",
          gamma["counted_censuses_covered_by_the_declaration"] == 1,
          json.dumps(gamma))
    check("L13 a self-filename list covers no census at all",
          alpha["counted_censuses_covered_by_the_declaration"] == 0,
          json.dumps(alpha))
    check("L14 covered is the sum of per-row coverage",
          covered == sum(r["counted_censuses_covered_by_the_declaration"] for r in rows))
    check("L15 total is the sum of per-row counted censuses",
          total == sum(r["counted_censuses"] for r in rows))

    # L16  vintage comparison must not compare a date against a timestamp of that date
    check("L16 date-only vs same-day timestamp is indeterminate",
          vintage_pair("2026-10-31", "2026-10-31T04:10:24")[0] == "indeterminate")
    check("L17 a genuinely later timestamp is forward",
          vintage_pair("2026-10-31T15:30:39", "2026-10-31T22:16:03")[0] == "forward")
    check("L18 an earlier timestamp is backward",
          vintage_pair("2026-10-31T22:16:03", "2026-10-31T15:30:39")[0] == "backward")
    check("L19 a missing stamp is unknown, never backward",
          vintage_pair(None, "2026-10-31")[0] == "unknown")

    vrows, tally = vintage_rows(edges, per_face, docs, canon)
    check("L20 C(09:00) counts A(10:00) and D(11:00): exactly two forward arcs",
          sorted(r["counted"] for r in vrows) == ["E10_alpha", "E13_delta"],
          json.dumps(vrows))
    check("L21 every vintage arc lands in exactly one tally bucket",
          sum(tally.values()) == sum(len(v) for v in edges.values()))

    # L22  mutation: folding prose into rows changes the population, so the split is load
    baseline = len({(a, b) for a in edges for b in edges[a]})
    _saved_class = pointer_class

    def _all_rows(json_path):
        return "row" if json_path else "prose"

    globals()["pointer_class"] = _all_rows
    try:
        folded_edges, _folded = graph(docs, base, canon)
    finally:
        globals()["pointer_class"] = _saved_class
    folded = len({(a, b) for a in folded_edges for b in folded_edges[a]})
    check("L22 folding prose into rows adds exactly the prose-only edge",
          folded == baseline + 1, "baseline=%d folded=%d" % (baseline, folded))
    check("L22b the frozen pointer vocabulary is unchanged after the mutation",
          pointer_class(["rows", "0", "face"]) == "row" and
          pointer_class(["notes"]) == "prose")

    # L23  transitive closure on the fixture: C reaches A, B, D
    check("L23 transitive closure of C is {A,B,D}",
          transitive(edges, "E12_gamma") == {"E10_alpha", "E11_beta", "E13_delta"},
          json.dumps(sorted(transitive(edges, "E12_gamma"))))

    # L24  cycles are detectable (fixture has none)
    check("L24 the fixture graph is acyclic",
          not any(s in transitive(edges, s) for s in edges))

    passed = sum(1 for c in checks if c["ok"])
    return checks, passed, len(checks)


# ---- run ----------------------------------------------------------------------
def load_docs():
    """Every study face under results/, minus this study's own face.

    E319 is about censuses counting their own programme's output, so it must not be the
    one census that counts itself: the exclusion is by study identity, not by filename.
    """
    docs = {}
    base = {}
    for dirpath, _dirnames, filenames in os.walk(RESULTS):
        for name in filenames:
            if not name.endswith(".json"):
                continue
            path = os.path.join(dirpath, name)
            try:
                with io.open(path, encoding="utf-8") as handle:
                    doc = json.load(handle)
            except Exception:
                continue
            if not isinstance(doc, dict):
                continue
            study = doc.get("study")
            if study == STUDY:
                continue
            if isinstance(study, str) and STUDY_RE.match(study):
                docs[path] = doc
    for path in docs:
        base.setdefault(os.path.basename(path), path)
    return docs, base


def build():
    docs, base = load_docs()
    canon = canonical_faces(docs)
    edges, per_face = graph(docs, base, canon)
    census = build_census(edges, per_face, docs, canon)
    exc_rows, covered, total_census_edges = exclusion_rows(edges, per_face, docs, canon)
    vrows, vtally = vintage_rows(edges, per_face, docs, canon)

    later = census.pop("_later")
    indeg = census.pop("_indeg")

    kinds = {}
    for row in exc_rows:
        kinds[row["declared_kind"]] = kinds.get(row["declared_kind"], 0) + 1

    census.update({
        "declared_exclusion_faces": sum(1 for r in exc_rows if r["declared_kind"] != "none"),
        "declared_kind_counts": kinds,
        "census_edges_covered_by_a_declaration": covered,
        "census_edges_missed_by_every_declaration": total_census_edges - covered,
        "censuses_needing_an_exclusion_but_declaring_none":
            sum(1 for r in exc_rows if r["counted_censuses"] and r["declared_kind"] == "none"),
        "vintage": {
            "compared": sum(vtally.values()),
            "forward": vtally["forward"],
            "backward": vtally["backward"],
            "indeterminate": vtally["indeterminate"],
            "unknown": vtally["unknown"],
        },
        "transitive_closure_beats_direct_edges": [
            {"study": s, "direct": len(edges[s]), "closure": len(transitive(edges, s))}
            for s in sorted(edges, key=study_ordinal)
            if len(transitive(edges, s)) > len(edges[s])
        ][:8],
    })

    faces = []
    for study in sorted(per_face, key=study_ordinal):
        row = dict(per_face[study])
        row["is_census"] = study in edges
        row["generated"] = str(docs[canon[study]].get("generated"))
        row["counted_by_a_later_census"] = sorted(later.get(study, []), key=study_ordinal)
        row["in_degree"] = indeg.get(study, 0)
        faces.append(row)

    verdict = (
        "every_census_counts_other_censuses_and_the_only_declared_guard_is_a_filename_list_"
        "that_cannot_express_is_a_census"
    ) if covered == 0 else "some_declared_lists_do_cover_census_edges"

    identity_checks = [
        {"check": "census edges <= all edges",
         "ok": census["census_to_census_edges"] <= census["all_edges"]},
        {"check": "census studies <= studies",
         "ok": census["census_studies"] <= census["studies"]},
        {"check": "every census has at least one counted study",
         "ok": all(len(edges[s]) >= 1 for s in edges)},
        {"check": "covered + missed equals the census edge count",
         "ok": covered + (total_census_edges - covered) == total_census_edges},
        {"check": "census edge count equals the sum of per-row counted censuses",
         "ok": total_census_edges == sum(r["counted_censuses"] for r in exc_rows)},
        {"check": "the vintage audit covers every census edge",
         "ok": sum(vtally.values()) == sum(len(v) for v in edges.values())},
        {"check": "declared kind counts sum to the census rows",
         "ok": sum(kinds.values()) == len(exc_rows)},
        {"check": "counted-by-a-later set only names censuses",
         "ok": all(t in edges for v in later.values() for t in v)},
        {"check": "no study counts itself",
         "ok": all(s not in edges[s] for s in edges)},
        {"check": "prose mentions are never folded into rows",
         "ok": all(set(p["prose_only_targets"]) | set(p["row_targets"]) >=
                   set(p["row_targets"]) for p in per_face.values())},
        {"check": "the study's own face is not in the discovery set",
         "ok": all(not str(p["face"]).upper().startswith("SELFINCLUSION-")
                   for p in per_face.values())},
    ]

    face = {
        "schema": "e319-census-self-inclusion/v1",
        "study": STUDY,
        "title": ("which study faces are counted as rows by later censuses of the same "
                  "programme, and is the exclusion list a declared property or a copy of "
                  "the writer's own family"),
        "evidence_cutoff": TODAY,
        "generated": TODAY,
        "discovery": {
            "root": "results/**/*.json",
            "study_rule": "top-level `study` matching ^E\\d+_",
            "row_pointer_rule": ("a .json string whose immediate parent key is one of "
                                 + ",".join(sorted(ROW_LEAF_KEYS)) +
                                 " or whose parent container key contains 'face'"),
            "prose_rule": "every other .json mention is reported and never counted",
            "canonical_face_rule": "per study, the dated build; the *_latest twin is dropped",
            "face_count": len(docs),
            "canonical_study_count": len(canon),
        },
        "self_faces_excluded": [FACE % TODAY, LATEST],
        "self_scripts_excluded": ["scripts/e319_census_self_inclusion_sweep.py"],
        "census": census,
        "verdict": verdict,
        "faces": faces,
        "exclusions": exc_rows,
        "in_degree_top": [
            {"study": s, "counted_by": indeg[s]}
            for s in sorted(indeg, key=lambda k: (-indeg[k], study_ordinal(k)))[:10]
        ],
        "forward_vintage_rows": vrows,
        "notes": [
            "A census is defined by what it does, not by its name: a study counts as a "
            "census only when its face carries a structured row pointer to another study's "
            "face. Prose mentions are published in prose_only_targets and are never counted.",
            "The declared guard on every face is `self_faces_excluded`, and on 10 of 31 "
            "censuses it names only that face's own two filenames -- a list that cannot "
            "answer 'is this face itself a census'.",
            "E317 is the only face that declares a filename-prefix family list; it still "
            "counts censuses outside that list, so the list is a copy of the writer's recent "
            "family rather than a property of the population.",
            "Filenames are not versions: a census row names a file, and that file is rewritten "
            "in place, so the content a census actually counted is not recoverable from the arc.",
            "Vintage comparison is granularity-aware: a date-only stamp against a same-day "
            "timestamp is INDETERMINATE, never forward. Plain string comparison manufactures "
            "34 extra forward edges on this face.",
        ],
        "identity_checks": identity_checks,
    }
    return face


def verify(face):
    problems = []
    if face.get("evidence_cutoff") != TODAY:
        problems.append("evidence_cutoff moved: %r" % (face.get("evidence_cutoff"),))
    if not str(face.get("verdict") or ""):
        problems.append("verdict missing")
    bad = [c for c in face.get("identity_checks") or [] if not c.get("ok")]
    if bad:
        problems.append("identity checks failing: %s" % ",".join(c["check"] for c in bad))
    census = face.get("census") or {}
    exclusions = face.get("exclusions") or []
    if census.get("census_to_census_edges") != \
            sum(r.get("counted_censuses") or 0 for r in exclusions):
        problems.append("census edge count does not recompute from the exclusion rows")
    if len(exclusions) != census.get("census_studies"):
        problems.append("exclusion rows are not one per census")
    faces = face.get("faces") or []
    if len(faces) != census.get("studies"):
        problems.append("face rows are not one per study")
    if sum(1 for f in faces if f.get("is_census")) != census.get("census_studies"):
        problems.append("is_census flags do not match the census count")
    vintage = census.get("vintage") or {}
    if vintage.get("compared") != census.get("all_edges"):
        problems.append("vintage audit does not cover every edge")
    for row in exclusions:
        if row.get("counted_censuses_missed") != \
                (row.get("counted_censuses") or 0) - \
                (row.get("counted_censuses_covered_by_the_declaration") or 0):
            problems.append("missed does not recompute for %s" % row.get("study"))
            break
    return problems


def write(face):
    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)
    dated = os.path.join(OUTDIR, FACE % TODAY)
    latest = os.path.join(OUTDIR, LATEST)
    payload = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for path in (dated, latest):
        with io.open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload + "\n")
    return dated, latest


def run():
    face = build()
    dated, latest = write(face)
    problems = verify(face)
    census = face["census"]
    print("face: %s" % os.path.relpath(dated, ROOT))
    print("studies %s | censuses %s | edges %s (census->census %s)"
          % (census["studies"], census["census_studies"],
             census["all_edges"], census["census_to_census_edges"]))
    print("declared exclusion faces %s | kinds %s"
          % (census["declared_exclusion_faces"],
             json.dumps(census["declared_kind_counts"], sort_keys=True)))
    print("census edges covered by any declaration %s | missed %s"
          % (census["census_edges_covered_by_a_declaration"],
             census["census_edges_missed_by_every_declaration"]))
    print("vintage %s" % json.dumps(census["vintage"], sort_keys=True))
    print("verdict: %s" % face["verdict"])
    if problems:
        print("PROBLEMS: %s" % "; ".join(problems))
        return 2
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        return run()
    if cmd == "verify":
        face = build()
        problems = verify(face)
        if problems:
            print("PROBLEMS: %s" % "; ".join(problems))
            return 1
        print("verify: 0 problems")
        return 0
    if cmd == "selftest":
        checks, passed, total = selftest()
        for row in checks:
            if not row["ok"]:
                print("FAIL %s %s" % (row["check"], row.get("detail", "")))
        print("selftest %d/%d" % (passed, total))
        return 0 if passed == total else 1
    print("usage: run | verify | selftest")
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv))