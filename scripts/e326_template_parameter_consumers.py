"""E326 -- which consumers quote a number from a face whose parameter they never carry.

E325 closed at the face level: no face in the 196-gate population is an orphan once every way of
naming a file is allowed.  But 30 of its 51 faces are reached only through a format template
(``BANDDEFLATE-%s.json`` % CUTOFF) or a composed path -- and a template has a *free parameter*.
That is a different question from "is there a writer": a face written for cutoff X answers a
different question than the same template at cutoff Y, so a consumer of such a face is only
honest if either (a) it supplies the parameter itself, or (b) it reads the parameter back out of
the face, or (c) the face republishes the parameter beside the number it publishes.

The measurement is the consumer census the pool card asks for, and it keeps three readings
apart, because collapsing them is the defect being studied:

  P1 LITERAL    the consumer's own line carries the parameter token (a pinned date)
  P2 CONSTANT   the consumer formats the template with a name it defines (``% CUTOFF``)
  P3 READ_BACK  the consumer takes the parameter out of the face (``face["evidence_cutoff"]``)
  P4 UNPINNED   the consumer names the face and quotes from it with no parameter in sight

P4 on a face that does not republish its parameter is the published number whose provenance is
not republished beside it: re-deriving the face at another parameter would silently change what
that number answers.  Everything is static tree analysis -- no panel, no engine, no network.

Usage:
    python scripts/e326_template_parameter_consumers.py run|verify|selftest
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import e312_gate_operand_identity as e312  # noqa: E402  (path set above)
import e325_orphan_gate_faces as e325  # noqa: E402

ROOT = e312.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
INPUT = "results/state_tilt/ORPHANGATEFACE-2026-10-31.json"
TODAY = "2026-10-31"
FACE = "TEMPLATEPARAM-%s.json" % TODAY
LATEST = "templateparam_latest.json"
STUDY = "E326_template_parameter_consumers"

DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
COMPACT = re.compile(r"\d{8}")
# a key that would republish the parameter beside the number
PARAM_KEY = re.compile(r"(cutoff|as_?of|date|class|cls|era|window|tag)", re.I)
# a name a source defines to supply the parameter itself
PARAM_NAME = re.compile(r"(CUTOFF|CUT_OFF|TODAY|AS_OF|ASOF|LAST_DATE|SESSION|DATE|CLS|CLASS|ERA)\b")

C_PRODUCER = "this_source_is_the_face_s_own_writer"
C_LITERAL = "consumer_pins_the_parameter_literally"
C_CONSTANT = "consumer_formats_the_template_with_a_parameter_it_defines"
C_READ_BACK = "consumer_reads_the_parameter_back_out_of_the_face"
C_UNPINNED = "consumer_names_the_face_with_no_parameter_in_sight"
C_MENTION = "the_mention_is_a_comment_or_docstring_not_a_dependency"
CLASSES = (C_PRODUCER, C_LITERAL, C_CONSTANT, C_READ_BACK, C_UNPINNED, C_MENTION)
# a consumer is judged by its weakest line, never its strongest
CLASS_RANK = {C_LITERAL: 1, C_CONSTANT: 2, C_READ_BACK: 3, C_UNPINNED: 4}

VERDICT_ALL = "every_consumer_of_a_parameterised_face_supplies_the_parameter_in_its_own_source"
VERDICT_CARRIED = ("every_consumer_that_names_a_face_without_its_parameter_quotes_a_face_that_"
                   "republishes_it_beside_the_numbers")
VERDICT_SILENT = ("some_published_numbers_ride_a_template_face_whose_parameter_neither_the_"
                  "consumer_nor_the_face_republishes")
VERDICT_NONE = "no_parameterised_face_in_the_population_has_a_consumer_outside_its_writer"


def relp(path):
    return path.replace("\\", "/") if not os.path.isabs(path) else e312.rel(path)


_SRC = None


def corpus():
    """E325's corpus minus this scanner (a scanner that reads its own output lies to itself)."""
    global _SRC
    if _SRC is None:
        own = os.path.abspath(__file__)
        _SRC = [(p, s) for p, s in e325.corpus() if os.path.abspath(p) != own]
    return _SRC


def _norm(path):
    return (path or "").replace("\\", "/").strip()


def same_source(a, b):
    """Fixture sources live outside the repo, so equality must survive a path prefix."""
    a, b = _norm(a), _norm(b)
    if not a or not b:
        return False
    return a == b or a.endswith("/" + b) or b.endswith("/" + a)


def read_json(rel_path, root=None):
    with io.open(os.path.join(root or ROOT, rel_path), encoding="utf-8") as fh:
        return json.load(fh)


# ------------------------------------------------------------------------ population / params

def population(doc=None):
    """E325's own faces, filtered to the two classes that carry a free parameter."""
    doc = doc if doc is not None else read_json(INPUT)
    out = []
    for rec in doc.get("faces") or []:
        final = rec["class_by_rung"][e325.RUNG_COMPOSED]
        if final in (e325.CLS_FAMILY, e325.CLS_COMPOSED):
            out.append(rec)
    return sorted(out, key=lambda r: r["face"])


def parameter_of(face, face_class=None, evidence=None):
    """The token(s) a template substitutes to name this face -- none for a static path.

    A composed path is a name the source spells in full, so it has no free parameter and cannot
    be quoted "without its parameter".  A family face takes its token from the writer's own
    template where one is published (that is the definition of the parameter, not a guess).
    """
    if face_class == e325.CLS_COMPOSED:
        return {"kind": "none", "token": None, "tokens": [], "derived_from": "composed_path"}
    base = os.path.basename(face)
    match = DATE.search(base)
    if match:
        token = match.group(0)
        return {"kind": "date", "token": token,
                "tokens": [token, token.replace("-", "")], "derived_from": "file_name"}
    match = COMPACT.search(base)
    if match:
        return {"kind": "compact_date", "token": match.group(0),
                "tokens": [match.group(0)], "derived_from": "file_name"}
    stem = base[:-5] if base.endswith(".json") else base
    for rec in evidence or []:
        ev = rec.get("evidence") or {}
        needle = ev.get("needle") or ""
        if ev.get("shape") != "format_template" or not needle:
            continue
        # the needle is the family prefix as the writer spells it ("p1e_nulls_" / "BANDDEFLATE-")
        prefix = needle.split("%s")[0].split("{")[0]
        prefix = prefix.rstrip("-_") + ("-" if needle.rstrip().endswith("-") else "_")
        if not stem.startswith(prefix) or len(stem) <= len(prefix):
            continue
        token = stem[len(prefix):]
        return {"kind": "class_token", "token": token, "tokens": [token],
                "derived_from": "writer_template"}
    return {"kind": "none", "token": None, "tokens": [], "derived_from": "no_template"}


def _walk_keys(node, prefix=""):
    if isinstance(node, dict):
        for k, v in node.items():
            path = ("%s.%s" % (prefix, k)) if prefix else str(k)
            yield path, k, v
            for item in _walk_keys(v, path):
                yield item
    elif isinstance(node, list):
        for i, v in enumerate(node[:3]):
            path = "%s[%d]" % (prefix, i)
            yield path, "", v
            for item in _walk_keys(v, path):
                yield item


def republished_in_face(face_rel, param):
    """Which keys of the face restate the parameter beside the numbers it publishes."""
    if not param["tokens"]:
        return []
    try:
        doc = read_json(face_rel)
    except Exception:
        return []
    out = []
    for path, key, value in _walk_keys(doc):
        if not key or not PARAM_KEY.search(str(key)):
            continue
        text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
        if any(tok and tok in text for tok in param["tokens"]):
            out.append(path)
        if len(out) >= 24:
            break
    return out


def pointer_siblings(face_rel):
    """The `*latest*.json` pointers in the same directory that name this exact face.

    A pointer makes the parameter invisible one step earlier: a reader that opens the pointer
    never sees the date in a file name.  This is measured (not followed) so the next study has
    a population instead of an assumption.
    """
    directory = os.path.dirname(os.path.join(ROOT, face_rel))
    base = os.path.basename(face_rel)
    out = []
    if not os.path.isdir(directory):
        return out
    for name in sorted(os.listdir(directory)):
        low = name.lower()
        if not low.endswith(".json") or "latest" not in low:
            continue
        full = os.path.join(directory, name)
        try:
            if os.path.getsize(full) > 4 * 1024 * 1024:
                continue
            with io.open(full, encoding="utf-8") as fh:
                text = fh.read()
        except Exception:
            continue
        if base in text:
            out.append(relp(full))
    return out


# --------------------------------------------------------------------------------- consumers

def code_lines(src):
    """Lines that are code: comments dropped, triple-quoted blocks dropped (method disclosed)."""
    out = []
    in_doc = False
    for lineno, line in enumerate((src or "").splitlines(), 1):
        stripped = line.strip()
        triples = stripped.count('"""') + stripped.count("'''")
        if in_doc:
            if triples % 2 == 1:
                in_doc = False
            continue
        if triples % 2 == 1 and (stripped.startswith('"""') or stripped.startswith("'''")):
            in_doc = True
            continue
        if not stripped or stripped.startswith("#"):
            continue
        out.append((lineno, stripped))
    return out


def reference_forms(face):
    """How a reader could name this face: the exact name and the family prefix it varies.

    A prefix alone is not a reference (``REPRO-`` appears inside gate labels such as
    ``G-REPRO-v1``), so a prefix only counts when it is followed by a format marker or a glob.
    """
    base = os.path.basename(face)
    stem = base[:-5] if base.endswith(".json") else base
    prefix = None
    match = DATE.search(stem)
    if match:
        prefix = stem[:match.start()]
    elif COMPACT.search(stem):
        prefix = stem[:COMPACT.search(stem).start()]
    else:
        for form in e325.family_templates(face):
            if form.endswith("_") and stem.startswith(form) and len(stem) > len(form):
                prefix = form
                break
    return {"name": base, "prefix": prefix}


def match_reference(text, forms):
    """(shape, needle) when this line names the face, else None."""
    if forms["name"] in text:
        return "name", forms["name"]
    prefix = forms["prefix"]
    if not prefix:
        return None
    for marker in ("%s", "{"):
        if prefix + marker in text:
            return "template", prefix + marker
    if prefix + "*" in text:
        return "glob", prefix + "*"
    return None


def classify_line(line, shape, needle, param):
    """Which of P1..P4 this line is -- one line of evidence per consumer."""
    toks = [t for t in param["tokens"] if t]
    if toks and any(tok in line for tok in toks):
        return C_LITERAL, "the parameter is written out on the line"
    if re.search(r"(?:\bget\(\s*[\"']|\[\s*[\"'])\s*[^\"']*(?:cutoff|as_?of|date|class|cls)",
                 line, re.I):
        return C_READ_BACK, "the consumer takes the parameter out of the face"
    if shape == "name":
        return C_LITERAL, "the consumer spells the face's own name"
    if shape == "template":
        return C_CONSTANT, "the consumer fills the template from a name it supplies"
    return C_UNPINNED, "the consumer resolves the family without naming the parameter"


def consumers_of(face_rec, param, files=None):
    face = face_rec["face"]
    producers = {e["producer"] for e in face_rec.get("evidence") or [] if e.get("producer")}
    forms = reference_forms(face)
    out = []
    for path, src in (files if files is not None else corpus()):
        rel = relp(path)
        mentioned = []
        for lineno, text in code_lines(src):
            hit = match_reference(text, forms)
            if hit:
                mentioned.append((lineno, hit[0], hit[1], text))
        if not mentioned:
            continue
        if any(same_source(rel, producer) for producer in producers):
            lineno, text = mentioned[0][0], mentioned[0][3]
            out.append({"source": rel, "line": lineno, "text": text[:160],
                        "class": C_PRODUCER, "why": "it writes this face"})
            continue
        lineno, shape, needle, text = mentioned[0]
        # a consumer is only honest if EVERY line that names the face is honest: a file that
        # pins the date in one place and globs the family in another is an unpinned consumer.
        ranked = [(CLASS_RANK[cls], cls, why, line, txt, shp)
                  for line, shp, ndl, txt in mentioned
                  for cls, why in [classify_line(txt, shp, ndl, param)]]
        worst = max(ranked, key=lambda r: r[0])
        out.append({"source": rel, "line": worst[3], "text": worst[4][:160],
                    "shape": worst[5], "class": worst[1], "needle": needle,
                    "why": worst[2], "lines_naming_the_face": len(mentioned)})
    return out


def face_record(face_rec, files=None):
    face = face_rec["face"]
    face_class = face_rec["class_by_rung"][e325.RUNG_COMPOSED]
    param = parameter_of(face, face_class, face_rec.get("evidence"))
    republished = republished_in_face(face, param)
    consumers = consumers_of(face_rec, param, files) if param["kind"] != "none" else []
    counts = {}
    for c in consumers:
        counts[c["class"]] = counts.get(c["class"], 0) + 1
    unpinned = [c for c in consumers if c["class"] == C_UNPINNED]
    return {
        "face": face,
        "face_class": face_rec["class_by_rung"][e325.RUNG_COMPOSED],
        "rows": face_rec.get("rows"),
        "on_disk": face_rec.get("on_disk"),
        "producers": sorted({e["producer"] for e in face_rec.get("evidence") or []
                             if e.get("producer")}),
        "template_forms": reference_forms(face),
        "parameter": param,
        "parameter_republished_in_the_face": republished,
        "parameter_is_carried_by_the_face": bool(republished),
        "pointer_siblings": pointer_siblings(face) if param["kind"] != "none" else [],
        "consumers": consumers,
        "consumer_classes": counts,
        "quoted_without_its_parameter": (
            len(unpinned) > 0 and param["kind"] != "none" and not republished),
        "unpinned_consumers": len(unpinned),
    }


# -------------------------------------------------------------------------------------- build

def build(outdir=None):
    doc = read_json(INPUT)
    pop = population(doc)
    files = corpus()
    faces = [face_record(r, files) for r in pop]
    all_consumers = [c for f in faces for c in f["consumers"]]
    by_class = {}
    for c in all_consumers:
        by_class[c["class"]] = by_class.get(c["class"], 0) + 1
    silent = [f for f in faces if f["quoted_without_its_parameter"]]
    named = []
    for f in silent:
        for c in f["consumers"]:
            if c["class"] != C_UNPINNED:
                continue
            named.append({"face": f["face"], "parameter_kind": f["parameter"]["kind"],
                          "parameter_token": f["parameter"]["token"],
                          "consumer": c["source"], "line": c["line"], "text": c["text"]})
    parameterised = [f for f in faces if f["parameter"]["kind"] != "none"]
    consumed = [f for f in parameterised if any(c["class"] != C_PRODUCER for c in f["consumers"])]
    unpinned = [c for c in all_consumers if c["class"] == C_UNPINNED]
    no_param_faces = [f["face"] for f in parameterised
                      if not f["parameter_is_carried_by_the_face"]]
    unpinned_on_carried = 0
    for f in parameterised:
        if f["parameter_is_carried_by_the_face"]:
            unpinned_on_carried += len([c for c in f["consumers"] if c["class"] == C_UNPINNED])

    if not parameterised or not consumed:
        verdict = VERDICT_NONE
        reason = ("the population carries %d parameterised faces and %d of them are named "
                  "outside their own writer" % (len(parameterised), len(consumed)))
    elif silent:
        verdict = VERDICT_SILENT
        reason = ("%d of %d parameterised faces are named by a consumer with no parameter in "
                  "sight AND do not republish it -- %d numbers answer a question they cannot "
                  "state" % (len(silent), len(parameterised), len(named)))
    elif unpinned:
        verdict = VERDICT_CARRIED
        reason = ("%d consumers name a face with no parameter in sight, but all %d of them "
                  "quote faces that republish the parameter beside their numbers (%d of %d "
                  "parameterised faces carry it; %d do not and are named only by writers)"
                  % (len(unpinned), len(unpinned), len(parameterised) - len(no_param_faces),
                     len(parameterised), len(no_param_faces)))
    else:
        verdict = VERDICT_ALL
        reason = ("all %d consumers outside the writers of %d parameterised faces pin the "
                  "parameter in their own source or supply it from a constant they define"
                  % (len([c for c in all_consumers if c["class"] != C_PRODUCER]),
                     len(parameterised)))
    out = {
        "study": STUDY,
        "title": ("the consumers of a template face, and which published numbers are quoted "
                  "with the parameter that made them invisible"),
        "evidence_cutoff": TODAY,
        "upstream": os.path.basename(INPUT),
        "upstream_study": e325.STUDY,
        "corpus": {"files": len(files), "self_excluded": os.path.basename(__file__)},
        "rules": {
            "population": "E325 faces whose final class is a format template or a composed path",
            "parameter": ("the token a template substitutes: an ISO date, a compact stamp, or "
                          "the class suffix an underscore family varies"),
            "republished": ("a key whose name carries cutoff/asof/date/class/era/window/tag and "
                            "whose value contains the parameter token"),
            C_LITERAL: "the parameter token appears on the consumer's own line",
            C_CONSTANT: "the consumer fills the template from a name it defines",
            C_READ_BACK: "the consumer subscripts/gets a parameter-like key",
            C_UNPINNED: "the face is named and no parameter appears on the line",
            C_MENTION: "comments and docstrings are stripped before any of the above",
        },
        "held_fixed": ("every upstream face class, row and producer list is read and never "
                       "rewritten; only the consumer side is measured here"),
        "limits": ("a consumer is judged by its weakest naming line, but only direct references to the "
                   "family are seen: a reader that reaches the face through a *_latest pointer is "
                   "counted as a pointer (summary.faces_reachable_through_a_latest_pointer) and "
                   "its own source is not traversed this round; the scan is static, so a face "
                   "loaded through a computed name outside the family prefix is not seen"),
        "no_bill": "published faces, in-repo sources only; no draws, no panel, no engine, no network",
        "faces": faces,
        "summary": {
            "faces_in_population": len(faces),
            "faces_with_a_parameter": len(parameterised),
            "faces_with_a_static_path": len(faces) - len(parameterised),
            "faces_named_outside_their_writer": len(consumed),
            "faces_whose_parameter_the_face_republishes":
                len([f for f in parameterised if f["parameter_is_carried_by_the_face"]]),
            "consumers": len(all_consumers),
            "consumers_by_class": {k: by_class.get(k, 0) for k in CLASSES},
            "faces_quoted_without_their_parameter": len(silent),
            "numbers_quoted_without_their_parameter": len(named),
            "faces_that_do_not_republish_their_parameter": no_param_faces,
            "unpinned_consumers_on_faces_that_republish_the_parameter": unpinned_on_carried,
            "faces_reachable_through_a_latest_pointer": len(
                [f for f in parameterised if f["pointer_siblings"]]),
            "latest_pointers_naming_a_parameterised_face": sum(
                len(f["pointer_siblings"]) for f in parameterised),
            "unpinned_share_of_non_writer_consumers": round(
                100.0 * by_class.get(C_UNPINNED, 0)
                / max(1, len([c for c in all_consumers if c["class"] != C_PRODUCER])), 2),
        },
        "numbers_quoted_without_their_parameter": named,
        "faces_quoted_without_their_parameter": [f["face"] for f in silent],
        "verdict": verdict,
        "verdict_reason": reason,
    }
    if outdir:
        if not os.path.isdir(outdir):
            os.makedirs(outdir, exist_ok=True)
        path = os.path.join(outdir, FACE)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        latest = os.path.join(outdir, LATEST)
        with io.open(latest, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    return out


# ----------------------------------------------------------------------------------- commands

def cmd_run():
    out = build(OUTDIR)
    s = out["summary"]
    print("E326 consumers of %d template/composed faces (corpus %d sources)"
          % (s["faces_in_population"], out["corpus"]["files"]))
    print("  parameterised %d  static %d  named outside their writer %d"
          % (s["faces_with_a_parameter"], s["faces_with_a_static_path"],
             s["faces_named_outside_their_writer"]))
    print("  consumers by class:", json.dumps(s["consumers_by_class"], ensure_ascii=False))
    print("  faces whose parameter the face republishes: %d"
          % s["faces_whose_parameter_the_face_republishes"])
    print("  numbers quoted without their parameter: %d on %d faces"
          % (s["numbers_quoted_without_their_parameter"],
             s["faces_quoted_without_their_parameter"]))
    for row in out["numbers_quoted_without_their_parameter"][:12]:
        print("   - %-46s %s:%s  %s" % (os.path.basename(row["face"]), row["consumer"],
                                        row["line"], row["text"][:70]))
    print("verdict:", out["verdict"])
    print("reason:", out["verdict_reason"])
    return 0


def cmd_verify():
    path = os.path.join(OUTDIR, FACE)
    if not os.path.exists(path):
        print("verify: face missing:", FACE)
        return 2
    on_disk = read_json(os.path.join("results", "state_tilt", FACE))
    fresh = build(None)
    problems = []
    for key in ("verdict", "verdict_reason"):
        if on_disk.get(key) != fresh.get(key):
            problems.append("%s on disk %r != %r" % (key, on_disk.get(key), fresh.get(key)))
    for key, value in fresh["summary"].items():
        got = (on_disk.get("summary") or {}).get(key)
        if got != value:
            problems.append("summary.%s %r != %r" % (key, got, value))
    a = {f["face"]: f["consumer_classes"] for f in on_disk.get("faces") or []}
    b = {f["face"]: f["consumer_classes"] for f in fresh["faces"]}
    if a != b:
        moved = [k for k in b if a.get(k) != b[k]]
        problems.append("per-face consumer classes drifted on %d face(s): %s"
                        % (len(moved), moved[:4]))
    if problems:
        print("verify: %d problem(s)" % len(problems))
        for p in problems:
            print("  -", p)
        return 1
    print("verify: problems=[] (%d faces, %d consumers)"
          % (fresh["summary"]["faces_in_population"], fresh["summary"]["consumers"]))
    return 0


def cmd_selftest():
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))
        print("  %-64s %s%s" % (name, "PASS" if ok else "FAIL",
                                ("  " + detail) if (detail and not ok) else ""))

    # L1 the parameter of a dated family face is the date, and its compact twin
    p = parameter_of("results/state_tilt/BANDDEFLATE-2026-10-29.json", e325.CLS_FAMILY)
    check("L1 a dated face's parameter is the date (and its compact form)",
          p["kind"] == "date" and p["token"] == "2026-10-29" and "20261029" in p["tokens"],
          str(p))

    # L1b a class-suffix family face takes its token from the writer's own template
    p2 = parameter_of("results/shortline/p1e_nulls_M_arc.json", e325.CLS_FAMILY,
                      [{"evidence": {"shape": "format_template",
                                     "needle": "p1e_nulls_", "line": 1}}])
    check("L1b an underscore family face's parameter is its class suffix",
          p2["kind"] == "class_token" and p2["token"] == "M_arc"
          and p2["derived_from"] == "writer_template", str(p2))

    # L1c a composed path is static -- it must not be counted as parameterised
    p3 = parameter_of("results/shortline/p1e_synth.json", e325.CLS_COMPOSED)
    check("L1c a composed path carries no parameter",
          p3["kind"] == "none" and not p3["tokens"], str(p3))

    # L2 comments and docstrings are not dependencies
    src = ('"""results/BANDDEFLATE-2026-10-29.json is a face\n'
           'not code here"""\n'
           '# results/BANDDEFLATE-2026-10-29.json in a comment\n'
           'x = load("results/BANDDEFLATE-2026-10-29.json")\n')
    lines = code_lines(src)
    check("L2 docstrings and comments are stripped before the mention search",
          len(lines) == 1 and "load(" in lines[0][1], str(lines))

    # L3 each of P1..P4 is reached by its own shape
    param = parameter_of("results/state_tilt/BANDDEFLATE-2026-10-29.json", e325.CLS_FAMILY)
    c1, _ = classify_line('load("BANDDEFLATE-2026-10-29.json")', "name",
                          "BANDDEFLATE-2026-10-29.json", param)
    c2, _ = classify_line('SRC = "BANDDEFLATE-%s.json" % CUTOFF', "template",
                          "BANDDEFLATE-%s", param)
    c3, _ = classify_line('f["evidence_cutoff"]', "name", "BANDDEFLATE-2026-10-29.json", param)
    c4, _ = classify_line('D = newest(glob("BANDDEFLATE-*.json"))', "glob",
                          "BANDDEFLATE-*", param)
    check("L3 the four consumer classes are separable",
          (c1, c2, c3, c4) == (C_LITERAL, C_CONSTANT, C_READ_BACK, C_UNPINNED),
          str((c1, c2, c3, c4)))

    # L3b a family prefix inside an unrelated label is not a reference
    forms = reference_forms("results/state_tilt/REPRO-2026-10-29.json")
    check("L3b a bare family prefix in a gate label is not a reference",
          match_reference('_log(f"G-REPRO-v1 {ok}")', forms) is None
          and forms["prefix"] == "REPRO-", str(forms))

    # L4 a number quoted without its parameter is only a finding when the face lacks it too
    fake = {"face": "results/state_tilt/FAKE-2026-10-29.json",
            "class_by_rung": {e325.RUNG_COMPOSED: e325.CLS_FAMILY},
            "rows": 1, "on_disk": True, "evidence": [{"producer": "scripts/w.py"}]}
    rec = face_record(fake, [("C:/fake/scripts/r.py",
                              'D = newest(glob("FAKE-*.json"))\nload(D)\n')])
    check("L4 an unpinned consumer of a face with no republished parameter is a finding",
          rec["quoted_without_its_parameter"] and rec["unpinned_consumers"] == 1,
          str(rec["consumer_classes"]))

    # L5 the same consumer on a face that republishes the parameter is not a finding
    saved = globals()["republished_in_face"]
    globals()["republished_in_face"] = lambda face, param: ["evidence_cutoff"]
    try:
        carried = face_record(fake, [("C:/fake/scripts/r.py",
                                      'D = newest(glob("FAKE-*.json"))\nload(D)\n')])
    finally:
        globals()["republished_in_face"] = saved
    check("L5 a face that republishes its parameter makes the same consumer honest",
          carried["parameter_is_carried_by_the_face"]
          and not carried["quoted_without_its_parameter"], str(carried["consumer_classes"]))

    # L6 a composed path is static: no consumer list, no silent-parameter finding
    static = {"face": "results/shortline/p1e_synth.json",
              "class_by_rung": {e325.RUNG_COMPOSED: e325.CLS_COMPOSED},
              "rows": 1, "on_disk": True, "evidence": [{"producer": "scripts/p1e_synth.py"}]}
    rec_static = face_record(static, [("C:/fake/scripts/r.py",
                                       'D = "p1e_synth.json"\nload(D)\n')])
    check("L6 a composed path is not parameterised and cannot be an unpinned finding",
          rec_static["parameter"]["kind"] == "none" and not rec_static["consumers"]
          and not rec_static["quoted_without_its_parameter"], str(rec_static["consumers"]))

    # L6b a consumer that spells the full dated name pins the parameter in its own source
    rec_lit = face_record(fake, [("C:/fake/scripts/r.py",
                                  'load("FAKE-2026-10-29.json")\n')])
    check("L6b spelling the full dated name is a literal pin, not a finding",
          rec_lit["consumer_classes"].get(C_LITERAL) == 1
          and not rec_lit["quoted_without_its_parameter"], str(rec_lit["consumer_classes"]))

    # L7 the population is E325's own template/composed faces -- no invented, none dropped
    pop = population()
    e325_doc = read_json(INPUT)
    expect = [r["face"] for r in e325_doc["faces"]
              if r["class_by_rung"][e325.RUNG_COMPOSED]
              in (e325.CLS_FAMILY, e325.CLS_COMPOSED)]
    check("L7 the population is exactly E325's template and composed faces",
          [r["face"] for r in pop] == sorted(expect), str(len(pop)))

    # L8 the build is deterministic (two runs agree, so verify can police it)
    a = build(None)
    b = build(None)
    check("L8 two builds agree byte-for-byte on the summaries",
          a["summary"] == b["summary"] and a["verdict"] == b["verdict"])

    # L9 the verdict is one of the frozen three and its reason states the count
    check("L9 the verdict is inside the frozen set",
          a["verdict"] in (VERDICT_ALL, VERDICT_CARRIED, VERDICT_SILENT, VERDICT_NONE),
          a["verdict"])

    # L9b an unpinned consumer is never reported as "everyone supplies the parameter"
    if a["summary"]["consumers_by_class"].get(C_UNPINNED):
        check("L9b a face quoted with no parameter in sight is not called fully pinned",
              a["verdict"] != VERDICT_ALL, a["verdict"])
    else:
        check("L9b (no unpinned consumer exists to police the wording)", True)

    # L10 this scanner is excluded from its own corpus
    own = os.path.abspath(__file__)
    check("L10 this scanner is excluded from its own corpus",
          all(os.path.abspath(p) != own for p, _s in corpus()))

    # L11 a writer is classified as a writer, not as an unpinned consumer
    rec_w = face_record(fake, [("C:/fake/scripts/w.py",
                                'D = newest(glob("FAKE-*.json"))\nwrite(D)\n')])
    check("L11 the face's own writer is not counted as an unpinned consumer",
          rec_w["consumer_classes"].get(C_PRODUCER) == 1
          and not rec_w["quoted_without_its_parameter"], str(rec_w["consumer_classes"]))

    passed = sum(1 for _n, ok, _d in checks if ok)
    print("selftest: %d/%d" % (passed, len(checks)))
    return 0 if passed == len(checks) else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd in ("run", "build"):
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))